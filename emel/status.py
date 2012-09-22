import sys
import argparse
import os
from utils.settings.configobj import ConfigObj

EMEL_CONFIG_FILE = os.getcwd() + os.sep + 'emel.conf'

def check_directory_status(verbose=False):

    config = ConfigObj(EMEL_CONFIG_FILE)
    try:
        cd = config['data']['current']
        if not cd: raise KeyError
        if verbose: print 'Current data directory set to "{0}"\n'.format(cd) 
    except KeyError as e:
        if verbose: print '[WARNING] Current data directory not set.'
        if verbose: print 'please run emel data -h for more help\n'
        return False
    return True


def check_project_status(verbose=False):

    config = ConfigObj(EMEL_CONFIG_FILE)
    try:
        cp = config['project']['current']
        if not cp: raise KeyError
        if verbose: print 'Current project set to "{0}"\n'.format(cp)
    except KeyError as e:
        if verbose: print '[WARNING] Current project not set.'
        if verbose: print 'please run emel project -h for more help\n'
        return False

    return True


def __check_status__():
    '''
    Looks in to the emel.conf file and makes sure the current project and 
    the current data directory is set.
    '''
    check_directory_status(True)
    check_project_status(True)


def setup_arg_parser():
    '''
    Create the argument parser
    '''
    parser = argparse.ArgumentParser(description='Checks the status of your emel project.')
    return parser


def main(argv):
    '''
    '''
    parser = setup_arg_parser()
    options = parser.parse_args(argv)
    __check_status__()


if __name__=='__main__':
    main(sys.argv[1:])
