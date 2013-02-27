import imp
import sys
import argparse
from utils.path.pathhandler import emel_train_file_path, create_path, create_marker
from utils.path.pathhandler import emel_project_tools_file_path
from utils.settings.configobj import ConfigObj
from utils.userinput.userinput import yes_no_option
from emel.status import check_directory_status, check_project_status
from emel_globals import EMEL_CONFIG_FILE, Project, Data, INIT_MARKER

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
        config = __validate_config__()

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
    trainPath = emel_train_file_path()
    trainOrderPath = create_path([trainPath, TRAIN_ORDER_NAME])
    trainObjectPath = create_path([trainPath, TRAIN_OBJECT_NAME])

    train_order = imp.load_source('train_order', trainOrderPath)
    train_object = imp.load_source('train', trainObjectPath)

    train = train_object.Train()
    for function in train_order.order:
        getattr(train, function)(**train_order.args[function])

def setup_arg_parser():
    '''
    Create the argument parser
    '''
    parser = argparse.ArgumentParser(description='Sets up the train object.')

    parser.add_argument('-n', '--new', action='store_true',
                    dest='new', help='Create a new train object.')
    parser.add_argument('-r', '--run', action='store_true',
                    dest='run', help='Run the current train object.')
    return parser


def main(argv):
    '''
    '''
    if not check_directory_status(True):
        exit()
    if not check_project_status(True):
        exit()
    parser = setup_arg_parser()
    options = parser.parse_args(argv)

    if options.new:
        __create_train__()
    elif options.run:
        __run_train__()

if __name__=='__main__':
    main(sys.argv[1:])
