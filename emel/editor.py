import os
import sys
import argparse
from utils.settings.configobj import ConfigObj
from emel_globals import EMEL_CONFIG_FILE, Editor


def __validate_config__():
    config = ConfigObj(EMEL_CONFIG_FILE)
    return config


def __set_editor__(editor):
    print 'Setting default editor to', editor,
    config = __validate_config__()
    config[Editor.SECTION] = {}
    config[Editor.SECTION][Editor.CURRENT] = ''
    config[Editor.SECTION][Editor.CURRENT] = editor
    config.write()
    print 'Done'

def __run_editor__(files):
    config = __validate_config__()
    if Editor.SECTION not in config or not config[Editor.SECTION] or not config[Editor.SECTION][Editor.CURRENT]:
        print '[WARNING] Editor is not set.'
        print 'run emel.py editor -h for more info'
        exit()

    editor = config[Editor.SECTION][Editor.CURRENT]
    os.system(editor + ' ' + ' '.join(files))

def __show_editor__():
    config = __validate_config__()
    if Editor.SECTION not in config or not config[Editor.SECTION] or not config[Editor.SECTION][Editor.CURRENT]:
        print '[WARNING] Editor is not set.'
        print 'run emel.py editor -h for more info'
        exit()

    print 'Current editor set to "', config[Editor.SECTION][Editor.CURRENT], '"'

def setup_arg_parser():
    '''
    Create the argument parser
    '''
    parser = argparse.ArgumentParser(description='Sets up the train object.')

    parser.add_argument('--set', action='store', default=None,
                    dest='set', help='Set the editor.')
    parser.add_argument('-r', '--run', action='store', default=[], nargs='*',
                    dest='run', help='Run the current train object.')
    parser.add_argument('--which', action='store_true',
                    dest='which', help='Shows the default editor.')
    return parser


def main(argv):
    '''
    '''
    parser = setup_arg_parser()
    options = parser.parse_args(argv)

    if options.set:
        __set_editor__(options.set)
    elif options.which:
        __show_editor__()
    elif options.run is not None:
        __run_editor__(options.run)

if __name__=='__main__':
    main(sys.argv[1:])
