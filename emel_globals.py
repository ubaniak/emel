'''
This file is used to store constants that are global to emel. 
'''
import os
# Config 
EMEL_CONFIG_FILE = os.path.join(os.getcwd(), 'emel.conf')
EMEL_UTILS_FILE = os.path.join(os.getcwd(), 'utils')
INIT_MARKER = '__init__.py'

class Data:
    SECTION = 'data'
    CURRENT = 'current'
    ALL = 'all'
    MARKER = '__data__.emel'

class Project:
    SECTION = 'project'
    CURRENT = 'current'
    MARKER = '__project__.emel'
    FILES = [ 'raw', 'processed', 'train', 'tools' ]
