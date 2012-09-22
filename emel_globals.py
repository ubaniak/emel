'''
This file is used to store constants that are global to emel. 
'''
import os
# Config 
EMEL_CONFIG_FILE = os.getcwd() + os.sep + 'emel.conf'

class Data:
    SECTION = 'data'
    CURRENT = 'current'
    ALL = 'all'
    MARKER = '__data__.emel'

class Project:
    SECTION = 'project'
    CURRENT = 'current'
    MARKER = '__project__.emel'
    FILES = [ 'raw', 'processed', 'train' ]
