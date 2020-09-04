"""Service App module for TcEx App."""
# first-party
from args import Args


# pylint: disable=unused-argument
from tcex import TcEx


class ServiceApp:
    """Service App Class.

    Args:
        _tcex: An instance of tcex.
    """

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
        self.args = self.tcex.args
        self.tcex.log.info('Parsed Args.')

    def create_config_callback(self, trigger_id: str, config: dict, **kwargs) -> dict:
        """Handle create config messages.

        Args:
            trigger_id: The ID of the playbook.
            config: The playbook config inputs.
            url (str, kwargs): The URL for a webhook trigger.

        Returns:
            dict: A dict containing a **msg** field that can be used to relay error context back to
                playbook and a status boolean. True indicates configuration was successful.
        """
        self.tcex.log.trace('create config callback')
        return {'msg': 'Success', 'status': True}

    def delete_config_callback(self, trigger_id: int) -> None:
        """Handle delete config messages.

        Args:
            trigger_id: The ID of the playbook.
        """
        self.tcex.log.trace('delete config callback')

    def run(self) -> None:
        """Run the App main logic."""
        self.tcex.log.trace('run')

    def setup(self) -> None:
        """Perform prep/startup operations."""
        self.tcex.log.trace('setup')

    def shutdown_callback(self) -> None:
        """Handle shutdown messages."""
        self.tcex.log.trace('shutdown callback')

    def teardown(self) -> None:
        """Perform cleanup operations and gracefully exit the App."""
        self.tcex.log.trace('teardown')
