import sys
import argparse
import os
from glob import glob
import re

from utils.settings.configobj import ConfigObj
from utils.path.pathhandler import create_dir, create_path, create_marker
from utils.userinput.userinput import yes_no_option
from emel_globals import EMEL_CONFIG_FILE, Data


def __validate_config__():
    config = ConfigObj(EMEL_CONFIG_FILE)
    if Data.SECTION not in config: config[Data.SECTION] = {}
    if Data.CURRENT not in config[Data.SECTION]: config[Data.SECTION][Data.CURRENT] = ''
    if Data.ALL not in config[Data.SECTION]: config[Data.SECTION][Data.ALL] = []
    return config


def __scan_directory__(location, addCurrent=True):
    '''
    Scans a given location for any directories with a data marker in it.
    If it finds a directory 
    '''
    config = __validate_config__()
    location = os.getcwd() if not location else location
    print 'Scanning', location, '...'
    files = [ root for root, _, files in os.walk(location) if Data.MARKER in files ]
    untracked = [ f for f in files if f not in config[Data.SECTION][Data.ALL] ]

    print 'Found (', len(untracked), ') untracked folders.'
    if untracked:
        [ config[Data.SECTION][Data.ALL].append(f) for f in untracked ]
        if not config[Data.SECTION][Data.CURRENT] and addCurrent:
            print '\nCurrent directory is not set.'
            print 'Setting"',config[Data.SECTION][Data.ALL][0], '" as current.'
            config[Data.SECTION][Data.CURRENT] = config[Data.SECTION][Data.ALL][0]
        config.write()


def __create_directory__(location, setAsCurrent=True, create=True, islocation=True):
    '''
    Sets the location of the data directory in the emel.config file.
    '''
    config = __validate_config__()
    current = create_path([location, 'Data']) if islocation else location
    if create: 
        print 'Attempting to create', current
        current = create_dir(current, True, True)
        if current: create_marker(current, Data.MARKER)

    if setAsCurrent and current: config[Data.SECTION][Data.CURRENT] = current
    if current and current not in config[Data.SECTION][Data.ALL]: config[Data.SECTION][Data.ALL].append(current)
    print 'Done.'

    config.write()


def __remove_directory__():
    '''
    Removes a location from the config file.
    Does NOT delete the directory.
    '''
    config = __validate_config__()
    print 'Removing "{0}" as the current directory.'.format(config[Data.SECTION][Data.CURRENT])
    print "This will not delete the folder."
    config[Data.SECTION][Data.CURRENT] = ''
    config.write()


def __show_directories__():
    '''
    Show all the data directories stored in all_data_dirs.
    '''
    config = __validate_config__()
    i = 0
    if not config[Data.SECTION][Data.ALL]:
        print 'No data directories are listed'
        return

    print 'All known data directories:'
    for dd in config[Data.SECTION][Data.ALL]:
        if dd == config[Data.SECTION][Data.CURRENT]:
            print '  #   *','(',i,')',dd
        else:
            print '  #    ','(',i,')',dd
        i += 1


def __change_directory__(newLocation):
    config = __validate_config__()
    i = 0
    for directory in config[Data.SECTION][Data.ALL]:
        if i == newLocation: 
            print 'Changing current directory to "{0}"'.format(directory)
            config[Data.SECTION][Data.CURRENT] = directory
            config.write()
            break
        i += 1


def setup_arg_parser():
    '''
    Create the argument parser
    '''
    parser = argparse.ArgumentParser(description='This module sets the location of the emel Data directory.')

    parser.add_argument('-n', '--new', action='store',  
                    dest='new', default=os.getcwd(), help='Sets the location of the data directory. If not given, data will use the current working directory')
    parser.add_argument('-rm', '--remove', action='store_true', 
                    dest='remove', help='Removes the data directory from the config file. This will NOT delete the data directory.')
    parser.add_argument('-ls', '--list', action='store_true', 
                    dest='listDirs', help='List all known Data directories')
    parser.add_argument('-cd', '--change_directory', action='store', type=int, 
                    dest='change_directory', default=None, help='Change the current directory to one of the known directories. Uses the index given from ls.')
    parser.add_argument('-s', '--scan', action='store', nargs='*', 
                    dest='scan', default=None, help='Scans a given directory to see if data directories exist in a given location. If they do the tool will add them to the list of known data directories.')
    return parser


def main(argv):
    '''
    '''
    parser = setup_arg_parser()
    options = parser.parse_args(argv)

    if options.listDirs:
        __show_directories__()
    elif options.change_directory is not None:
        __change_directory__(options.change_directory)
    elif options.remove:
        __remove_directory__()
    elif options.scan is not None:
        __scan_directory__(options.scan)
    else:
        __scan_directory__(options.new, False)
        __create_directory__(options.new)


if __name__=='__main__':
    main(sys.argv[1:])
