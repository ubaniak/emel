"""
A collection of unittests for the settings.Settings object
"""
import sys
import unittest


class TestSettings(unittest.TestCase):
    """
    A collection of unittests for the settings.Settings object
    """
    def setUp(self):
        from os.path import dirname, join

    def test_basic(self):
        from settings.configmanager import ConfigManager, Section
        config = ConfigManager('c:/Code/emel/utils/settings/test/test.ini')
        config.display_settings()
        config.save('t2.ini')
        config2 = ConfigManager('t2.ini')
        config2.display_settings()
        print 'done'


def run_tests():
    """
    Run all TestSettings tests.
    """
    # This code pushes settings onto the path if necessary, so testing
    # can be done without installation. It is duplicated accross all
    # settings.test files so they each can be run independantly.
    # Unfortunately pylint can't locally disble the associated Warning.
    # Leaving the disable in, for when they fix that bug.
    # pylint: disable-msg=R0801
    import imp

    try:
        imp.find_module('settings')
    except ImportError:
        from os.path import dirname, abspath
        from sys import path
        print abspath(__file__)

        path.append(dirname(dirname(dirname(abspath(__file__)))))
    # pylint: enable-msg=R0801

    unittest.main()


if __name__ == '__main__':
    run_tests()
