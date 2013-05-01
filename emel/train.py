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
from emel.editor import __run_editor__
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

DEFAULT_TRAIN_LIST = ("description='Please give an explanation of your expiriment here.'\n"
        "order=['gather_data', 'pre_process', 'train']\n"
        "args={'gather_data':{},\n      'pre_process':{},\n      'train': {}}")


TRAIN_BKUP_TEMPlATE = 'Train_%Y%m%d_%H%M%S'





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
    folderName = datetime.now().strftime(TRAIN_BKUP_TEMPlATE)
    backupPath = create_dir(create_path([trainPath, folderName]))
    print 'Creating backup folder "{}" ...'.format(backupPath),
    print 'Done.'
    
    if backupPath:
        config[BACKUP] = backupPath
        trainOrderPath = create_path([trainPath, TRAIN_ORDER_NAME])
        trainObjectPath = create_path([trainPath, TRAIN_OBJECT_NAME])

        # copy over the train order and train object files.
        print 'Backing up the train order ...',
        subprocess.call(['cp', trainOrderPath, backupPath])
        print 'Done.'
        print 'Backing up train object ...',
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

def __edit_train__(which=None):
    if not which or which == 'current':
        __edit_current_train__()
    elif which == 'older':
        __edit_older_train__()

def __edit_current_train__(show='both'):
    trainPath = emel_train_file_path()
    trainOrder = create_path([trainPath, TRAIN_ORDER_NAME])
    trainObject = create_path([trainPath, TRAIN_OBJECT_NAME])

    if not os.path.exists(trainOrder):
        print '[ERROR] Could not find {}.'.format(TRAIN_ORDER_NAME)
        print 'please run train -n first.'

    if not os.path.exists(trainObject):
        print '[ERROR] Could not find {}.'.format(TRAIN_OBJECT_NAME)
        print 'please run train -n first.'

    to_open = []
    if show == 'both':
        to_open = [trainOrder, trainObject]
    if show == 'order':
        to_open = [trainOrder]
    if show == 'object':
        to_open = [trainObject]

    __run_editor__(to_open)


def __edit_older_train__():
    trainPath = emel_train_file_path()

    all_files = os.listdir(trainPath)
    all_files = [f for f in all_files if f.startswith('Train_')]

    print 'Please choos a folder to edit.'
    print '\tq - quit'
    for i, j in enumerate(all_files):
        print '\t', i, '-',j 

    choice = ''
    valid_choices = ['q'] + [str(i) for i in range(len(all_files))]
    while choice not in valid_choices:
        choice = raw_input('[ ')
        if choice == 'q':
            print 'User aborted'
            exit()
        elif choice in [str(i) for i in range(len(all_files))]:
            choice = int(choice)
            trainOrder = os.path.join(trainPath, all_files[choice], TRAIN_ORDER_NAME)
            trainObject = os.path.join(trainPath, all_files[choice], TRAIN_OBJECT_NAME)
            
            __run_editor__([trainOrder, trainObject])
            exit()
        else:
            print 'Invalid choice.'


def __ls_train__(which=None):
    if not which or which == 'current':
        __list_current_train__()
    elif which == 'older':
        __list_older_train__()


def __list_current_train__():
    trainPath = emel_train_file_path()
    trainOrderPath  = create_path([trainPath, TRAIN_ORDER_NAME])

    if not os.path.exists(trainOrderPath):
        print '[ERROR] the train object is not properly set up.'
        print 'please run train -n'
        exit()

    train_order = imp.load_source('train_order', trainOrderPath)
    print '"{}"'.format(train_order.description)
    for function in train_order.order:
        print '\t', function


def __list_older_train__():
    trainPath = emel_train_file_path()

    all_files = os.listdir(trainPath)
    all_files = [f for f in all_files if f.startswith('Train_')]
    if not all_files:
        print 'No older train runs.'
        exit()

    print 'Older train files:'
    for i in all_files:
        trainOrderPath = os.path.join(trainPath, i, TRAIN_ORDER_NAME)
        train_order = imp.load_source('train_order', trainOrderPath)
        print os.path.join(trainPath, i)
        print '\t', '"{}"'.format(train_order.description)
        for function in train_order.order:
            print '\t\t', function


def setup_arg_parser():
    '''
    Create the argument parser
    '''
    parser = argparse.ArgumentParser(description='Sets up the train object.')

    parser.add_argument('-n', '--new', action='store_true',
                    dest='new', help='Create a new train object.')
    parser.add_argument('-r', '--run', action='store_true',
                    dest='run', help='Run the current train object.')
    parser.add_argument('-e', '--edit', action='store', default='donotuse', nargs='?',
                    dest='edit', help='Open the train object/order in the chosen editor')
    parser.add_argument('-ls', '--list', action='store', type=str, default='donotuse', nargs='?', 
                    dest='list_', help='List either the current or older train fils.')
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
    elif options.edit != 'donotuse':
        __edit_train__(options.edit)
    elif options.list_ != 'donotuse':
        __ls_train__(options.list_)


if __name__=='__main__':
    main(sys.argv[1:])
