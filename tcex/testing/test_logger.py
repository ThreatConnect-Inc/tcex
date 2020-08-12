# -*- coding: utf-8 -*-
"""TcEx testing Framework."""
# standard library
import logging
import math
import os

from ..logger import RotatingFileHandlerCustom
from ..logger.trace_logger import TraceLogger


class TestLogger(TraceLogger):
    """Custom logger for test Case"""

    def data(self, stage, label, data, level='info'):
        """Log validation data in a specific format for test case.

        Args:
            stage (str): The stage of the test phase (e.g., setup, staging, run, validation, etc)
            label (str): The label for the provided data.
            data (str): The data to log.
            level (str, optional): The logging level to write the event. Defaults to 'info'.
        """
        stage = f'[{stage}]'
        stage_width = 25 - len(level)
        msg = f'{stage!s:>{stage_width}} : {label!s:<20}: {data!s:<50}'
        level = logging.getLevelName(level.upper())
        self.log(level, msg)

    def title(self, title, separator='-'):
        """Log validation data.

        Args:
            title (str): The title for the section of data to be written using data method.
            separator (str, optional): The value to use as a separator. Defaults to '-'.
        """
        separator = separator * math.ceil((100 - len(str(title))) / 2)
        self.log(logging.INFO, f'{separator} {title} {separator}')


# create logger based on custom TestLogger
logging.setLoggerClass(TestLogger)

# init logger
logger = logging.getLogger('TestCase')

# set logger level
logger.setLevel(logging.TRACE)

# create rotation filehandler
lfh = RotatingFileHandlerCustom(filename='log/tests.log')

# get logging level from OS env or default to debug
logging_level = logging.getLevelName(os.getenv('TCEX_TEST_LOGGING_LEVEL', 'debug').upper())

# set handler logging level
lfh.setLevel(logging_level)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
if logging_level < 10:
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        '(%(filename)s:%(funcName)s:%(lineno)d:%(threadName)s)'
    )

# set formatter
lfh.setFormatter(formatter)

# add handler
logger.addHandler(lfh)
