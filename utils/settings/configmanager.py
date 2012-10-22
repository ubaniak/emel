"""
The Settings class provides a simple JSON-based settings object that is
meant to bring the LoadConfiguration settings experience to python.

Settings objects allow for loading from multiple settings files with
overwriting of values (like client.dat and user.dat). Settings objects
store values liek dicts, but behave like a Matlab structs, with keys
accessed as attributes (e.g. settings.foo.bar.baz).
"""
import re

class 

class Section(dict):
    def __init__(self):
        self.scalars = []
        self.sections = []
        self.comments = {}
        self.inline_comments = {}

    def __setitem__(self, key, value):
        '''Add an item to the Section object.'''
        if isinstance(value, Section):
            self.sections.append(key)
        else:
            self.scalars.append(key)
        dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        '''Return an item with the given key from the Section object.'''
        return dict.__getitem__(self, key)

    def __delitem__(self, key):
        '''Remove an item '''
        dict.__delitem__(self, key)


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
                                    ((?:[a-z0-9_]*))
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
            print padding, '{0} = {1} {2}'.format(scalar, settings[scalar], settings.inline_comments[scalar])

        for section in settings.sections:
            print settings.comments[section]
            print padding, '{0} {1} {2} {3}'.format('['*level, section, ']'*level, settings.inline_comments[section])
            self.__rec_disp_settings(settings[section], level + 1, padding + '    ')






















