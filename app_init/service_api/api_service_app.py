"""Service App module for TcEx App."""
# first-party
from args import Args


# pylint: disable=unused-argument
class ApiServiceApp:
    """Service App Class.

    Args:
        _tcex (tcex.TcEx): An instance of tcex.
    """

    def __init__(self, _tcex):
        """Initialize class properties."""
        self.tcex = _tcex
        self.args = None
        self.exit_message = 'Success'

        # automatically parse args on init
        self.parse_args()

    def parse_args(self):
        """Parse CLI args."""
        Args(self.tcex.parser)
        self.args = self.tcex.args
        self.tcex.log.info('feature=app, event=args-parsed')

    def setup(self):
        """Perform prep/startup operations."""
        self.tcex.log.trace('feature=app, event=setup')

    def shutdown_callback(self):
        """Handle shutdown messages."""
        self.tcex.log.trace('feature=app, event=shutdown-callback')

    def teardown(self):
        """Perform cleanup operations and gracefully exit the App."""
        self.tcex.log.trace('feature=app, event=teardown')
