import sys
import imp
from glob import glob
import re
import os
import inspect


def trace_errors(e):
    print '{0} {1}'.format(type(e), str(e))
    for i in inspect.trace()[1:]:
        frameInfo = inspect.getframeinfo(i[0])
        #print frameInfo
        print '\t"{1}": {0}'.format(frameInfo.lineno,frameInfo.filename)
        print '\t\t({0})'.format(', '.join([ c.strip() for c in frameInfo.code_context ]))
        

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
            trace_errors(e)
            exit(1)
    
    return allActions


def main(argv):
    '''
    '''
    try:
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
    except Exception as e:
        trace_errors(e)

if __name__ == '__main__':
    main(sys.argv[1:])


