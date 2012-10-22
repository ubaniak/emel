"""
The Settings class provides a simple JSON-based settings object that is
meant to bring the LoadConfiguration settings experience to python.

Settings objects allow for loading from multiple settings files with
overwriting of values (like client.dat and user.dat). Settings objects
store values liek dicts, but behave like a Matlab structs, with keys
accessed as attributes (e.g. settings.foo.bar.baz).
"""
# enable: from settings import Settings
# instead of just: from settings.settings import Settings
# pylint: disable-msg=W0403
from settings import Settings
# pylint: enable-msg=W0403
