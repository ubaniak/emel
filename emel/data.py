import sys
import argparse
import os
from utils.settings.configobj import ConfigObj

EMEL_CONFIG_FILE = os.getcwd() + os.sep + 'emel.conf'


def __set_location__(location):
    '''
    Sets the location of the data directory in the emel.config file.
    '''
    current = location + os.sep + 'Data'
    if not os.path.isdir(current):
        print 'Creatint Data folder at', current
        os.makedirs(current)
    else:
        print 'Directory', current, 'allready exists'

    config = ConfigObj(EMEL_CONFIG_FILE)
    if 'data_directory' not in config: config['data_directory'] = {}
    if 'all_data_dirs' not in config['data_directory']: config['data_directory']['all_data_dirs'] = []

    config['data_directory']['current'] = current

    if current not in config['data_directory']['all_data_dirs']: 
        config['data_directory']['all_data_dirs'].append(current)

    config.write()


def __remove_location__():
    '''
    Removes a location from the config file.
    '''
    config = ConfigObj(EMEL_CONFIG_FILE)
    print "Removing '{0}' from config file.".format(config['data_directory']['current'])
    print "This will not delete the folder."
    config['data_directory']['current'] = ''
    config.write()


def __show_locations__():
    '''
    Show all the data directories stored in all_data_dirs.
    '''
    config = ConfigObj(EMEL_CONFIG_FILE)
    i = 0
    print 'All known data directories:'
    for dd in config['data_directory']['all_data_dirs']:
        print '\t','(',i,')',dd
        i += 1

def __change_location__(newLocation):
    config = ConfigObj(EMEL_CONFIG_FILE)
    allKnownDirectories = config['data_directory']['all_data_dirs']
    i = 0
    for directory in allKnownDirectories:
        if i == newLocation:
            config['data_directory']['current'] = directory
        i += 1

    config.write()


def setup_arg_parser():
    '''
    Create the argument parser
    '''
    parser = argparse.ArgumentParser(description='This module sets the location of the emel Data directory.')

    parser.add_argument('-n', '--new', action='store',  
                    dest='new', default=os.getcwd(), help='Sets the location of the data directory. Defaults to the current working directory.')
    parser.add_argument('-rm', '--remove', action='store_true', 
                    dest='remove', help='Removes the data directory from the config file. This will NOT delete the data directory.')
    parser.add_argument('-ls', '--list', action='store_true', 
                    dest='listDirs', help='List all past Data directories')
 ##### MAKE THIS STORE AN INT
    parser.add_argument('-cl', '--change_location', action='store', 
                    dest='change_location', default=None, help='Change the current directory to one of the known directories')
    return parser


def main(argv):
    '''
    '''
    parser = setup_arg_parser()
    options = parser.parse_args(argv)

    if options.listDirs:
        __show_locations__()
    elif options.change_location:
        __change_location__(options.change_location)
    elif options.remove:
        __remove_location__()
    else:
        __set_location__(options.new)


if __name__=='__main__':
    main(sys.argv[1:])
