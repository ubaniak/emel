import sys
import argparse
import os
import re
import subprocess
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

# Check if pip or easy_install is Installed
def __get_installer__():
    easy_install = subprocess.call(['easy_install','--version'])
    pip = subprocess.call(['pip','--version'])

    if easy_install != 0 and pip != 0:
        print 'ERROR: cannot find easy_install or pip.'
        exit()
    elif easy_install == 0 and pip == 0:
        # pip is the installer of choice.
        installer = 'pip'
    elif easy_install != 0 and pip == 0:
        installer = 'easy_install'
    elif easy_install == 0 and pip != 0:
        installer = 'pip'
    return installer


def __get_list__():
    the_list = DEFULT
    if check_project_status():
        depFile = create_path([emel_project_path(), DEPENDENCY_FILE])
        if os.path.exists(depFile):
            the_list = []
            with open(depFile, 'r') as f:
                for line in f.readlines():
                    if not line.startswith('#'):
                        line = line.split('#')
                        the_list.append(line[0].strip())
    return the_list

def __sanitize_moduel__(module):
    regex = re.compile(';|&|-r')
    m = regex.search(module)
    if m:
        return False
    else:
        return True


def __install_dependencies__(verbose=False):
    message = ('[WARNING] This will install all listed dependencies.\n'
               'Please make sure you are sudo.')
    go = yes_no_option(message)
    if go:
        installer = __get_installer__()

        for module in __get_list__():
            print '\n*****Installing:', module,'*****\n'
            if __sanitize_moduel__(module):
                status = subprocess.call([installer, 'install', module])
                if status != 0:
                    print '\n*****Failed to install', module,'*****'
                else:
                    print '\n*****Successflly installed', module,'*****'
            else:
                print 'Rejecting', module
    else:
        print 'Aborting.'

def __list_dependencies__(verbose=False):

    can_run = True
    for module in __get_list__():
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
        message = 'Creatint dependency file for project.\n [WARNING] will overrite existing file. Continue?'
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
    parser.add_argument('--install', action='store_true', 
                    dest='install', help='Install the selected modules.')
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
    elif options.install:
        __install_dependencies__()


if __name__=='__main__':
        main(sys.argv[1:])
