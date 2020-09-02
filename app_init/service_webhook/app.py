"""ThreatConnect Playbook App"""
from typing import Union, List, Dict

# first-party
from service_app import ServiceApp


class App(ServiceApp):
    """Service App Template."""

    # pylint: disable=no-self-use,unused-argument
    def webhook_event_callback(
        self,
        body: Union[bytes, str],
        headers: List[Dict[str, str]],
        method: str,
        params: List[Dict[str, str]],
        **kwargs,
    ):
        """Run the trigger logic.

        Args:
            body: The HTTP request body.
            headers: The HTTP request headers (multiple values will be returned in an array).
            method: The HTTP request method (e.g., DELETE, GET, etc.).
            params: The HTTP request query params (multiple values will be returned in an array).
            playbook: (object | kwargs) An instance of Playbook to use to write output variables.
                Not provided when feature WebhookServiceEndpoint is enabled.
            config (dict | kwargs): The playbook config inputs. Not provided
                when feature WebhookServiceEndpoint is enabled.
            request_key (str | kwargs): The unique request key for the current event. Only
                provided when feature webhookResponseMarshall or webhookServiceEndpoint is enabled.
            trigger_id (int | kwargs): The trigger id value used for the playbook being
                launched. Not provided when feature WebhookServiceEndpoint is enabled.

        Returns:
            bool, Callable[..., Any], dict: Dependent on the feature
                the method should provide different response.
        """
        response = None
        if self.tcex.ij.has_feature('WebhookResponseMarshall'):
            # * Callable - Playbook will be launched and if marshall
            #              callback will be set to response.
            # * True - Playbook will be launched.
            # * Else - Playbook will NOT be launched.
            response = True
        elif self.tcex.ij.has_feature('WebhookServiceEndpoint'):
            # * Dict - Playbook will be launched and provided data
            #          will be used in the response to the client.
            # * Else - Response will be set to default of statusCode=200, body=None, and headers=[].
            response = None
        else:
            # * Dict - Playbook will not be launched and provided data
            #          will be used in the response to the client.
            # * True - Playbook will be launched.
            # * Else - Playbook will NOT be launched.
            response = True

        return response

    # pylint: disable=no-self-use,unused-argument
    def webhook_marshall_event_callback(
        self,
        body: Union[bytes, str],
        headers: List[Dict[str, str]],
        request_key: str,
        status_code: int,
        trigger_id: int,
    ):
        """Handle webhook marshall events.

        !!! Only needed when APP support WebhookResponseMarshall feature. !!!

        A marshall event contains the the body, headers, and status code from a completed
        Playbook. This call back method allows the service to update or change the response
        that for the HTTP request.

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
            request_key: [WebhookResponseMarshall] The unique request
                key for the current event.
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
