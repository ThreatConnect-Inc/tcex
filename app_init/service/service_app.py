# -*- coding: utf-8 -*-
"""Service App module for TcEx App."""
# first-party
from args import Args


# pylint: disable=unused-argument
class ServiceApp:
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
        self.tcex.log.info('Parsed Args.')

    def create_config_callback(self, trigger_id, config, **kwargs):
        """Handle create config messages.

        Args:
            trigger_id (str): The ID of the playbook.
            config (dict): The playbook config inputs.
            url (str, kwargs): The URL for a webhook trigger.
        """
        self.tcex.log.trace('create config callback')

    def delete_config_callback(self, trigger_id):
        """Handle delete config messages.

        Args:
            trigger_id (str): The ID of the playbook.
        """
        self.tcex.log.trace('delete config callback')

    def run(self):
        """Run the App main logic."""
        self.tcex.log.trace('run')

    def setup(self):
        """Perform prep/startup operations."""
        self.tcex.log.trace('setup')

    def shutdown_callback(self):
        """Handle shutdown messages."""
        self.tcex.log.trace('shutdown callback')

    def teardown(self):
        """Perform cleanup operations and gracefully exit the App."""
        self.tcex.log.trace('teardown')
