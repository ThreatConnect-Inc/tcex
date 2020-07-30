# -*- coding: utf-8 -*-
"""ThreatConnect Playbook App"""

# first-party
from service_app import ServiceApp  # Import default Service Class (Required)


# pylint: disable=unused-argument
class App(ServiceApp):
    """Service App Template."""

    def webhook_event_callback(  # pylint: disable=no-self-use
        self, trigger_id, playbook, method, headers, params, body, config
    ):
        """Run the trigger logic.

        Args:
            trigger_id (str): Optional trigger_id value used in testing framework.
            playbook (obj): An instance of Playbook to use to write output variables.
            method (str): The HTTP method (e.g., DELETE, GET, etc.).
            headers (dict): The request headers (multiple values will be returned in an array).
            params (dict): The request query params (multiple values will be returned in an array).
            body (bytes, string): The request body.
            config (dict): The playbook config inputs.

        Returns:
            bool: True if playbook should trigger, False if not.
        """
        return True
