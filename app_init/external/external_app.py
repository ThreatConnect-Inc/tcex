# -*- coding: utf-8 -*-
"""External App Template."""

# Typically no changes are required to this file.


class ExternalApp(object):
    """Get the owners and indicators in the given owner."""

    def __init__(self, _tcex):
        """Initialize class properties."""
        self.tcex = _tcex
        self.args = None
        self.exit_message = 'Success'
        self.args = self.tcex.args

    def done(self):
        """Perform cleanup operations and gracefully exit the App."""
        self.tcex.log.debug('Running done.')

    def run(self):
        """Run the App main logic."""
        self.tcex.log.info('No run logic provided.')

    def start(self):
        """Perform prep/startup operations."""
        self.tcex.log.debug('Running start.')
