# -*- coding: utf-8 -*-
"""TcEx Framework"""
__author__ = 'ThreatConnect (support@threatconnect.com)'
__version__ = '0.9.2'
__license__ = 'Apache License, Version 2'
name = 'tcex'

try:
    from .tcex import TcEx  # noqa: F401
except ImportError as e:
    print('Error: {}'.format(e))
    print('Try running tclib')

from .tcex_argparser import TcExArgParser  # noqa: F401; pylint: disable=C0413
from .tcex_app_decorators import *  # noqa: F401,F403; pylint: disable=C0413
