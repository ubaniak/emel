import argparse
import sys
import os

def evaluate_init_args(args):
    print args

def setup_argument_parser():
    parser = argparse.ArgumentParser("Emel framework")
    subparsers = parser.add_subparsers(dest="commands",
                                       description='list of reconized commands')

    # -- init --------------
    init = subparsers.add_parser('init', help='')

    init.add_argument('path', type=str, nargs='?', default=None,
            help = 'path to folder to create an emel project')
    init.set_defaults(func=evaluate_init_args)
    pass

    return parser


if __name__=='__main__':
    parser = setup_argument_parser()
    arguments = parser.parse_args(sys.argv[1:])
    arguments.func(arguments)
