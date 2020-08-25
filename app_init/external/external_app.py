"""External App Template."""


class ExternalApp:
    """Get the owners and indicators in the given owner."""

    def __init__(self, _tcex: object):
        """Initialize class properties."""
        self.tcex = _tcex

        # properties
        self.args = None
        self.exit_message = 'Success'
        self.args: object = self.tcex.args

    def run(self) -> None:
        """Run the App main logic."""
        self.tcex.log.info('No run logic provided.')

    def setup(self) -> None:
        """Perform prep/setup logic."""
        # run legacy method
        if hasattr(self, 'start'):
            self.tcex.log.warning('calling legacy start method')
            self.start()  # pylint: disable=no-member
        self.tcex.log.trace('setup')

    def teardown(self) -> None:
        """Perform cleanup/teardown logic."""
        # run legacy method
        if hasattr(self, 'done'):
            self.tcex.log.warning('calling legacy done method')
            self.done()  # pylint: disable=no-member
        self.tcex.log.trace('teardown')
