# -*- coding: utf-8 -*-
"""ThreatConnect Playbook App"""

# Import default Service Class (Required)
from service_app import ServiceApp


# pylint: disable=unused-argument
class App(ServiceApp):
    """Service App Template."""

    def webhook_event_callback(self, playbook, method, headers, params, body, config):
        """Run the trigger logic.

        Args:
            playbook (obj): An instance of Playbook to use to write output variables.
            method (str): The HTTP method (e.g., DELETE, GET, etc.).
            headers (dict): The request headers (multiple values will be returned in an array).
            params (dict): The request query params (multiple values will be returned in an array).
            body (bytes, string): The request body.
            config (dict): The playbook config inputs.

        Returns:
            bool: True if playbook should trigger, False if not.
        """
        self.tcex.log.info('method: {}'.format(method))
        self.tcex.log.info('headers: {}'.format(headers))
        self.tcex.log.info('params: {}'.format(params))
        self.tcex.log.info('body: {}'.format(body))
        self.tcex.log.info('config: {}'.format(config))

        if config.get('id') == params.get('id'):
            return True  # playbook triggered
        return False  # playbook skipped
