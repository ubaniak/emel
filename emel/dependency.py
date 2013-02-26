import sys
import argparse
import os
import re
import imp

from utils.settings.configobj import ConfigObj
from utils.path.pathhandler import create_dir, create_path, create_marker
from utils.userinput.userinput import yes_no_option
from emel.status import check_directory_status, check_project_status
from emel_globals import EMEL_CONFIG_FILE, Project, Data

def __validate_config__():
    config = ConfigObj(EMEL_CONFIG_FILE)
    if Data.SECTION not in config: config[Data.SECTION] = {}
    if Data.CURRENT not in config[Data.SECTION]: config[Data.SECTION][Data.CURRENT] = ''
    if Data.ALL not in config[Data.SECTION]: config[Data.SECTION][Data.ALL] = {}
    if Project.SECTION not in config: config[Project.SECTION] = {}
    if Project.CURRENT not in config[Project.SECTION]: config[Project.SECTION][Project.CURRENT] = ''
    return config


def __check_dependencies__():
    default = ['sklearn', 're']

    for module in default:
        try:
            imp.find_module(module)
            print 'Successfully imported {}'.format(module)
        except ImportError:
            print '!!! Cannot import {}'.format(module)

        


def __list_dependencies__():
    pass


def __create_dep_list__():
    if not check_directory_status(True):
        exit()
    if not check_project_status(True):
        exit()
    pass


def setup_arg_parser():
    '''
    Create the argument parser
    '''
    parser = argparse.ArgumentParser(description='Check if 3rd party python packages are installed.')

    parser.add_argument('-c', '--check', action='store_true', 
                    dest='check', help='Checks the dependencies.')
    parser.add_argument('-n', '--new', action='store_true', 
                    dest='new', help='Creates a new dependency file in the current project directory.')
    parser.add_argument('-ls', '--list', action='store_true', 
                    dest='listDeps', help='Checks the list of dependencies.')
    return parser


def main(argv):
    '''
    '''
    parser = setup_arg_parser()
    options = parser.parse_args(argv)

    if options.listDeps:
        __list_dependencies__()
    elif options.new:
        __create_dep_list__()
    elif options.check:
        __check_dependencies__()


if __name__=='__main__':
    main(sys.argv[1:])
