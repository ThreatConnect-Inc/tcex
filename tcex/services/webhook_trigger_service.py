"""TcEx Framework Webhook Service Trigger module."""
# standard library
import base64
import json
import traceback
from typing import Any, Optional, Union

from .common_service_trigger import CommonServiceTrigger


class WebhookTriggerService(CommonServiceTrigger):
    """TcEx Framework Webhook Service Trigger module."""

    def __init__(self, tcex: object):
        """Initialize the Class properties.

        Args:
            tcex: Instance of TcEx.
        """
        super().__init__(tcex)

        # config callbacks
        self.webhook_event_callback = None
        self.webhook_marshall_event_callback = None

    @property
    def command_map(self) -> dict:
        """Return the command map for the current Service type."""
        command_map: dict = super().command_map
        command_map.update({'webhookevent': self.process_webhook_event_command})
        command_map.update({'webhookmarshallevent': self.process_webhook_marshall_event_command})
        return command_map

    def process_webhook_event_command(self, message: dict) -> None:
        """Process the WebhookEvent command.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            {
                "appId": 387,
                "command": "WebhookEvent",
                "triggerId": 1,
                "requestKey": "cd8c7a3a-7968-4b97-80c9-68b83a8ef1a1",
                "method": "GET",
                "headers": [
                    {
                        "name": "Accept-Encoding",
                        "value": "gzip, deflate, br"
                    }
                ],
                "queryParams": [
                    {
                        "name": "registration",
                        "value": "true"
                    }
                ]
            }

        Args:
            message: The message payload from the server topic.
        """
        self.log.trace('feature=webhooktrigger-service, event=process-webhook-event')

        # acknowledge webhook event (nothing is currently done with this message on the core side)
        self.publish_webhook_event_acknowledge(message)

        # get config using triggerId passed in WebhookEvent data
        config: dict = self.configs.get(message.get('triggerId'))
        if config is None:
            self.log.error(
                '''feature=webhooktrigger-service, event=missing-config, '''
                f'''trigger-id={message.get('triggerId')}'''
            )
            return

        # get an instance of playbooks for App
        outputs: Union[list, str] = config.get('tc_playbook_out_variables') or []
        if isinstance(outputs, str):
            outputs = outputs.split(',')

        # get a context aware pb instance for the App callback method
        playbook: object = self.tcex.pb(context=self.session_id(), output_variables=outputs)
        try:
            request_key: str = message.get('requestKey')
            body: Any = self.redis_client.hget(request_key, 'request.body')
            if body is not None:
                body = base64.b64decode(body).decode()
            headers: dict = message.get('headers')
            method: str = message.get('method')
            params: dict = message.get('queryParams')
            trigger_id: int = message.get('triggerId')
            # pylint: disable=not-callable
            callback_response: Union[bool, dict] = self.webhook_event_callback(
                trigger_id, playbook, method, headers, params, body, config
            )
            if isinstance(callback_response, dict):
                # webhook responses are for providers that require a subscription req/resp.
                self.publish_webhook_event_response(message, callback_response)
            elif isinstance(callback_response, bool) and callback_response:
                self.increment_metric('Hits')
                self.fire_event_publish(trigger_id, self.session_id(), request_key)

                # only required for testing in tcex framework
                self._tcex_testing(self.session_id(), trigger_id)

                # capture fired status for testing framework
                self._tcex_testing_fired_events(self.session_id(), True)
            else:
                self.increment_metric('Misses')

                # capture fired status for testing framework
                self._tcex_testing_fired_events(self.session_id(), False)
        except Exception as e:
            self.increment_metric('Errors')
            self.log.error(
                f'feature=webhooktrigger-service, event=webhook-callback-exception, error="""{e}"""'
            )
            self.log.trace(traceback.format_exc())

    def process_webhook_marshall_event_command(self, message: dict) -> None:
        """Process the WebhookMarshallEvent command.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            {
                "appId": 95,
                "bodyVariable": "request.body",
                "command": "WebhookMarshallEvent",
                "headers": [
                    {
                        "name": "Accept",
                        "value": "*/*"
                    }
                ],
                "requestKey": "c29927c8-b94d-4116-a397-e6eb7002f41c",
                "statusCode": 200,
                "triggerId": 1234
            }

        Args:
            message: The message payload from the server topic.
        """
        # get config using triggerId passed in WebhookMarshallEvent data
        config: dict = self.configs.get(message.get('triggerId'))
        if config is None:
            self.log.error(
                '''feature=webhooktrigger-service, event=missing-config, '''
                f'''trigger-id={message.get('triggerId')}'''
            )
            return

        # read body from kv store
        request_key: str = message.get('requestKey')
        body: Any = self.redis_client.hget(request_key, 'request.body')
        if body is not None:
            body = base64.b64decode(body).decode()

        # call callback method
        # pylint: disable=not-callable
        callback_response: Optional[dict] = self.webhook_marshall_event_callback(
            body=body,
            headers=message.get('headers'),
            request_key=request_key,
            status_code=message.get('statusCode'),
            trigger_id=message.get('triggerId'),
        )

        # webhook responses are for providers that require a subscription req/resp.
        self.publish_webhook_event_response(message, callback_response)

    def publish_webhook_event_acknowledge(self, message: dict) -> None:
        """Publish the WebhookEventResponse message.

        Args:
            message: The message from the broker.
        """
        self.message_broker.publish(
            json.dumps(
                {
                    'command': 'Acknowledged',
                    'requestKey': message.get('requestKey'),
                    'triggerId': message.get('triggerId'),
                    'type': 'WebhookEvent',
                }
            ),
            self.args.tc_svc_client_topic,
        )

    def publish_webhook_event_response(self, message: dict, callback_response: dict) -> None:
        """Publish the WebhookEventResponse message.

        Args:
            message: The message from the broker.
            callback_response: The data from the callback method.
            playbook: Configure instance of Playbook used to write body.
        """
        playbook: object = self.tcex.pb(context=self.session_id())

        # write response body to redis
        if callback_response.get('body') is not None:
            playbook.create_string(
                'response.body',
                base64.b64encode(callback_response.get('body').encode('utf-8')).decode('utf-8'),
            )

        # publish response
        self.message_broker.publish(
            json.dumps(
                {
                    'sessionId': self.session_id(),  # session/context
                    'requestKey': message.get('requestKey'),
                    'command': 'WebhookEventResponse',
                    'triggerId': message.get('triggerId'),
                    'bodyVariable': 'response.body',
                    'headers': callback_response.get('headers', []),
                    'statusCode': callback_response.get('status_code', 200),
                }
            ),
            self.args.tc_svc_client_topic,
        )
