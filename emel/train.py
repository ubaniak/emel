import os
import imp
import sys
import argparse
import subprocess
from utils.path.pathhandler import emel_train_file_path, create_path, create_marker
from utils.path.pathhandler import emel_project_tools_file_path, create_dir
from utils.settings.configobj import ConfigObj
from utils.userinput.userinput import yes_no_option
from emel.status import check_directory_status, check_project_status
from emel.editor import __run__
from emel_globals import EMEL_CONFIG_FILE, Project, Data, INIT_MARKER
from emel_globals import BACKUP

from datetime import datetime

def __validate_config__():
    config = ConfigObj(EMEL_CONFIG_FILE)
    if Data.SECTION not in config: config[Data.SECTION] = {}
    if Data.CURRENT not in config[Data.SECTION]: config[Data.SECTION][Data.CURRENT] = ''
    if Data.ALL not in config[Data.SECTION]: config[Data.SECTION][Data.ALL] = {}
    if Project.SECTION not in config: config[Project.SECTION] = {}
    if Project.CURRENT not in config[Project.SECTION]: config[Project.SECTION][Project.CURRENT] = ''
    return config

TRAIN_TEMPLATE = """
import sys
# Add a path to project specific tools.
sys.path.append('{}')
import tools as project_tools

class Train(object):
    def gather_data(self):
        pass
    def pre_process(self):
        pass
    def train(self):
        pass
"""

TRAIN_ORDER_NAME = 'train_order.py'
TRAIN_OBJECT_NAME = 'train.py'

DEFAULT_TRAIN_LIST = ("order=['gather_data', 'pre_process', 'train']\n"
        "args={'gather_data':{},\n      'pre_process':{},\n      'train': {}}")


def __create_train__():
    message = ('[WARNING] This will destroy any existing train objects. Continue?')
    go = yes_no_option(message)
    if go:
        trainPath = emel_train_file_path()
        train_object = TRAIN_TEMPLATE.format(emel_project_tools_file_path())

        print 'Creating default train order ...',
        with open(create_path([trainPath, TRAIN_ORDER_NAME]), 'w') as fp:
            fp.write(DEFAULT_TRAIN_LIST)
        print 'Done.'

        print 'Creating train object ...',
        with open( create_path([trainPath, TRAIN_OBJECT_NAME]), 'w' ) as fp:
            fp.write(train_object)
        create_marker( trainPath, INIT_MARKER )
        print 'Done.'
    else:
        print 'Aborting'


def __run_train__():
    config = __validate_config__()
    trainPath = emel_train_file_path()

    # Create a backup train folder
    folderName = datetime.now().strftime('Train_%Y%m%dT%H%M%S')
    print 'Creating backup folder "{}" ...'.format(folderName),
    backupPath = create_dir(create_path([trainPath, folderName]))
    print 'Done.'
    
    if backupPath:
        config[BACKUP] = backupPath
        trainOrderPath = create_path([trainPath, TRAIN_ORDER_NAME])
        trainObjectPath = create_path([trainPath, TRAIN_OBJECT_NAME])

        # copy over the train order and train object files.
        print 'Backing up the train order ...'
        subprocess.call(['cp', trainOrderPath, backupPath])
        print 'Done.'
        print 'Backing up train object ...'
        subprocess.call(['cp', trainObjectPath, backupPath])
        print 'Done.'

        train_order = imp.load_source('train_order', trainOrderPath)
        train_object = imp.load_source('train', trainObjectPath)

        train = train_object.Train()
        f = open(create_path([backupPath, 'time.txt']), 'w')
        for function in train_order.order:
            print 'Running', function
            start = datetime.now()
            getattr(train, function)(**train_order.args[function])
            f.write('Function "{}" (Took: {})\n'.format(function, datetime.now() - start))
        f.close()
    else:
        print '[ERROR] Could not create backup train folder.'


def __list_order__():
    trainPath = emel_train_file_path()
    trainOrderPath = create_path([trainPath, TRAIN_ORDER_NAME])
    trainObjectPath = create_path([trainPath, TRAIN_OBJECT_NAME])

    if not os.path.exists(trainOrderPath) or not os.path.exists(trainObjectPath):
        print '[ERROR] the train object is not properly set up.'
        print 'please run train -n'
        exit()

    train_order = imp.load_source('train_order', trainOrderPath)
    for function in train_order.order:
        print function


def __edit_train__():
    trainPath = emel_train_file_path()
    trainOrderPath = create_path([trainPath, TRAIN_ORDER_NAME])
    trainObjectPath = create_path([trainPath, TRAIN_OBJECT_NAME])

    if not os.path.exists(trainOrderPath):
        print '[ERROR] Could not find {}.'.format(TRAIN_ORDER_NAME)
        print 'please run train -n first.'

    if not os.path.exists(trainObjectPath):
        print '[ERROR] Could not find {}.'.format(TRAIN_OBJECT_NAME)
        print 'please run train -n first.'

    __run__([trainOrderPath, trainObjectPath])


def setup_arg_parser():
    '''
    Create the argument parser
    '''
    parser = argparse.ArgumentParser(description='Sets up the train object.')

    parser.add_argument('-n', '--new', action='store_true',
                    dest='new', help='Create a new train object.')
    parser.add_argument('-r', '--run', action='store_true',
                    dest='run', help='Run the current train object.')
    parser.add_argument('-e', '--edit', action='store_true',
                    dest='edit', help='Open the train object/order in the chosen editor')
    parser.add_argument('--list-order', action='store_true',
                    dest='list_order', help='Shows the order of the functions wich will be run.')
    return parser


def main(argv):
    '''
    '''
    parser = setup_arg_parser()
    if not check_directory_status(True):
        exit()
    if not check_project_status(True):
        exit()
    options = parser.parse_args(argv)

    if options.new:
        __create_train__()
    elif options.run:
        __run_train__()
    elif options.list_order:
        __list_order__()
    elif options.edit:
        __edit_train__()

if __name__=='__main__':
    main(sys.argv[1:])
