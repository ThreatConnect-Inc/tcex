# -*- coding: utf-8 -*-
"""TcEx Framework module init file."""
__author__ = 'ThreatConnect (support@threatconnect.com)'
__version__ = '1.1.5'
__license__ = 'Apache License, Version 2'
name = 'tcex'

# flake8: noqa
try:
    from .tcex import TcEx
except ImportError as e:
    print('Error: {}'.format(e))
    print('Try running tclib')

from .decorators import (  # pylint: disable=wrong-import-position
    Benchmark,
    Debug,
    FailOnInput,
    FailOnOutput,
    IterateOnArg,
    OnException,
    OnSuccess,
    Output,
    ReadArg,
    WriteOutput,
)
from .tcex_ti.tcex_ti import TcExTi  # pylint: disable=wrong-import-position
