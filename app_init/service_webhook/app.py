# -*- coding: utf-8 -*-
"""ThreatConnect Playbook App"""

# Import default Service Class (Required)
from service_app import ServiceApp


class App(ServiceApp):
    """Service App Template."""

    def webhook_callback(self, session_id, method, headers, params, body, config):
        """Run the trigger logic.

        Args:
            session_id (str): The session_id for the current playbook execution.
            method (str): The HTTP method (e.g., DELETE, GET, etc.).
            headers (dict): The request headers (multiple values will be returned in an array).
            params (dict): The request query params (multiple values will be returned in an array).
            body (bytes, string): The request body.
            config (dict): The playbook config inputs.

        Returns:
            bool: True if playbook should trigger, False if not.
        """
        try:
            self.tcex.log.info('session_id: {}'.format(session_id))
            self.tcex.log.info('method: {}'.format(method))
            self.tcex.log.info('params: {}'.format(params))
            self.tcex.log.info('headers: {}'.format(headers))
            self.tcex.log.info('body: {}'.format(body))
            self.tcex.log.info('config: {}'.format(config))

            if config.get('id') == params.get('id'):
                return True  # playbook triggered
            return False  # playbook skipped
        except Exception as e:
            # micro-service callback should not raise for any reason
            self.tcex.log.error('Webhook trigger failed ({})'.format(e))
            return False
