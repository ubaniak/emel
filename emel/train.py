import sys
import argparse
from utils.path.pathhandler import emel_train_file_path, create_path, create_marker
from utils.path.pathhandler import emel_project_tools_file_path
from utils.settings.configobj import ConfigObj
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

class Train(object):
    def gather_data(self):
        pass
    def pre_process(self):
        pass
    def train(self):
        pass
"""

def __create_train__():
    config = __validate_config__()

    trainPath = emel_train_file_path()
    print emel_project_tools_file_path()

    print 'Creating train object ...',
    with open( create_path([trainPath, 'train.py']), 'w' ) as fp:
        fp.write(TRAIN_TEMPLATE)
    create_marker( trainPath, INIT_MARKER )
    print 'Done.'

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
    parser = setup_arg_parser()
    options = parser.parse_args(argv)

    if options.new:
        __create_train__()

if __name__=='__main__':
    main(sys.argv[1:])
