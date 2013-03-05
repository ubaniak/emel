from utils.settings.configobj import ConfigObj
from utils.userinput.userinput import yes_no_option
from emel.status import check_directory_status, check_project_status
from emel_globals import EMEL_CONFIG_FILE, Data, Project

from glob import glob
import os


def create_dir(directory, interactive=False, force=False, verbose=False):
    '''
    creates a new directory if one does not already exist.
    directory, the path to where you want to create the directory
    interactive, if a directory already exists, ask the user if they want to create a directory with the same name
                but with a (i) next to it.
    force, same as interactive but does not ask the user. 
    '''
    if not os.path.isdir(directory):
        if verbose: print 'Creating "{0}"'.format(directory)
        os.makedirs(directory)
        return directory
    else:
        verbose = force or interactive if force or interactive else verbose
        if verbose: print 'Directory "{0}" already exists'.format(directory)
        newDirectoryFormat='{0}({1})'
        if interactive or force:
            i = 1
            while os.path.isdir( newDirectoryFormat.format(directory, i) ): 
                print 'Directory "{0}" already exists'.format(newDirectoryFormat.format(directory, i))
                i += 1

            newDirectory = newDirectoryFormat.format(directory, i)
            
            choice = yes_no_option('Would you like to create "{0}"?'.format(newDirectory)) if interactive else True

            if choice:
                if verbose: print 'Creating "{0}"'.format(newDirectory)
                os.makedirs(newDirectory)
                return newDirectory
            else:
                print 'emel failed to create "{0}"'.format(directory)
        else:
            print 'emel failed to create "{0}"'.format(directory)

        return None


def create_path(paths):
    return os.sep.join(paths)


def create_marker(path, marker):
    '''
    This function places a __<???>__.emel file in a folder
    in order to mark it as an emel directory
    '''
    with open( os.sep.join([path, marker]), 'w') as f: f.close()

def __get_emel_file_path__(fileType):
    if fileType.lower() not in Project.FILES: raise TypeError( 'unknown file type {}. Only use {}'.format(fileType, ','.join(Project.FILES)) )
    
    config = ConfigObj(EMEL_CONFIG_FILE)
    
    if not check_directory_status(): exit(1)
    if not check_project_status(): exit(1)

    currData = config[Data.SECTION][Data.CURRENT] 
    dataDir = config[Data.SECTION][Data.ALL][currData]
    project = config[Project.SECTION][Project.CURRENT]
    return create_path( [dataDir, project,  fileType] )

def emel_raw_file_path():
    return __get_emel_file_path__('data/raw')

def emel_processed_file_path():
    return __get_emel_file_path__('data/processed')

def emel_train_file_path():
    return __get_emel_file_path__('train')

def emel_project_tools_file_path():
    return __get_emel_file_path__('tools')

def emel_project_path():
    config = ConfigObj(EMEL_CONFIG_FILE)
    dataDir = config[Data.SECTION][Data.CURRENT] 
    project = config[Project.SECTION][Project.CURRENT]
    return create_path([dataDir, project])
