import os
import sys
import argparse
import subprocess
from utils.settings.configobj import ConfigObj
from utils.userinput.userinput import yes_no_option
from emel_globals import EMEL_CONFIG_FILE, Editor


def __validate_config__():
    config = ConfigObj(EMEL_CONFIG_FILE)
    if Data.SECTION not in config: config[Data.SECTION] = {}
    if Data.CURRENT not in config[Data.SECTION]: config[Data.SECTION][Data.CURRENT] = ''
    if Data.ALL not in config[Data.SECTION]: config[Data.SECTION][Data.ALL] = {}
    if Project.SECTION not in config: config[Project.SECTION] = {}
    if Project.CURRENT not in config[Project.SECTION]: config[Project.SECTION][Project.CURRENT] = ''
    return config


def __set__(editor):
    pass

def __run__(files):
    pass

def __show__():
    pass

def setup_arg_parser():
    '''
    Create the argument parser
    '''
    parser = argparse.ArgumentParser(description='Sets up the train object.')

    parser.add_argument('--set', action='store', default=None,
                    dest='set', help='Set the editor.')
    parser.add_argument('-r', '--run', action='store', default=[], nargs='*',
                    dest='run', help='Run the current train object.')
    parser.add_argument('--which', action='store_true',
                    dest='which', help='Shows the default editor.')
    return parser


def main(argv):
    '''
    '''
    parser = setup_arg_parser()
    options = parser.parse_args(argv)

    if options.set:
        __set__(options.set)
    elif options.run:
        __run__(options.run)
    elif options.which:
        __show__()

if __name__=='__main__':
    main(sys.argv[1:])
