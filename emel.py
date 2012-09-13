import sys
import imp
from glob import glob
import re
import os

def list_all_actions():
    allActions = {}

    emelInfo = imp.find_module('emel')
    emelModule = imp.load_module('emel', *emelInfo)

    files = glob('emel/*.py')

    moduleNames = [ os.path.splitext(os.path.split(f)[-1])[0] for f in files if not f.startswith('__') and not f.endswith('__.py') ]

    for moduleName in moduleNames:
        try:
            moduleInfo = imp.find_module(moduleName, emelModule.__path__)
            currModule = imp.load_module(moduleName, *moduleInfo)
            allActions[moduleName] = currModule

        except Exception as e:
            print 'Emel failed with errors:'
            print '{0} {1}'.format(type(e), str(e))
            exit(1)
    
    return allActions

def main(argv):
    '''
    '''
    if argv:
        actions = list_all_actions()
        if argv[0] not in actions:
            print '\tUnknown command "{0}"'.format(argv[0])
            print '\t please try'
            for action in actions:
                print '\t\t',action
            exit(1)

        else:
            actions[argv[0]].main(argv[1:])

if __name__ == '__main__':
    main(sys.argv[1:])


