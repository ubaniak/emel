import sys
import imp
from glob import glob
import re

def list_all_actions():
    info = imp.find_module('emel')
    module = imp.load_module('emel', *info)

    files = glob('emel/*.py')


    


def main(argv):
    '''
    '''


if __name__ == '__main__':
    main(sys.argv[1:])


