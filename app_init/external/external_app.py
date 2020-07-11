# -*- coding: utf-8 -*-
"""External App Template."""

# Typically no changes are required to this file.


class ExternalApp:
    """Get the owners and indicators in the given owner."""

    def __init__(self, _tcex):
        """Initialize class properties."""
        self.tcex = _tcex
        self.args = None
        self.exit_message = 'Success'
        self.args = self.tcex.args

    def run(self):
        """Run the App main logic."""
        self.tcex.log.info('No run logic provided.')

    def setup(self):
        """Perform prep/setup logic."""
        # run legacy method
        if hasattr(self, 'start'):
            self.tcex.log.warning('calling legacy start method')
            self.start()  # pylint: disable=no-member
        self.tcex.log.trace('setup')

    def teardown(self):
        """Perform cleanup/teardown logic."""
        # run legacy method
        if hasattr(self, 'done'):
            self.tcex.log.warning('calling legacy done method')
            self.done()  # pylint: disable=no-member
        self.tcex.log.trace('teardown')
