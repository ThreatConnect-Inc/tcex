# -*- coding: utf-8 -*-
"""ThreatConnect Trigger Service App"""

# Import default Service App Class (Required)
from service_app import ServiceApp


# pylint: disable=unused-argument
class App(ServiceApp):
    """Service App Template."""

    def run(self):
        """Run the trigger logic."""
        while self.tcex.service.loop_forever(sleep=30):
            self.tcex.service.fire_event(self.trigger_callback, my_data='data')

    def trigger_callback(self, playbook, trigger_id, config, **kwargs):
        """Execute trigger callback for all current configs.

        Args:
            playbook (object): An instance of Playbooks used to write
                output variables to be used in downstream Apps.
            trigger_id (int): The ID of the Playbook Trigger.
            config (dict): The trigger input configuration data.

        Returns:
            bool: True if playbook should trigger, False if not.
        """
        my_data = kwargs.get('my_data')
        self.tcex.log.debug(f'my_data: {my_data}')
        return True
