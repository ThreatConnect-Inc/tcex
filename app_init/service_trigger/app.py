# -*- coding: utf-8 -*-
"""ThreatConnect Trigger Service App"""
import time

# Import default Service App Class (Required)
from service_app import ServiceApp


# pylint: disable=unused-argument
class App(ServiceApp):
    """Service App Template."""

    def run(self):
        """Run the trigger logic."""
        sleep_time = 30
        while True:
            # sleep for 30 seconds and then fire playbook
            time.sleep(sleep_time)
            self.tcex.service.fire_event(self.trigger_callback)

    def trigger_callback(  # pylint: disable=no-self-use
        self, playbook, trigger_id, config, **kwargs
    ):
        """Execute trigger callback for all current configs.

        Args:
            playbook (object): An instance of Playbooks used to write output variables to be
                used in downstream Apps.
            trigger_id (int): The ID of the Playbook Trigger.
            config (dict): The trigger input configuration data.

        Returns:
            bool: True if playbook should trigger, False if not.
        """
        return True
