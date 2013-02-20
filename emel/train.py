import sys
import argparse

def __validate_config__():
    config = ConfigObj(EMEL_CONFIG_FILE)
    if Data.SECTION not in config: config[Data.SECTION] = {}
    if Data.CURRENT not in config[Data.SECTION]: config[Data.SECTION][Data.CURRENT] = ''
    if Data.ALL not in config[Data.SECTION]: config[Data.SECTION][Data.ALL] = {}
    if Project.SECTION not in config: config[Project.SECTION] = {}
    if Project.CURRENT not in config[Project.SECTION]: config[Project.SECTION][Project.CURRENT] = ''
    return config

train_object_template = """
class Trein(object):
    def gather_data(self):
        pass
    def pre_process(self):
        pass
    def train(self):
        pass
"""

def __create_train__():
    config = __validate_config__()

    fp = open( create_path(['train.py']), 'w' )
    fp.write( TOOL_TEMPLATE.format(tool_name, re.sub('\\\\', '/', new_cat_path)) )
    fp.close()
    pass

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
