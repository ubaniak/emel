import sys
import argparse
import os
import re

from utils.settings.configobj import ConfigObj
from utils.path.pathhandler import create_dir, create_path, create_marker
from utils.userinput.userinput import yes_no_option
from emel.status import check_directory_status, check_project_status
from emel_globals import EMEL_CONFIG_FILE, Project, Data
GLOBAL = 'g'
PROJECT = 'p'
BOTH = 'b'


TOOL_TEMPLATE = r'''
from utils.path.pathhandler import emel_raw_file_path, emel_processed_file_path
from utils.path.pathhandler import emel_train_file_path, emel_project_path
def {0}():
    print "I am a new tool. Find me at {1}"
'''
# TODO: delete projects.
def __validate_config__():
    config = ConfigObj(EMEL_CONFIG_FILE)
    if Data.SECTION not in config: config[Data.SECTION] = {}
    if Data.CURRENT not in config[Data.SECTION]: config[Data.SECTION][Data.CURRENT] = ''
    if Data.ALL not in config[Data.SECTION]: config[Data.SECTION][Data.ALL] = {}
    if Project.SECTION not in config: config[Project.SECTION] = {}
    if Project.CURRENT not in config[Project.SECTION]: config[Project.SECTION][Project.CURRENT] = ''
    return config


def __create_tool__(catagory, tool_name, is_global=True):

    config = __validate_config__()
    if not is_global:
        data_dir = config[Data.SECTION][Data.ALL][config[Data.SECTION][Data.CURRENT]]
        project = config[Project.SECTION][Project.CURRENT]

        new_cat_path = create_path([data_dir, project, 'tools', catagory])
    else:
        new_cat_path = create_path(['tools', catagory])

    if catagory not in __get_catagories__(is_global=is_global):
        choice = yes_no_option('"{0}" is not a catagory. Would you like to create it ?'.format(catagory))
        if choice:
            create_dir(new_cat_path, verbose=True)
            create_marker(new_cat_path, '__init__.py')
        else:
            print '[WARNING] emel did not create {0}->{1}.'.format(catagory, tool_name)
            exit()

    if os.path.exists(create_path([new_cat_path, tool_name + '.py'])):
       print '[WARNING] {0}->{1} all ready exists.'.format(catagory, tool_name)
       exit()

    fp = open( create_path([new_cat_path, tool_name+'.py']), 'w' )
    fp.write( TOOL_TEMPLATE.format(tool_name, re.sub('\\\\', '/', new_cat_path)) )
    fp.close()
    print 'Created a new tool at {0}/{1}.py'.format(re.sub('\\\\', '/',new_cat_path), tool_name)


def __get_catagories__(verbose=True, is_global=True):
    config = __validate_config__()
    if not is_global:
        data_dir = config[Data.SECTION][Data.ALL][config[Data.SECTION][Data.CURRENT]]
        project = config[Project.SECTION][Project.CURRENT]

        tools_path = create_path([data_dir, project, 'tools'])
    else:
        tools_path = create_path(['tools'])

    files = [ root for root, _, files in os.walk(tools_path) ]
    files = [ os.path.split(f)[-1] for f in files[1:] ]
    if verbose:
        project = config[Project.SECTION][Project.CURRENT]
        print 'Project ('+project+') specific catagories:' if not is_global else "Global catagories:"
        for f in files:
            print '\t', f
    return files

def __show_tools__(verbose=True, is_global=True):
    config = __validate_config__()
    if not is_global:
        data_dir = config[Data.SECTION][Data.ALL][config[Data.SECTION][Data.CURRENT]]
        project = config[Project.SECTION][Project.CURRENT]

        tools_path = create_path([data_dir, project, 'tools'])
    else:
        tools_path = create_path(['tools'])

    project = config[Project.SECTION][Project.CURRENT]
    print 'Project ('+project+')  catagories:' if not is_global else "Global catagories:"
    
    for root, d, files in os.walk(tools_path):
        catagory = os.path.split(root)[-1]
        if catagory != 'tools':
            print '\t', catagory
            files = [ f for f in files if not f.startswith('__') ]
            for f in files:
                print '\t\t', f


def __show_catagories__(location):
    config = __validate_config__()
    location = location if location else BOTH

    if location == GLOBAL:
        __get_catagories__()
    elif location == PROJECT:
        __get_catagories__(is_global=False)
    elif location == BOTH:
        __get_catagories__()
        __get_catagories__(is_global=False)

def __list_tools__(location):
    config = __validate_config__()
    location = location if location else BOTH
    if location == GLOBAL:
        __show_tools__()
    elif location == PROJECT:
        __show_tools__(is_global=False)
    elif location == BOTH:
        __show_tools__()
        __show_tools__(is_global=False)

def setup_arg_parser():
    '''
    Create the argument parser
    '''
    parser = argparse.ArgumentParser(description='Allows the user to view/create all global or project specific tools.')

    parser.add_argument('-p', '--new_project_tool', action='store', nargs = 2,  
                    dest='new_project_tool', default=None, help='<catagory>, <name> creates a new project specific tool.')
    parser.add_argument('-g', '--new_global_tool', action='store', nargs=2, 
                    dest='new_global_tool', default=None, help='creates a new project specific tool.')
    parser.add_argument('-ls', '--list', action='store', nargs='?',
                    dest='list_tools', default='s', help='List all tools.')
    parser.add_argument('-c', '--show_catagories', nargs='?', action='store', 
                    dest='show_catagories', default='s', help='Gives a list of all catagories available. Add p for project only, g for global only and b for both.')
    return parser


def main(argv):
    '''
    '''
    parser = setup_arg_parser()
    options = parser.parse_args(argv)

    if options.new_project_tool:
        __create_tool__(options.new_project_tool[0], options.new_project_tool[1], is_global=False)
    elif options.new_global_tool:
        __create_tool__(options.new_global_tool[0], options.new_global_tool[1], is_global=True)
    elif options.show_catagories != 's':
        __show_catagories__(options.show_catagories)
    elif options.list_tools != 's':
        __list_tools__(options.list_tools)


if __name__=='__main__':
    main(sys.argv[1:])
