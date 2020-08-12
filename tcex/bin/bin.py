#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework Bin Command Base Module."""
# standard library
import os
import sys

# third-party
import colorama as c

from ..app_config_object import InstallJson, LayoutJson, TcexJson
from ..app_config_object.permutations import Permutations


class Bin:
    """Base Class for ThreatConnect command line tools.

    Args:
        _args (namespace): The argparser args Namespace.
    """

    def __init__(self, _args):
        """Initialize Class properties.

        Args:
            _args (namespace): The argparser args Namespace.
        """
        self.args = _args

        # properties
        self.app_path = os.getcwd()
        self.exit_code = 0
        self.ij = InstallJson()
        self.lj = LayoutJson()
        self.permutations = Permutations()
        self.tj = TcexJson()

        # initialize colorama
        c.init(autoreset=True, strip=False)

    @staticmethod
    def handle_error(err, halt=True):
        """Print errors message and optionally exit.

        Args:
            err (str): The error message to print.
            halt (bool, optional): Defaults to True. If True the script will exit.
        """
        print(f'{c.Style.BRIGHT}{c.Fore.RED}{err}')
        if halt:
            sys.exit(1)

    @staticmethod
    def print_message(message, line_bright=False, line_color=None, line_limit=150):
        """Print the message ensuring lines don't exceed line limit."""
        bright = ''
        if line_bright:
            bright = c.Style.BRIGHT
        message_line = ''
        for word in message.split(' '):
            if len(message_line) + len(word) < line_limit:
                message_line += f'{word} '
            else:
                print(f'{bright}{line_color}{message_line.rstrip()}')
                message_line = f'{word} '
        print(f'{bright}{line_color}{message_line.rstrip()}')

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
