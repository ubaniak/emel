"""
The Settings class provides a simple JSON-based settings object that is
meant to bring the LoadConfiguration settings experience to python.

Settings objects allow for loading from multiple settings files with
overwriting of values (like client.dat and user.dat). Settings objects
store values liek dicts, but behave like a Matlab structs, with keys
accessed as attributes (e.g. settings.foo.bar.baz).
"""
import json
import re


class Settings(object):
    """
    A JSON-based settings object designed to mimic the LoadConfiguration
    system used in Matlab. Loaded settings are designed to be accessed
    as attributes (e.g. settings.foo.bar.baz), and allow for names to
    be accessed dynamically (e.g. setting.foo('bar').baz).

    The raw dictionary can be accessed at any time using dict-style
    access (e.g. foo['bar']), or by calling the Settings objects
    built-in as_dict method.

    To allow multiple settings files to be added together, Settings
    objects can be added together. It is important to note that addition
    is not commutative (a + b != b + a). Values in the right-hand object
    overwrite properties in the left-hand object in cases where values
    differ.

    NOTE: The correct way to instantiate a Settings object is using the
    load_configuration, or load_data factory methods.
    """
    def __init__(self, settings=None):
        self._settings = {}

        if settings is not None:
            for key in settings:
                self[key] = settings[key]

    def __call__(self, key):
        """
        s(key)

        Return a child Settings object

        key: the child to return

        NOTE: this method also provides away of accessing children with
        illegal names (e.g. as_dict) as Settings objects
        """
        if key not in self:
            # raise an AttributeError not a KeyError
            # error for struct-access: AttributeError
            # error for raw-access: KeyError
            raise AttributeError('{0} object has no attribute {1}'.format(
                                 self.__class__.__name__, repr(key)))
        return self.load_data(self[key])

    def __setitem__(self, key, value):
        """
        s[key] = value

        add a child to the settings object

        key: the name of the child
        value: the value of the child
        """
        self._settings[key] = value

        # add the key as an attribute if possible
        if self.valid_attribute_name(key):
            setattr(self, key, self.load_data(value))

    def __getitem__(self, key):
        """
        s[key]

        get a child as a raw dict

        key: the child to return
        """
        return self._settings[key]

    def __delitem__(self, key):
        """
        del s[key]

        remove a child

        key: the child to remove
        """
        if self.valid_attribute_name(key):
            delattr(self, key)

        del self._settings[key]

    def __contains__(self, key):
        """
        key in s[key]

        test whether a child is in the Settings object

        key: the name of the (potential) child
        """
        return key in self._settings

    def __len__(self):
        """
        len(s)

        calculate how many children are in the object
        """
        return len(self._settings)

    def __iter__(self):
        """
        (key for key in s)

        iterate through all children
        """
        return self._settings.__iter__()

    def __add__(self, other):
        """
        s + other

        Add a settings object or dict to this settings object

        NOTE: s + other != other + s
        """
        if isinstance(other, self.__class__):  # same type
            new = Settings()

            skeys = set([key for key in self])
            okeys = set([key for key in other])

            # only in self
            for key in (skeys - okeys):
                new[key] = self[key]

            # only in other
            for key in (okeys - skeys):
                new[key] = other[key]

            # in both
            for key in skeys.intersection(okeys):
                # note that the children are beign accessed as Settings
                # objects, not as raw values. Otherwise, values would be
                # overwritten
                if (isinstance(self(key), Settings) and isinstance(other(key),
                                                                   Settings)):
                    new[key] = self(key) + other(key)  # as Settings objects
                else:
                    new[key] = other[key]

            return new
        elif isinstance(other, dict):
            return self + Settings(other)
        else:
            return NotImplemented  # allow others to expand on addition

    def __radd__(self, other):
        """
        other + s

        add this settings object to a settings object or dict

        NOTE: s + other != other + s
        """
        if isinstance(other, self.__class__):
            return other.__add__(self)
        elif isinstance(other, dict):
            return Settings(other) + self
        else:
            return NotImplemented

    def __repr__(self):
        return ''.join(['s{',
                        ','.join(['{0}: {1}'.format(repr(k), repr(self(k)))
                                  for k in self]), '}'])

    def __str__(self):
        return ''.join(['{', ','.join(['{0}: {1}'.format(str(k), str(self(k)))
                                       for k in self]), '}'])

    def to_dict(self):
        """
        Create a dict representation of the settings object.
        """
        return self._settings

    def save(self, filepath, indentation=2):
        """
        Save the settings object as a JSON file.

        filepath: where to save the settings
        indentation: the level of indentation to use (default: 2)
        """
        with open(filepath, 'w') as file_object:
            json.dump(self._settings, file_object, indent=indentation)

    @classmethod
    def valid_attribute_name(cls, key):
        """
        Tests whether a key may be used as an attribute name. To be
        usable, the key must be a string/unicode containing only
        alphanumeric characters (and underscores) that starts with an
        alphabetic character and is not already set by the class.

        key: the value being checked
        """
        return (isinstance(key, basestring) and
                re.match('^[A-Za-z][A-Za-z_0-9]*$', key) and
                not hasattr(cls, key))

    @classmethod
    def load_data(cls, data):
        """
        Build a Settings object. This is the preferred way to build a
        settings object, as it handles any kind of data, not just dicts.

        data: the data to build the Settings object with
        """
        if isinstance(data, list):
            return [cls.load_data(sub) for sub in data]
        elif isinstance(data, dict):
            return cls(data)
        else:  # already a leaf
            return data

    @classmethod
    def load_configuration(cls, *args):
        """
        Build a Settings object from a JSON-formatted file.

        *args: Any number of settings files
        """
        settings = cls()

        for filepath in args:
            with open(filepath, 'r') as file_object:
                settings += cls.load_data(json.load(file_object))

        return settings
