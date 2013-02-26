import sys
import argparse
import os
import re
import imp

from utils.settings.configobj import ConfigObj
from utils.path.pathhandler import create_dir, create_path, create_marker
from utils.path.pathhandler import emel_project_path
from utils.userinput.userinput import yes_no_option
from emel.status import check_directory_status, check_project_status
from emel_globals import EMEL_CONFIG_FILE, Project, Data

# The default list of things emel needs.
DEFULT = ['sklearn']
DEPENDENCY_FILE = 'dependency'

def __validate_config__():
    config = ConfigObj(EMEL_CONFIG_FILE)
    if Data.SECTION not in config: config[Data.SECTION] = {}
    if Data.CURRENT not in config[Data.SECTION]: config[Data.SECTION][Data.CURRENT] = ''
    if Data.ALL not in config[Data.SECTION]: config[Data.SECTION][Data.ALL] = {}
    if Project.SECTION not in config: config[Project.SECTION] = {}
    if Project.CURRENT not in config[Project.SECTION]: config[Project.SECTION][Project.CURRENT] = ''
    return config


def __list_dependencies__(verbose=False):
    the_list = DEFULT
    if check_project_status():
        the_list = []
        depFile = create_path([emel_project_path(), DEPENDENCY_FILE])

        with open(depFile, 'r') as f:
            for line in f.readlines():
                if not line.startswith('#'):
                    line = line.split('#')
                    the_list.append(line[0].strip())
    can_run = True
    for module in the_list:
        try:
            imp.find_module(module)
            if verbose:
                print module, '[Installed]'
        except ImportError:
            if verbose:
                print module, '[Missing]'
            can_run = False

    return can_run


def __create_dep_list__(check_first=True):
    if not check_directory_status(True):
        exit()
    if not check_project_status(True):
        exit()
    create = True
    if check_first:
        message = 'Creatint dependency file for project.\n WARNING: will overrite existing file. Continue?'
        create = yes_no_option(message)

    if create:
        depFile = create_path([emel_project_path(), DEPENDENCY_FILE])
        with open(depFile, 'w') as f:
            f.write('# emel default packages #\n')
            for module in DEFULT:
                f.write(module)
                f.write('\n')
            f.write('# End emel defaults #')


def setup_arg_parser():
    '''
    Create the argument parser
    '''
    parser = argparse.ArgumentParser(description='Check if 3rd party python packages are installed.')

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
        __list_dependencies__(True)
    elif options.new:
        __create_dep_list__()


if __name__=='__main__':
        main(sys.argv[1:])
