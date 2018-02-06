__author__ = 'ThreatConnect (support@threatconnect.com)'
__version__ = '0.7.14'
__license__ = 'Apache License, Version 2'

try:
    from .tcex import TcEx
except ImportError as e:
    print('Error: {}'.format(e))
    print('Try running tc_lib')

from .tcex_local import TcExLocal
from .argparser import ArgParser
