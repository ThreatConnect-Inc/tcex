# -*- coding: utf-8 -*-
"""TcEx Framework module init file."""
__author__ = 'ThreatConnect (support@threatconnect.com)'
__version__ = '2.0.0'
__license__ = 'Apache License, Version 2'
name = 'tcex'

# flake8: noqa
try:
    from .tcex import TcEx
    from .decorators import (
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
    from .tcex_ti.tcex_ti import TcExTi
except ImportError as e:
    print(f'Error: {e}')
    print('Try running tclib')
