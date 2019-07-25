# -*- coding: utf-8 -*-
"""ThreatConnect Playbook App"""
import time

# Import default Service Class (Required)
from service_app import ServiceApp


# pylint: disable=unused-argument
class App(ServiceApp):
    """Service App Template."""

    def run(self):
        """Run the trigger logic."""
        while True:
            time.sleep(30)
            self.tcex.service.fire_event(self.trigger_callback)

    def trigger_callback(self, playbook, trigger_id, config, **kwargs):
        """Execute trigger callback for all current configs.

        Args:
            session_id (str): The session_id for the current playbook execution.
            config (dict): The playbook config inputs.

        Returns:
            bool: True if playbook should trigger, False if not.
        """
        self.tcex.log.error('trigger callback')
        try:
            self.tcex.log.trace('config: {}'.format(config))

            if config.get('fire') is True:
                return True
            return False
        except Exception as e:
            # micro-service callback should not raise for any reason
            self.tcex.log.error('Custom trigger failed ({})'.format(e))
            return False
