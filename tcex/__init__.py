import os
import sys
import inspect

__author__ = 'ThreatConnect (support@threatconnect.com)'
__version__ = '0.0.4'
__license__ = 'Apache License, Version 2'

# For Apps Append the '/lib' directory
lib_path = os.path.join(os.getcwd(), 'lib')

for root, dirs, files in os.walk(lib_path):
    while len(dirs) > 0:
        sys.path.insert(1, '%s/%s' % (lib_path, dirs.pop()))

try:
    from tcex import TcEx
except ImportError as e:
    print('Error: {}'.format(e))
    print('Try app.py --lib')

from tcex_local import TcExLocal
from argparser import ArgParser