#!/usr/bin/env python
"""TcEx Framework Bin Command Base Module."""
# standard library
import logging
import os
import sys
from abc import ABC
from pathlib import Path
from typing import Optional

# third-party
import typer
from click import Choice

# first-party
from tcex.app_config.install_json import InstallJson
from tcex.app_config.layout_json import LayoutJson
from tcex.app_config.tcex_json import TcexJson
from tcex.backports import cached_property
from tcex.logger.rotating_file_handler_custom import (  # pylint: disable=no-name-in-module
    RotatingFileHandlerCustom,
)
from tcex.logger.trace_logger import TraceLogger  # pylint: disable=no-name-in-module
from tcex.utils.utils import Utils


class BinABC(ABC):
    """Base Class for ThreatConnect command line tools."""

    def __init__(self):
        """Initialize Class properties."""
        # properties
        self.app_path = os.getcwd()
        self.exit_code = 0
        self.i1 = ' ' * 4  # indent level 1
        self.i2 = ' ' * 8  # indent level 2
        self.i3 = ' ' * 12  # indent level 3
        self.ij = InstallJson()
        self.lj = LayoutJson()
        self.tj = TcexJson()
        self.utils = Utils()

    @cached_property
    def cli_out_path(self) -> 'Path':  # pylint: disable=no-self-use
        """Return the path to the tcex cli command out directory."""
        _out_path = Path(os.path.expanduser('~/.tcex'))
        _out_path.mkdir(exist_ok=True, parents=True)
        return _out_path

    @staticmethod
    def handle_error(err, halt: Optional[bool] = True):
        """Print errors message and optionally exit.

        Args:
            err (str): The error message to print.
            halt (bool, optional): Defaults to True. If True the script will exit.
        """
        typer.secho(err, fg=typer.colors.RED, err=True)
        if halt:
            sys.exit(1)

    @cached_property
    def log(self) -> 'logging.Logger':
        """Return the configured logger."""
        # create logger based on custom TestLogger
        logging.setLoggerClass(TraceLogger)

        # init logger
        logger = logging.getLogger('tcex-cli')

        # set logger level
        logger.setLevel(logging.TRACE)  # pylint: disable=no-member

        # create rotation filehandler
        lfh = RotatingFileHandlerCustom(
            backupCount=3,
            filename=f'{self.cli_out_path}/tcex.log',
            maxBytes=100_000,
        )

        # get logging level from OS env or default to debug
        logging_level = logging.getLevelName('DEBUG')

        # set handler logging level
        lfh.setLevel(logging_level)

        # create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s ' '(%(filename)s:%(lineno)d)'
        )
        if logging_level < 10:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                '(%(filename)s:%(funcName)s:%(lineno)d:%(threadName)s)'
            )

        # set formatter
        lfh.setFormatter(formatter)

        # add handler
        logger.addHandler(lfh)

        return logger

    @staticmethod
    def print_block(text: str, max_length: Optional[int] = 80, **kwargs):
        """Print Divider."""
        bold = kwargs.get('bold', False)
        fg_color = getattr(typer.colors, kwargs.get('fg_color', 'white').upper())

        # split text
        text_wrapped = ''
        for word in text.split(' '):
            if len(text_wrapped) + len(word) < max_length:
                text_wrapped += f'{word} '
            else:
                typer.secho(text_wrapped, fg=fg_color, bold=bold)
                text_wrapped = f'{word} '
        typer.secho(text_wrapped, fg=fg_color, bold=bold)

    @staticmethod
    def print_divider(char: Optional[str] = '-', count: Optional[int] = 100, **kwargs):
        """Print Divider."""
        bold = kwargs.get('bold', False)
        fg_color = getattr(typer.colors, kwargs.get('fg_color', 'bright_white').upper())

        # print divider
        typer.secho(char * count, fg=fg_color, bold=bold)

    @staticmethod
    def print_failure(message: str, exit_: Optional[bool] = True):
        """Print Failure."""
        typer.secho(message, fg=typer.colors.RED, bold=True)
        if exit_ is True:
            sys.exit(1)

    @staticmethod
    def print_setting(label: str, value: str, **kwargs):
        """Print Setting."""
        bold = kwargs.get('bold', True)
        fg_color = getattr(typer.colors, kwargs.get('fg_color', 'magenta').upper())
        indent = ' ' * kwargs.get('indent', 0)

        # print setting
        value_display = typer.style(f'{value}', fg=fg_color, bold=bold)
        typer.echo(f'{indent}{label:<20}: {value_display}')

    @staticmethod
    def print_title(title: str, divider: Optional[bool] = True, **kwargs):
        """Print Title."""
        bold = kwargs.get('bold', True)
        fg_color = getattr(typer.colors, kwargs.get('fg_color', 'cyan').upper())

        # print title
        typer.secho(title, fg=fg_color, bold=bold)
        if divider is True:
            typer.secho('=' * len(title), fg=fg_color, bold=bold)

    @staticmethod
    def prompt_choice(text: str, choices: list, default: str, **kwargs) -> bool:
        """Present a prompt with a bool response."""
        bold = kwargs.get('bold', True)
        fg_color = getattr(typer.colors, kwargs.get('fg_color', 'cyan').upper())

        text = typer.style(f'{text}', fg=fg_color, bold=bold)
        choice = Choice(choices)

        return typer.prompt(
            text=text,
            default=default,
            type=choice,
        )

    @staticmethod
    def update_system_path():
        """Update the system path to ensure project modules and dependencies can be found."""
        cwd = os.getcwd()
        lib_dir = os.path.join(os.getcwd(), 'lib_')
        lib_latest = os.path.join(os.getcwd(), 'lib_latest')

        # insert the lib_latest directory into the system Path if no other lib directory found. This
        # entry will be bumped to index 1 after adding the current working directory.
        if not [p for p in sys.path if lib_dir in p]:
            sys.path.insert(0, lib_latest)

        # insert the current working directory into the system Path for the App, ensuring that it is
        # always the first entry in the list.
        try:
            sys.path.remove(cwd)
        except ValueError:
            pass
        sys.path.insert(0, cwd)
