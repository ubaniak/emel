import sys
import argparse
import os

from utils.settings.configobj import ConfigObj
from utils.path.pathhandler import create_dir, create_path, create_marker
from utils.userinput.userinput import yes_no_option
from emel.status import check_directory_status 
from emel_globals import EMEL_CONFIG_FILE, Project, Data


# TODO: delete projects.
def __validate_config__():
    config = ConfigObj(EMEL_CONFIG_FILE)
    if Project.SECTION not in config: config[Project.SECTION] = {}
    if Project.CURRENT not in config[Project.SECTION]: config[Project.SECTION][Project.CURRENT] = ''
    return config


def __list_projects__(verbose=False):
    '''
    Looks in to the data directory and gets a list of all projects.
    '''
    config = __validate_config__()
    location = config[Data.SECTION][Data.CURRENT]
    files = [ root for root, _, files in os.walk(location) if Project.MARKER in files ]
    projects = [ os.path.split(f)[-1] for f in files ]
    projects.sort()
    
    if not projects and verbose:
        print 'There are no projects in "'+ config[Data.SECTION][Data.CURRENT] + '"'
    elif verbose:
        print 'All Projects:'
        i = 0
        for project in projects:
            project = os.path.split(project)[-1] 
            if project == config[Project.SECTION][Project.CURRENT]:
                print '  #   *','(',i,')',project
            else:
                print '  #    ','(',i,')',project
            i += 1
    return projects


def __new_project__(newProject):
    '''
    Creates a new project in the current data directory.
    '''
    config = __validate_config__()
    
    if newProject in __list_projects__():
        print '"', newProject, '" allready exists'
        exit()
    
    dataDir = config[Data.SECTION][Data.CURRENT] 
    projectDir = create_path([dataDir, newProject])
    create_dir(projectDir)
    create_marker( projectDir, Project.MARKER )

    for fileType in Project.FILES:
        newDir = create_path([projectDir, fileType])
        create_dir( newDir, verbose=True )

    config[Project.SECTION][Project.CURRENT] = newProject
    config.write()
    print '"{0}" Successfully created.'.format(newProject)


def __change_project__(n):
    config = __validate_config__()
    i = 0
    for project in __list_projects__():
        if i == n: 
            print 'Changing current directory to "{0}"'.format(project)
            config[Project.SECTION][Project.CURRENT] = project
            config.write()
            break
        i += 1

def setup_arg_parser():
    '''
    Create the argument parser
    '''
    parser = argparse.ArgumentParser(description='Manage all projects in the data directory')

    parser.add_argument('-n', '--new', action='store',  
                    dest='new', default=None, help='creates a new project.')
    parser.add_argument('-ls', '--list', action='store_true', 
                    dest='listProjs', help='List all projects')
    parser.add_argument('-cp', '--change_project', action='store', type=int, 
                    dest='change_project', default=None, help='Change the current project')
    return parser


def main(argv):
    '''
    '''
    if not check_directory_status(True):
        exit()

    parser = setup_arg_parser()
    options = parser.parse_args(argv)

    if options.new:
        __new_project__(options.new)
    elif options.listProjs:
        __list_projects__(verbose=True)
    elif options.change_project is not None:
        __change_project__(options.change_project)


if __name__=='__main__':
    main(sys.argv[1:])
