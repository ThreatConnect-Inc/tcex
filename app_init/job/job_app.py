# -*- coding: utf-8 -*-
""" Job App Template. """
from args import Args

# Typically no changes are required to this file.


class JobApp(object):
    """ Get the owners and indicators in the given owner. """

    def __init__(self, _tcex):
        """ Initialize class properties. """
        self.tcex = _tcex
        self.args = None
        self.exit_message = 'Success'

    def done(self):
        """ Perform cleanup operations and gracefully exit the App. """
        self.tcex.log.debug('Running done.')

    def parse_args(self):
        """ Parse CLI args. """
        Args(self.tcex)
        self.args = self.tcex.args

    def run(self):
        """ Run the App main logic. """
        self.tcex.log.info('No run logic provided.')

    def start(self):
        """ Perform prep/startup operations. """
        self.tcex.log.debug('Running start.')
