import sys
import argparse
import os

from utils.settings.configobj import ConfigObj
from utils.path.pathhandler import create_dir, create_path, create_marker
from utils.path.pathhandler import emel_tools_file_path, emel_raw_file_path
from utils.path.pathhandler import emel_processed_file_path, emel_train_file_path
from emel.status import check_directory_status, check_project_status
from emel_globals import EMEL_CONFIG_FILE, Project, Data, INIT_MARKER


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
                print '  #   *','(',project,')'
            else:
                print '  #    ','(',project,')'
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

    config[Project.SECTION][Project.CURRENT] = newProject
    config.write()
    
    dataDir = config[Data.SECTION][Data.CURRENT] 
    projectDir = create_path([dataDir, newProject])
    create_dir(projectDir)
    create_marker( projectDir, Project.MARKER )
    create_marker( projectDir, INIT_MARKER )

    # Create all nessesary folders.
    create_dir(emel_raw_file_path(), verbose=True)
    create_dir(emel_processed_file_path(), verbose=True)
    create_dir(emel_train_file_path(), verbose=True)
    create_dir(emel_tools_file_path(), verbose=True)

    # Create nessesary tool dirs in the project/tools folder.
    create_marker(emel_tools_file_path(), '__init__.py')
 
    print '"{0}" Successfully created.'.format(newProject)


def __change_project__(project):
    config = __validate_config__()
    if project not in __list_projects__():
        print '"{0}" not found'.format(project)
    else:
        config[Project.SECTION][Project.CURRENT] = project
        config.write()


def setup_arg_parser():
    '''
    Create the argument parser
    '''
    parser = argparse.ArgumentParser(description='Manage all projects in the data directory')

    parser.add_argument('-n', '--new', action='store',  
                    dest='new', default=None, help='creates a new project.')
    parser.add_argument('-ls', '--list', action='store_true', 
                    dest='listProjs', help='List all projects')
    parser.add_argument('-cp', '--change_project', action='store', 
                    dest='change_project', default=None, help='Change the current project')
    return parser


def main(argv):
    '''
    '''
    if not argv:
        check_project_status(True)
    else:
        parser = setup_arg_parser()
        options = parser.parse_args(argv)
        if not check_directory_status(True):
            exit()

        if options.new:
            __new_project__(options.new)
        elif options.listProjs:
            __list_projects__(verbose=True)
        elif options.change_project is not None:
            __change_project__(options.change_project)


if __name__=='__main__':
    main(sys.argv[1:])
