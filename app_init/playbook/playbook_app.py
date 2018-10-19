# -*- coding: utf-8 -*-
""" Playbook App Template. """
from args import Args

# Typically no changes are required to this file.


class PlaybookApp(object):
    """String Operation App"""

    def __init__(self, _tcex):
        """ Initialize class properties. """
        self.tcex = _tcex
        self.args = None
        self.exit_message = 'Success'

    def parse_args(self):
        """ Parse CLI args. """
        Args(self.tcex)
        self.args = self.tcex.args

    def run(self):
        """ Run the App main logic. """
        self.tcex.log.info('No run logic provided.')

    def write_output(self):
        """ Write the Playbook output variables. """
        self.tcex.log.info('No output variables written.')
