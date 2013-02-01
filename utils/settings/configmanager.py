"""
The Settings class provides a simple JSON-based settings object that is
meant to bring the LoadConfiguration settings experience to python.

Settings objects allow for loading from multiple settings files with
overwriting of values (like client.dat and user.dat). Settings objects
store values liek dicts, but behave like a Matlab structs, with keys
accessed as attributes (e.g. settings.foo.bar.baz).
"""
import re
import sys

class FP(object):
    def __init__(self, function, args=[], kv_args={}):
        self.function = function
        self.args = args
        self.kv_args = kv_args

    def execute(self, args=[], kv_args={}):
        if args or kv_args:
            return self.function( *args, **kv_args )
        elif self.args or self.kv_args:
            return self.function( *self.args, **self.kv_args )
        else:
            return self.function

    def __str__(self):
        module = getattr(self.function, '__module__', None)
        function = self.function.__name__

        args = [ to_string(i) for i in self.args ]
        args += [ '{0}={1}'.format(k, to_string(v)) for k,v in zip(self.kv_args.keys(), self.kv_args.values()) ]

        return '<{0}> {1} ({2})'.format(module, function, ', '.join(args))


def to_string(obj):
    '''
    Convert an object in to a string.
    '''
    if isinstance(obj, int) or isinstance(obj, float):
        return str(obj)

    if isinstance(obj, str):
        return '\'' + obj + '\''

    if isinstance(obj, bool):
        return 'True' if obj else 'False'

    if isinstance(obj, list):
        new_list = [ to_string(i) for i in obj ]
        return '[ {0} ]'.format(', '.join(new_list))

    if isinstance(obj, tuple):
        new_list = [ to_string(i) for i in obj ]
        return '( {0} )'.format(', '.join(new_list))

    if isinstance(obj, FP):
        return obj.__str__

    if isinstance(obj, dict):
        return obj
    raise Exception('need an error message.')


def from_string(string):
    '''
    Convert the data in a string to its given type.
    '''
    # Start with the primitive types.
    integer_regex = re.compile(r'''^[-0-9]*$''', re.IGNORECASE)
    float_regex = re.compile(r'''^[-0-9]*\.[0-9]*$''', re.IGNORECASE)
    single_quote_string = re.compile(r'^\'((?:.*))\'$', re.IGNORECASE)
    double_quote_string = re.compile(r'^\"((?:.*))\"$', re.IGNORECASE)
    booleans = { 'on':True, 'off':False, 
                 'True':True, 'False':False,
                 'true':True, 'false':False }
    is_integer = integer_regex.match(string)
    is_float = float_regex.match(string)
    is_single_quote = single_quote_string.match(string)
    is_double_quote = double_quote_string.match(string)

    if is_integer:
        return int(string)

    if is_float:
        return float(string)

    if is_single_quote:
        return is_single_quote.groups()[0]

    if is_double_quote:
        return is_double_quote.groups()[0]

    if string in booleans:
        return booleans[string]

    # Complex types
    list_regex = re.compile(r'''^\[((?:.*))\]$''', re.IGNORECASE)
    tuple_regex = re.compile(r'''^\(((?:.*))\)$''', re.IGNORECASE)

    is_list = list_regex.match(string)
    is_tuple = tuple_regex.match(string)

    if is_list:
        if is_list.groups()[0] != '':
            the_list = is_list.groups()[0].split(',')
            return [ from_string(i.strip()) for i in the_list ]
        else:
            return []

    if is_tuple:
        if is_tuple.groups()[0] != '':
            the_list = is_tuple.groups()[0].split(',')
            return tuple([ from_string(i.strip()) for i in the_list ])
        else:
            return ()
    
    # Objects
    # <module> function (args)
    function_regex = re.compile(r'''^<((?:[a-z0-9.]*))>\s*
                                     ((?:[a-z0-9_.]*))\s*
                                     \({0,1}
                                     ((?:[a-z0-9,= ]*))
                                     \){0,1}$''', re.IGNORECASE | re.VERBOSE)
    is_function = function_regex.match(string)
    if is_function:

        function_info = is_function.groups()
        module = function_info[0]
        function_name = function_info[1]
        args = function_info[2]

        __import__(module)
        mod = sys.modules[module]
        function = getattr(mod, function_name)

        if args:
            args = args.split(',')
            kvp_regex = re.compile('^[a-z][a-z0-9_]*\s*=[a-z0-9]*$', re.IGNORECASE)
            key_value_pairs = [ arg.strip() for arg in args if kvp_regex.match(arg.strip()) ]
            single = [ arg.strip() for arg in args if not kvp_regex.match(arg.strip()) ]
            single = [ from_string(i) for i in single ]
            key_value_pairs = [ arg.split('=') for arg in key_value_pairs ]
            key_value_pairs = [ (i[0], from_string(i[1])) for i in key_value_pairs ]
            key_value_pairs = dict(key_value_pairs)

            return FP(function, single, key_value_pairs)
        else:
            return FP(function)


class Section(dict):
    def __init__(self):
        self.scalars = []
        self.sections = []
        self.comments = {}
        self.inline_comments = {}

    def __setitem__(self, key, value):
        '''Add an item to the Section object.'''
        if isinstance(value, Section) or isinstance(value, dict):
            self.sections.append(key)
        else:
            self.scalars.append(key)
        dict.__setitem__(self, key, to_string(value))

    def __getitem__(self, key):
        '''Return an item with the given key from the Section object.'''
        value = dict.__getitem__(self, key)
        if isinstance(value, dict) or isinstance(value, Section):
            return value
        return from_string(value)

    def __delitem__(self, key):
        '''Remove an item '''
        dict.__delitem__(self, key)

    def __contains__(self, key):
        """
        key in s[key]

        test whether a child is in the Settings object

        key: the name of the (potential) child
        """
        return key in self.sections or key in self.scalars

