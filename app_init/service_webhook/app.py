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
        headers: Union[List[Dict[str, str], Dict[str, str]]],
        params: Union[List[Dict[str, str], Dict[str, str]]],
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
