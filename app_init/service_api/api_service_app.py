"""Service App module for TcEx App."""
# first-party
from args import Args


# pylint: disable=unused-argument
from tcex import TcEx


class ApiServiceApp:
    """Service App Class.

    Args:
        _tcex (tcex.TcEx): An instance of tcex.
    """

    def __init__(self, _tcex: TcEx):
        """Initialize class properties."""
        self.tcex: TcEx = _tcex

        # properties
        self.args = None
        self.exit_message = 'Success'

        # automatically parse args on init
        self.parse_args()

    def parse_args(self) -> None:
        """Parse CLI args."""
        Args(self.tcex.parser)
        self.args = self.tcex.args
        self.tcex.log.info('feature=app, event=args-parsed')

    def setup(self) -> None:
        """Perform prep/startup operations."""
        self.tcex.log.trace('feature=app, event=setup')

    def shutdown_callback(self) -> None:
        """Handle shutdown messages."""
        self.tcex.log.trace('feature=app, event=shutdown-callback')

    def teardown(self) -> None:
        """Perform cleanup operations and gracefully exit the App."""
        self.tcex.log.trace('feature=app, event=teardown')
