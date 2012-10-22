import sys
import argparse

def setup_arg_parser():
    '''
    Create the argument parser
    '''
    parser = argparse.ArgumentParser(description='')

    return parser


def main(argv):
    '''
    '''
    parser = setup_arg_parser()
    parser.parse_args(argv)

if __name__=='__main__':
    main(sys.argv[1:])
