# -*- coding: utf-8 -*-
"""TcEx Framework module init file."""
# flake8: noqa
from .__metadata__ import (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __package_name__,
    __url__,
    __version__,
)

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
