import sys
import argparse
import os
from glob import glob
import re

from utils.settings.configobj import ConfigObj
#from utils.settings.configmanager import ConfigManager
from utils.path.pathhandler import create_dir, create_path, create_marker
from utils.userinput.userinput import yes_no_option
from emel_globals import EMEL_CONFIG_FILE, Data, Project, INIT_MARKER
from emel.status import check_directory_status


def __validate_config__():
    config = ConfigObj(EMEL_CONFIG_FILE)
    if Data.SECTION not in config: config[Data.SECTION] = {}
    if Data.CURRENT not in config[Data.SECTION]: config[Data.SECTION][Data.CURRENT] = ''
    if Data.ALL not in config[Data.SECTION]: config[Data.SECTION][Data.ALL] = {}
    if Project.SECTION not in config: config[Project.SECTION] = {}
    if Project.CURRENT not in config[Project.SECTION]: config[Project.SECTION][Project.CURRENT] = ''
    return config


def __scan_directory__(locations, addCurrent=True):
    '''
    Scans a given location for any directories with a data marker in it.
    If it finds a directory 
    '''
    config = __validate_config__()
    locations = [os.getcwd()] if not locations else locations
    for location in locations:
        print 'Scanning', location, '...',
        files = [ root for root, _, files in os.walk(location) if Data.MARKER in files ]
        untracked = [ {os.path.split(f)[-1]: f} for f in files if f not in config[Data.SECTION][Data.ALL].values() ]

        print 'Done.\n'
        print 'Found (', len(untracked), ') untracked folder(s).\n'
        if untracked:
            [ config[Data.SECTION][Data.ALL].update(f) for f in untracked ]
            config.write()

        if not config[Data.SECTION][Data.CURRENT] and addCurrent:
            print '\n[WARNING] Current directory is not set.'
            print 'use emel.py data cd <label> to set the data directory.'

def __create_directory__(data_tuple, setAsCurrent=True, create=True, islocation=True):
    '''
    Sets the location of the data directory in the emel.config file.
    '''
    config = __validate_config__()
    data_tuple = data_tuple if isinstance(data_tuple, list) else [data_tuple]
    if not data_tuple:
        print '[ERROR] Please supply a lable for this data directory.'
        exit()
    
    lable = data_tuple[0]
    location = create_path([data_tuple[1],lable]) if len(data_tuple) > 1 else create_path([os.getcwd(), lable])

    if create: 
        print 'Attempting to create', lable, 'at location', location, 
        current = create_dir(location, True, True)
        if current:
            create_marker(current, Data.MARKER)
            create_marker(current, INIT_MARKER)
        if not os.path.isdir(location):
            print '\n[ERROR] "{0}" is not a valid path.'.format(location)
            exit()

    if current and setAsCurrent: config[Data.SECTION][Data.CURRENT] = lable
    if current and lable not in config[Data.SECTION][Data.ALL]: config[Data.SECTION][Data.ALL][lable] = location
    print 'Done.'

    config.write()


def __show_directories__():
    '''
    Show all the data directories stored in the "all" section in the config file. 
    '''
    config = __validate_config__()
    if not config[Data.SECTION][Data.ALL]:
        print 'No data directories are listed'
        return

    print 'All known data directories:'
    dirs = config[Data.SECTION][Data.ALL]
    for lable, location in zip(dirs.keys(), dirs.values()):
        if lable == config[Data.SECTION][Data.CURRENT]:
            print '  #   *','(',lable,')',location
        else:
            print '  #    ','(',lable,')',location
    if not config[Data.SECTION][Data.CURRENT]:
        print '\n[WARNING] No current directory set'
        print 'use emel.py data cd <label> to set the data directory.'


def __change_directory__(lable):
    config = __validate_config__()
    if lable not in config[Data.SECTION][Data.ALL]:
        print '"{0}" is not a known data directory.'.format(lable)
    else:
        print 'Setting new directory to "{0}"'.format(lable)
        config[Data.SECTION][Data.CURRENT] = lable
        config[Project.SECTION][Project.CURRENT] = ''
        config.write()


def setup_arg_parser():
    '''
    Create the argument parser
    '''
    parser = argparse.ArgumentParser(description='This module sets the location of the emel Data directory.')

    parser.add_argument('-n', '--new', action='store', nargs='+',  
                    dest='new', default=os.getcwd(), help='<lable> <location> Sets the location of the data directory. If a location is not given, data will use the current working directory')
    parser.add_argument('-ls', '--list', action='store_true', 
                    dest='listDirs', help='List all known Data directories')
    parser.add_argument('-cd', '--change_directory', action='store', 
                    dest='change_directory', default=None, help='Change the current directory to one of the known directories. Uses the index given from ls.')
    parser.add_argument('-s', '--scan', action='store', nargs='*', 
                    dest='scan', default=None, help='Scans a given directory for the existance of unknown data directories. If they do the tool will add them to the list of known data directories.')
    return parser


def main(argv):
    '''
    '''
    parser = setup_arg_parser()
    options = parser.parse_args(argv)

    if not argv:
        check_directory_status(True)
        __show_directories__()
    else:
        if options.listDirs:
            __show_directories__()
        elif options.change_directory is not None:
            __change_directory__(options.change_directory)
        elif options.scan is not None:
            __scan_directory__(options.scan)
        else:
            __scan_directory__(options.new[1] if len(options.new) > 1 else None, False)
            __create_directory__(options.new)


if __name__=='__main__':
    main(sys.argv[1:])
