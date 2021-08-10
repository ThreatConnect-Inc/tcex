"""TcEx Framework module init file."""
import logging

from tcex.logger import TraceLogger

# init tcex logger
logging.setLoggerClass(TraceLogger)
logger = logging.getLogger('tcex')
logger.setLevel(logging.TRACE)  # pylint: disable=E1101

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
    from .decorators import (
        Benchmark,
        Debug,
        FailOnOutput,
        IterateOnArg,
        OnException,
        OnSuccess,
        Output,
        ReadArg,
        WriteOutput,
    )
    from .tcex import TcEx
    from .threat_intelligence import ThreatIntelligence
except ImportError as e:
    print(f'Error: {e}')
    print('Try running tclib')
