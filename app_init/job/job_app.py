"""Job App Template."""
# first-party
from args import Args

from tcex import TcEx


class JobApp:
    """Get the owners and indicators in the given owner."""

    def __init__(self, _tcex: TcEx):
        """Initialize class properties."""
        self.tcex: TcEx = _tcex
        self.args = None
        self.exit_message = 'Success'

        # automatically parse args on init
        self.parse_args()

    def parse_args(self) -> None:
        """Parse CLI args."""
        Args(self.tcex.parser)
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
