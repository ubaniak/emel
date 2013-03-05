import re
import os
import imp
import sys
import argparse
import subprocess
from utils.path.pathhandler import emel_train_file_path, create_path, create_marker
from utils.path.pathhandler import emel_project_tools_file_path, create_dir, emel_gather_data_file_path
from utils.settings.configobj import ConfigObj
from utils.userinput.userinput import yes_no_option
from emel.status import check_directory_status, check_project_status
from emel_globals import EMEL_CONFIG_FILE, Project, Data, INIT_MARKER
from emel_globals import EMEL_UTILS_FILE

from datetime import datetime

def __validate_config__():
    config = ConfigObj(EMEL_CONFIG_FILE)
    if Data.SECTION not in config: config[Data.SECTION] = {}
    if Data.CURRENT not in config[Data.SECTION]: config[Data.SECTION][Data.CURRENT] = ''
    if Data.ALL not in config[Data.SECTION]: config[Data.SECTION][Data.ALL] = {}
    if Project.SECTION not in config: config[Project.SECTION] = {}
    if Project.CURRENT not in config[Project.SECTION]: config[Project.SECTION][Project.CURRENT] = ''
    return config

SETTINGS_FILE = '''
# downloader
# This variable specifies the function to use to download the data.
# To find a list of available downloaders use emel.py gather-data --downloaders
# example:
#downloader='download_http'

# download
# a list of tuples where the first item in where to get the file from
# and the second item is where to download the data to.
# The function will always put the data in the data/raw folder.
#to_download=[(from location, to location), ...]
'''

SETTING_FILE_NAME = 'settings.py'

def __create_dg__():
    message = ('[WARNING] This will destroy any existing data gathering settings. Continue?')
    go = yes_no_option(message)
    if go:
        config = __validate_config__()

        dg_file = emel_gather_data_file_path()

        print 'Creating settings file ...',
        with open( create_path([dg_file, SETTING_FILE_NAME]), 'w' ) as fp:
            fp.write(SETTINGS_FILE)
        print 'Done.'
    else:
        print 'Aborting'


def __run_dg__():
    if not os.path.exists(dg_file):
        print '[ERROR] settings file does not exist.'
        print 'pleas run emel.py gather-data -h'
        exit()

    settings = imp.load_source('train_order', dg_file)
    downloaders = imp.load_source('downloaders', EMEL_UTILS_FILE)

    if hasattr(settings, 'downloader'):
        downloader = getattr(settings, 'downloader')
    else:
        print '[ERROR] downloader must be set.'
        print 'Go to', create_path([emel_gather_data_file_path(), SETTING_FILE_NAME])
        exit()

    if hasattr(settings, 'to_download'):
        to_downlaod = getattr(settings, 'to_download')
    else:
        print '[ERROR] to_download must be set.'
        print 'Go to', create_path([emel_gather_data_file_path(), SETTING_FILE_NAME])
        exit()
    
    getattr(downloaders, downloader)()

    

def __show_settings__():
    dg_file = create_path([emel_gather_data_file_path(), SETTING_FILE_NAME])

    if not os.path.exists(dg_file):
        print '[ERROR] settings file does not exist.'
        print 'pleas run emel.py gather-data -h'
        exit()

    settings = imp.load_source('train_order', dg_file)

    if hasattr(settings, 'downloader'):
        downloader = getattr(settings, 'downloader')
        print 'downloader = ', downloader
    else:
        print '[ERROR] downloader must be set.'
        print 'Go to', create_path([emel_gather_data_file_path(), SETTING_FILE_NAME])
        exit()

    if hasattr(settings, 'to_download'):
        to_downlaod = getattr(settings, 'to_download')
        print 'to_download = ', to_download
    else:
        print '[ERROR] to_download must be set.'
        print 'Go to', create_path([emel_gather_data_file_path(), SETTING_FILE_NAME])
        exit()



def __show_downloaders__():
    download_folder = 'downloaders'

    dl_path = create_path([EMEL_UTILS_FILE, download_folder])
    downloaders = os.listdir(dl_path)
    print 'Available downloader:'
    for dl in downloaders:
        if not dl.startswith('__'):
            print dl

    


def setup_arg_parser():
    '''
    Create the argument parser
    '''
    parser = argparse.ArgumentParser(description='Set up the data gather tool.')

    parser.add_argument('-n', '--new', action='store_true',
                    dest='new', help='Create a new data gather object.')
    parser.add_argument('-r', '--run', action='store_true',
                    dest='run', help='Run the current data gather object.')
    parser.add_argument('-s', '--show', action='store_true',
                    dest='show', help='prints the current data gather settings to stdout.')
    parser.add_argument('-d', '--downloaders', action='store_true',
                    dest='downloaders', help='Show all available downloaders.')
    return parser


def main(argv):
    '''
    '''
    parser = setup_arg_parser()
    options = parser.parse_args(argv)

    if not check_directory_status(True):
        exit()
    if not check_project_status(True):
        exit()

    if options.new:
        __create_dg__()
    elif options.run:
        __run_dg__()
    elif options.show:
        __show_settings__()
    elif options.downloaders:
        __show_downloaders__()

if __name__=='__main__':
    main(sys.argv[1:])