class ConfigManager(dict):
    _section_marker = re.compile(r'''^
                                    \s*
                                    ((?:\[+\s*))
                                    ((?:[a-z0-9:_\.\s,]*))
                                    \s*
                                    ((?:\]+))\s*
                                    (\#.*)?
                                    $''',
                                    re.VERBOSE | re.IGNORECASE)
    _key_value_pair = re.compile(r'''^
                                    \s*
                                    ((?:[a-z][a-z0-9_]*))
                                    \s*
                                    =
                                    \s*
                                    ((?:[a-z0-9_\\/:]*))
                                    \s*
                                    (\#.*)?
                                    $''', re.VERBOSE | re.IGNORECASE)

    _comments = re.compile(r'''^
                                ((?:\s*\#.*))
                                $''', re.VERBOSE | re.IGNORECASE )
    def __init__(self, config_file=None):
        self.settings = Section()
        self.file_name = config_file
        if self.file_name: self.read()

    def __contains__(self, key):
        return key in self.settings

    def __setitem__(self, key, value):
        self.settings[key] = value

    def __getitem__(self, key):
        return self.settings[key]

    def read(self, file_name=None):
        '''
        Read in a settings file.
        '''
        self.file_name = file_name if file_name else self.file_name
        if not self.file_name: raise ValueError('No file name given.')
        print 'Reading file:', self.file_name 
        current_section = self.settings#()
        previous_section = Section()
        current_level = 1
        comments = []

        with open(self.file_name, 'r') as f:
            for line in f.readlines():
                # Loop through the setting file line by line.
                # a line can be one of 3 things
                # A section ie [Section]
                # A key value pair ie a = 1
                # a comment ie # bla
                is_section = self._section_marker.match(line)
                is_key_value_pair = self._key_value_pair.match(line)
                is_comment = self._comments.match(line)
                if is_section:
                    section_info = is_section.groups()
                    if section_info[0].count('[') != section_info[2].count(']'):
                        raise TypeError('Incorrect number of section braces.')
                    level = section_info[0].count('[')
                    if level == 1:
                        # if level is 1 than it is a top level section
                        previous_section = Section()
                        current_section = Section()
                        current_level = 1
                        self.settings[section_info[1]] = current_section
                        self.settings.inline_comments[section_info[1]] = section_info[3]
                        self.settings.comments[section_info[1]] = '\n'.join(comments)
                        comments = []
                    elif level > current_level:
                        # This is a sub section of the previous section
                        current_level = level
                        previous_section = current_section
                        current_section = Section()
                        previous_section[section_info[1]] = current_section
                        previous_section.inline_comments[section_info[1]] = section_info[3]
                        previous_section.comments[section_info[1]] = '\n'.join(comments)
                        comments = []
                    elif level == current_level:
                        # This is a sibling to the current section
                        current_level = level
                        current_section = Section()
                        previous_section[section_info[1]] = current_section
                        previous_section.inline_comments[section_info[1]] = section_info[3]
                        previous_section.comments[section_info[1]] = '\n'.join(comments)
                        comments = []
                if is_key_value_pair:
                    # If the data is a key value pair.
                    kvp_info = is_key_value_pair.groups()
                    current_section[kvp_info[0]] = kvp_info[1]
                    current_section.inline_comments[kvp_info[0]] = kvp_info[2]
                    current_section.comments[kvp_info[0]] = '\n'.join(comments)
                    comments = []
                if is_comment:
                    # Keep collecting comments. They will only be cleand up by
                    # the other operations.
                    comment_info = is_comment.groups()
                    comments.append(comment_info[0])
        return self.settings

    def save(self, file_name=None):
        '''
        Write the settings file to disk.
        '''
        self.file_name = file_name if file_name else self.file_name
        print 'Saving file to', self.file_name
        with open(self.file_name, 'wb') as f:
            self.__rec_save__(self.settings, f)

    def __rec_save__(self, settings, fp, level=1, padding=''):
        '''
        This function saves the settings in its original order.
        '''
        for scalar in settings.scalars:
            if settings.comments[scalar]: fp.write(settings.comments[scalar] + '\n')
            inline = settings.inline_comments[scalar] if settings.inline_comments[scalar] is not None else ''
            fp.write( '{0}{1}={2} {3}\n'.format(padding, scalar, settings[scalar], inline) ) 

        for section in settings.sections:
            if settings.comments[section]: fp.write(settings.comments[section] + '\n')
            inline = settings.inline_comments[section] if settings.inline_comments[section] is not None else ''
            fp.write('{0}{1}{2}{3} {4}\n'.format(padding, '['*level, section, ']'*level, inline))
            self.__rec_save__(settings[section], fp, level + 1, padding + '    ')


    def display_settings(self):
        '''
        write the settings to stdout
        '''
        self.__rec_disp_settings(self.settings)

    def __rec_disp_settings(self,settings, level=1, padding=''):

        for scalar in settings.scalars:
            print settings.comments[scalar]
            print padding, '{0} = {1} {2}'.format(scalar, settings[scalar], settings.inline_comments[scalar] if settings.inline_comments[scalar] else '')

        for section in settings.sections:
            print settings.comments[section]
            print padding, '{0} {1} {2} {3}'.format('['*level, section, ']'*level, settings.inline_comments[section] if settings.inline_comments[section] else '')
            self.__rec_disp_settings(settings[section], level + 1, padding + '    ')
