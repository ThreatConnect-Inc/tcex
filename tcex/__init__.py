# -*- coding: utf-8 -*-
"""TcEx Framework module init file."""
__author__ = 'ThreatConnect (support@threatconnect.com)'
__version__ = '1.0.4'
__license__ = 'Apache License, Version 2'
name = 'tcex'

try:
    from .tcex import TcEx  # noqa: F401
except ImportError as e:
    print('Error: {}'.format(e))
    print('Try running tclib')

from .tcex_argparser import TcExArgParser  # noqa: F401; pylint: disable=C0413
from .tcex_app_decorators import *  # noqa: F401,F403; pylint: disable=C0413

# import cli modules for bin commands
from .tcex_bin_init import TcExInit  # noqa: F401,F403; pylint: disable=C0413
from .tcex_bin_lib import TcExLib  # noqa: F401,F403; pylint: disable=C0413
from .tcex_bin_package import TcExPackage  # noqa: F401,F403; pylint: disable=C0413
from .tcex_bin_profile import TcExProfile  # noqa: F401,F403; pylint: disable=C0413
from .tcex_bin_run import TcExRun  # noqa: F401,F403; pylint: disable=C0413
from .tcex_bin_validate import TcExValidate  # noqa: F401,F403; pylint: disable=C0413
from .tcex_ti.tcex_ti import TcExTi  # noqa: F401,F403; pylint: disable=C0413
