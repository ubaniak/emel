import sys
import argparse
import os
from utils.settings.configobj import ConfigObj

def Initialize_emel(options):
    '''
    Sets the location of the data directory in the emel.config file.
    '''

    # 1. create the data directory
    dataDir = options.location + os.sep + 'Data'
    if not os.path.isdir(dataDir):
        print 'Creatint Data folder at', dataDir
        os.makedirs(dataDir)
    else:
        print 'Directory', dataDir, 'allready exists'

    config = ConfigObj()
    config.filename = os.getcwd() + os.sep + 'emel.conf'
    config['core'] = {}
    config['core']['dataDir'] = dataDir

    config.write()

    

def setup_arg_parser():
    '''
    Create the argument parser
    '''
    parser = argparse.ArgumentParser(description='This module sets the location of the emel Data directory.')

    parser.add_argument('-l', '--location', action='store',  
                    dest='location', default=os.getcwd(), help='Sets the location of the data directory. Defaults to the current working directory.')
    return parser


def main(argv):
    '''
    '''
    parser = setup_arg_parser()
    options = parser.parse_args(argv)
    Initialize_emel(options)


if __name__=='__main__':
    main(sys.argv[1:])
