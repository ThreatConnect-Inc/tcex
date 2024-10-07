"""TcEx Framework Module"""

# standard library
import base64
import json
import traceback
from collections.abc import Callable
from typing import Any

# first-party
from tcex.app.key_value_store.key_value_store import KeyValueStore
from tcex.app.service.common_service_trigger import CommonServiceTrigger
from tcex.app.token import Token
from tcex.input.model.create_config_model import CreateConfigModel
from tcex.input.model.module_app_model import ModuleAppModel
from tcex.logger.logger import Logger


class WebhookTriggerService(CommonServiceTrigger):
    """TcEx Framework Webhook Service Trigger module."""

    def __init__(
        self,
        key_value_store: KeyValueStore,
        logger: Logger,
        model: ModuleAppModel,
        token: Token,
    ):
        """Initialize the Class properties."""
        super().__init__(key_value_store, logger, model, token)

        # config callbacks
        self.webhook_event_callback: Callable  # set in run.py of the App
        self.webhook_marshall_event_callback = None

    def callback_response_handler(self, callback_response: Any, message: dict):
        """Handle the different types of callback responses.

        # Webhook App (default)

        * Dict - Playbook will not be launched and provided data
            will be used in the response to the client.
        * True - Playbook will be launched.
        * Else - Playbook will NOT be launched.

        # webhookResponseMarshall Feature App

        * Callable - Playbook will be launched and if marshall callback will be set to response.
        * True - Playbook will be launched.
        * Else - Playbook will NOT be launched.

        # webhookServiceEndpoint Feature App

        For this feature the callback method must fire the event on it's own.

        * Dict - Playbook will not be launched and provided data
            will be used in the response to the client.
        * Else - Response will be set to default of statusCode=200, body=None, and headers=[].

        Args:
            callback_response: The response from the webhook callback method.
            message: The message payload from the server topic.
        """
        if self.ij.has_feature('webhookserviceendpoint'):
            self.callback_response_service_endpoint(callback_response, message)
        elif self.ij.has_feature('webhookresponsemarshall'):
            self.callback_response_marshall(callback_response, message)
        else:
            self.callback_response_webhook(callback_response, message)

    def callback_response_webhook(self, callback_response: Any, message: dict):
        """Handle the different types of callback responses.

        * Dict - Playbook will not be launched and provided data
                 will be used in the response to the client.
        * True - Playbook will be launched.
        * Else - Playbook will NOT be launched.

        Args:
            callback_response: The response from the webhook callback method.
            message: The message payload from the server topic.
        """
        if isinstance(callback_response, dict):
            # webhook responses are for providers that require a subscription req/resp.
            self.publish_webhook_event_response(message, callback_response)
        elif callback_response is True:
            self.increment_metric('Hits')
            self.fire_event_publish(
                message['triggerId'], self.session_id, message.get('requestKey')
            )

            # only required for testing in tcex framework
            self._tcex_testing(self.session_id, message['triggerId'])

            # capture fired status for testing framework
            self._tcex_testing_fired_events(self.session_id, True)
        else:
            self.increment_metric('Misses')

            # capture fired status for testing framework
            self._tcex_testing_fired_events(self.session_id, False)

    def callback_response_marshall(self, callback_response: Any, message: dict):
        """Handle the different types of callback responses.

        # webhookResponseMarshall Feature App

        * Callable - Playbook will be launched and if marshall callback will be set to response.
        * True - Playbook will be launched.
        * Else - Playbook will NOT be launched.

        Args:
            callback_response: The response from the webhook callback method.
            message: The message payload from the server topic.
        """
        fire_trigger = False
        if callable(callback_response):
            self.webhook_marshall_event_callback = callback_response
            fire_trigger = True

        # handle response the same a normal response
        self.callback_response_webhook(fire_trigger, message)

    def callback_response_service_endpoint(self, callback_response: Any, message: dict):
        """Handle the different types of callback responses.

        # webhookServiceEndpoint Feature App

        For this feature the callback method must fire the event on it's own.

        * Dict - Playbook will not be launched and provided data
                 will be used in the response to the client.
        * Else - Response will be set to default of statusCode=200, body=None, and headers=[].

        Args:
            callback_response: The response from the webhook callback method.
            message: The message payload from the server topic.
        """
        response = {
            'body': None,
            'headers': [],
            'statusCode': 200,
        }
        if isinstance(callback_response, dict):
            # webhook responses are for providers that require a subscription req/resp.
            response.update(callback_response)

        self.publish_webhook_event_response(message, callback_response)

    @property
    def command_map(self) -> dict:
        """Return the command map for the current Service type."""
        command_map: dict = super().command_map
        command_map.update({'webhookevent': self.process_webhook_event_command})
        command_map.update({'webhookmarshallevent': self.process_webhook_marshall_event_command})
        return command_map

    def process_webhook_event_command(self, message: dict):
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
        self.log.trace(
            f'feature=webhook-trigger-service, event=process-webhook-event, message={message}'
        )

        # acknowledge webhook event (nothing is currently done with this message on the core side)
        self.publish_webhook_event_acknowledge(message)

        # get config using triggerId passed in WebhookEvent data
        config: CreateConfigModel | None = None
        outputs: list = []
        if not self.ij.has_feature('webhookserviceendpoint'):
            config = self.configs.get(message['triggerId'])
            if config is None:
                self.log.error(
                    '''feature=webhook-trigger-service, event=missing-config, '''
                    f'''trigger-id={message.get('triggerId')}'''
                )
                return
            outputs = config.tc_playbook_out_variables

        # get a context aware pb instance for the App callback method
        playbook = self.get_playbook(context=self.session_id, output_variables=outputs)
        try:
            body: Any = self.key_value_store.client.read(message['requestKey'], 'request.body')
            if body is not None:
                body = base64.b64decode(body).decode()
            # pylint: disable=not-callable
            callback_data = {
                'body': body,
                'headers': message.get('headers'),
                'method': message.get('method'),
                'params': message.get('queryParams'),
            }
            if self.ij.has_feature('webhookresponsemarshall') or self.ij.has_feature(
                'webhookserviceendpoint'
            ):
                # add request_key arg when marshall or services endpoints feature is set (kwarg)
                callback_data.update({'request_key': message.get('requestKey')})
            elif not self.ij.has_feature('webhookserviceendpoint'):
                # add optional inputs for "standard" and "marshall" webhook trigger
                callback_data.update(
                    {
                        'config': config,
                        'playbook': playbook,
                        'trigger_id': message.get('triggerId'),
                    }
                )

            callback_response: bool | Callable[..., Any] | dict = self.webhook_event_callback(
                **callback_data
            )
            self.callback_response_handler(callback_response, message)
        except Exception as e:
            self.increment_metric('Errors')
            self.log.error(
                'feature=webhook-trigger-service, event=webhook-callback-exception, '
                f'error="""{e}"""'
            )
            self.log.trace(traceback.format_exc())

    def process_webhook_marshall_event_command(self, message: dict):
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
        self.log.trace(
            'feature=webhook-trigger-service, event=process-webhook-marshall-event, '
            f'message={message}'
        )

        # acknowledge webhook event (nothing is currently done with this message on the core side)
        self.publish_webhook_marshall_event_acknowledge(message)

        # get config using triggerId passed in WebhookMarshallEvent data
        config = self.configs.get(message['triggerId'])
        if config is None:
            self.log.error(
                '''feature=webhook-trigger-service, event=missing-config, '''
                f'''trigger-id={message.get('triggerId')}'''
            )
            return

        body = None
        request_key = message.get('requestKey')

        try:
            body: Any = self.key_value_store.client.read(
                request_key, 'request.body'  # type: ignore
            )
            if body is not None:
                body = base64.b64decode(body).decode()
        except Exception as e:
            self.increment_metric('Errors')
            self.log.error(
                'feature=webhook-trigger-service, event=webhook-marshall-callback-exception, '
                f'error="""{e}"""'
            )
            self.log.trace(traceback.format_exc())

        # set default value for callback response to the data returned from the playbook
        response = {
            'body': body,
            'headers': message.get('headers'),
            'status_code': message.get('statusCode'),
        }

        if callable(self.webhook_marshall_event_callback):
            try:
                # call callback method
                # pylint: disable=not-callable
                callback_response: dict | None = (
                    self.webhook_marshall_event_callback(  # type: ignore
                        body=body,
                        headers=message.get('headers'),
                        request_key=request_key,
                        status_code=message.get('statusCode'),
                        trigger_id=message.get('triggerId'),
                    )
                )
                if isinstance(callback_response, dict):
                    response.update(callback_response)
            except Exception as e:
                self.increment_metric('Errors')
                self.log.error(
                    'feature=webhook-trigger-service, event=webhook-marshall-callback-exception, '
                    f'error="""{e}"""'
                )
                self.log.trace(traceback.format_exc())

        # webhook responses are for providers that require a subscription req/resp.
        self.publish_webhook_event_response(message, response)

    def publish_webhook_event_acknowledge(self, message: dict):
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
            self.model.tc_svc_client_topic,
        )

    def publish_webhook_marshall_event_acknowledge(self, message: dict):
        """Publish the WebhookEventResponse message.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            {
                "command": "Acknowledged",
                "requestKey": "cd8c7a3a-7968-4b97-80c9-68b83a8ef1a1",
                "triggerId": 1,
                "type": "WebhookMarshallResponse"
            }

        Args:
            message: The message from the broker.
        """
        self.message_broker.publish(
            json.dumps(
                {
                    'command': 'Acknowledged',
                    'requestKey': message.get('requestKey'),
                    'triggerId': message.get('triggerId'),
                    'type': 'WebhookMarshallEvent',
                }
            ),
            self.model.tc_svc_client_topic,
        )

    def publish_webhook_event_response(self, message: dict, callback_response: dict):
        """Publish the WebhookEventResponse message.

        Args:
            message: The message from the broker.
            callback_response: The data from the callback method.
            playbook: Configure instance of Playbook used to write body.
        """
        playbook = self.get_playbook(context=self.session_id, output_variables=[])

        # write response body to redis
        if callback_response.get('body') is not None:
            playbook.create.string(
                'response.body',
                base64.b64encode(callback_response['body'].encode('utf-8')).decode('utf-8'),
            )

        # publish response
        self.message_broker.publish(
            json.dumps(
                {
                    'sessionId': self.session_id,  # session/context
                    'requestKey': message.get('requestKey'),
                    'command': 'WebhookEventResponse',
                    'triggerId': message.get('triggerId'),
                    'bodyVariable': 'response.body',
                    'headers': callback_response.get('headers', []),
                    'statusCode': callback_response.get('status_code', 200),
                }
            ),
            self.model.tc_svc_client_topic,
        )
