import sys
import argparse
import os
import re

from utils.settings.configobj import ConfigObj
from utils.path.pathhandler import create_dir, create_path, create_marker
from utils.userinput.userinput import yes_no_option
from emel.status import check_directory_status, check_project_status
from emel.editor import __run_editor__
from emel_globals import EMEL_CONFIG_FILE, EMEL_UTILS_FILE, Project, Data


TOOL_TEMPLATE = r'''
import sys
sys.path.append('{0}')
from utils.path.pathhandler import emel_raw_file_path, emel_processed_file_path
from utils.path.pathhandler import emel_train_file_path, emel_project_path


def {1}():
    print "I am a new tool. Find me at {2}"
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


def __create_tool__(catagory, tool_name):

    config = __validate_config__()
    data_dir = config[Data.SECTION][Data.ALL][config[Data.SECTION][Data.CURRENT]]
    project = config[Project.SECTION][Project.CURRENT]

    new_cat_path = create_path([data_dir, project, 'tools', catagory])

    if catagory not in __get_catagories__(False):
        choice = yes_no_option('"{0}" is not a catagory. Would you like to create it ?'.format(catagory))
        if choice:
            create_dir(new_cat_path, verbose=True)
            create_marker(new_cat_path, '__init__.py')
        else:
            print '[WARNING] emel did not create {0}->{1}. user aborted.'.format(catagory, tool_name)
            exit()

    if os.path.exists(create_path([new_cat_path, tool_name + '.py'])):
       print '[WARNING] {0}->{1} all ready exists.'.format(catagory, tool_name)
       exit()

    fp = open( create_path([new_cat_path, tool_name+'.py']), 'w' )
    fp.write( TOOL_TEMPLATE.format(EMEL_UTILS_FILE, tool_name, re.sub('\\\\', '/', new_cat_path)) )
    fp.close()
    print 'Created a new tool at {0}/{1}.py'.format(re.sub('\\\\', '/',new_cat_path), tool_name)
    if yes_no_option('Would you like to edit the tool now?'):
        __run_editor__([os.path.join(new_cat_path, tool_name + '.py')])


def __get_catagories__(verbose=True):
    config = __validate_config__()
    data_dir = config[Data.SECTION][Data.ALL][config[Data.SECTION][Data.CURRENT]]
    project = config[Project.SECTION][Project.CURRENT]

    tools_path = create_path([data_dir, project, 'tools'])

    files = [ root for root, _, files in os.walk(tools_path) ]
    files = [ os.path.split(f)[-1] for f in files[1:] ]
    if verbose:
        print 'Catagories:'
        for f in files:
            print '\t', f
    return files


def __show_tools__(verbose=True):
    config = __validate_config__()
    data_dir = config[Data.SECTION][Data.ALL][config[Data.SECTION][Data.CURRENT]]
    project = config[Project.SECTION][Project.CURRENT]

    tools_path = create_path([data_dir, project, 'tools'])

    print "Catagories"
    for root, d, files in os.walk(tools_path):
        catagory = os.path.split(root)[-1]
        if catagory != 'tools':
            print '\t', catagory
            files = [ f for f in files if not f.startswith('__') ]
            for f in files:
                print '\t\t', f


def __edit_tool__(pattern):
    config = __validate_config__()
    data_dir = config[Data.SECTION][Data.ALL][config[Data.SECTION][Data.CURRENT]]
    project = config[Project.SECTION][Project.CURRENT]

    tools_path = create_path([data_dir, project, 'tools'])
    regex = re.compile(pattern)

    tools = []
    append_tools = tools.append
    for root, d, files in os.walk(tools_path):
        files = [f for f in files if not f.startswith('__')]
        for f in files:
            if regex.search(f):
                append_tools(os.path.join(root, f))
    if not tools:
        print 'Did not find any tools matching the pattern', pattern
    else:
        if len(tools) == 1:
            __run_editor__(tools)
        else:
            print 'Found (', len(tools), ') matching the pattern "', pattern, '"'
            print 'Please choose:'
            print 'a - all'
            print 'q - cancel'
            for i, j in enumerate(tools):
                print i,'-', j

            choice = ''
            while choice not in ['a', 'q'] + [str(i) for i in range(len(tools))]:
                choice = raw_input('[ ')
                if choice == 'q':
                    print 'User aborted.'
                    exit()
                elif choice == 'a':
                    __run_editor__(tools)
                elif choice in [str(i) for i in range(len(tools))]:
                    __run_editor__([tools[int(choice)]])


def __show_catagories__():
    __get_catagories__()


def __list_tools__():
    __show_tools__()

def setup_arg_parser():
    '''
    Create the argument parser
    '''
    parser = argparse.ArgumentParser(description='Allows the user to view/create project specific tools.')

    parser.add_argument('-n', '--new', action='store', nargs = 2,  
                    dest='new', default=None, help='<catagory>, <name> creates a new project specific tool.')
    parser.add_argument('-ls', '--list', action='store_true',
                    dest='list_tools', help='List all tools.')
    parser.add_argument('-c', '--show_catagories', action='store_true', 
                    dest='show_catagories', help='Gives a list of all catagories available.')
    parser.add_argument('-e', '--edit', action='store', 
                    dest='edit', help='edit a tool.')
    return parser


def main(argv):
    '''
    '''
    parser = setup_arg_parser()
    options = parser.parse_args(argv)

    if not check_directory_status(True) or not check_project_status(True):
        exit()

    if options.new:
        __create_tool__(options.new[0], options.new[1])
    elif options.show_catagories:
        __show_catagories__()
    elif options.list_tools:
        __list_tools__()
    elif options.edit is not None:
        __edit_tool__(options.edit)


if __name__=='__main__':
    main(sys.argv[1:])
