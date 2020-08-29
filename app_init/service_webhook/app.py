"""ThreatConnect Playbook App"""
from typing import Union, List, Dict

# first-party
from service_app import ServiceApp  # Import default Service Class (Required)


# pylint: disable=unused-argument
from tcex.playbooks import Playbooks


class App(ServiceApp):
    """Service App Template."""

    def webhook_event_callback(  # pylint: disable=no-self-use
        self,
        trigger_id: int,
        playbook: Playbooks,
        method: str,
        headers: List[Dict[str, str]],
        params: List[Dict[str, str]],
        body: Union[bytes, str],
        config: dict,
    ):
        """Run the trigger logic.

        Args:
            trigger_id: Optional trigger_id value used in testing framework.
            playbook: An instance of Playbook to use to write output variables.
            method: The HTTP method (e.g., DELETE, GET, etc.).
            headers: The request headers (multiple values will be returned in an array).
            params: The request query params (multiple values will be returned in an array).
            body: The request body.
            config: The playbook config inputs.

        Returns:
            bool: True if playbook should trigger, False if not.
        """
        return True

    def webhook_marshall_event_callback(  # pylint: disable=no-self-use
        self,
        body: Union[bytes, str],
        headers: List[Dict[str, str]],
        status_code: int,
        trigger_id: int,
    ):
        """Run the trigger logic.

        Example Headers:

        "headers": [
            {
                "name": "Accept",
                "value": "*/*"
            }
        ]

        Args:
            body: The response body.
            headers: The response headers (multiple values will be returned in an array).
            status_code: The response status code.
            trigger_id: Optional trigger_id value used in testing framework.

        Returns:
            bool: True if playbook should trigger, False if not.
        """
        return {
            'body': body,
            'headers': headers,
            'status_code': status_code,
        }
