"""TcEx Framework Webhook Service Trigger module."""
# standard library
import base64
import json
import traceback
from typing import Any, Optional, Union

from .service_trigger_common import ServiceTriggerCommon


class WebhookTriggerService(ServiceTriggerCommon):
    """TcEx Framework Webhook Service Trigger module."""

    def __init__(self, tcex: object):
        """Initialize the Class properties.

        Args:
            tcex: Instance of TcEx.
        """
        super().__init__(tcex)

        # config callbacks
        self.webhook_event_callback = None

    @property
    def command_map(self):
        """Return the command map for the current Service type."""
        command_map: dict = super().command_map
        command_map.update({'webhookevent': self.process_webhook_event_command})
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
                ],
                "apiToken": "SVC:8:p284JJ:1596817629413:387:Vn0TM7FlowersFirC2boatJfoB8RBobsB ... ",
                "expireSeconds": 1596817629
            }

        Args:
            message: The message payload from the server topic.
        """
        self.message_thread(self.session_id(message.get('triggerId')), self.webhook, (message,))

    def webhook(self, message: dict):
        """Process Webhook event messages.

        Args:
            message: The message data from the broker.
        """
        # session auth shared data is thread name which needs to map back to config triggerId
        self.tcex.token.register_thread(message.get('triggerId'), self.thread_name)

        # add logger for current session
        self.tcex.logger.add_thread_file_handler(
            name=self.thread_name,
            filename=self.session_logfile,
            level=self.args.tc_log_level,
            path=self.args.tc_log_path,
        )
        self.log.trace('Process webhook event trigger')

        # acknowledge webhook event
        self.publish(
            json.dumps(
                {
                    'command': 'Acknowledged',
                    'requestKey': message.get('requestKey'),
                    'triggerId': message.get('triggerId'),
                    'type': 'WebhookEvent',
                }
            )
        )

        # get config using triggerId passed in WebhookEvent data
        config: dict = self.configs.get(message.get('triggerId'))
        if config is None:
            self.log.error(f"Could not find config for triggerId {message.get('triggerId')}")
            return

        # get an instance of playbooks for App
        outputs: Union[list, str] = config.get('tc_playbook_out_variables') or []
        if isinstance(outputs, str):
            outputs = outputs.split(',')

        playbook: object = self.tcex.pb(context=self.thread_name, output_variables=outputs)

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
            callback_response: Optional[bool] = self.webhook_event_callback(
                trigger_id, playbook, method, headers, params, body, config
            )
            if isinstance(callback_response, dict):
                # write response body to redis
                if callback_response.get('body') is not None:
                    playbook.create_string(
                        'response.body',
                        base64.b64encode(callback_response.get('body').encode('utf-8')).decode(
                            'utf-8'
                        ),
                    )

                # webhook responses are for providers that require a subscription req/resp.
                self.publish(
                    json.dumps(
                        {
                            'sessionId': self.thread_name,  # session/context
                            'requestKey': request_key,
                            'command': 'WebhookEventResponse',
                            'triggerId': trigger_id,
                            'bodyVariable': 'response.body',
                            'headers': callback_response.get('headers', []),
                            'statusCode': callback_response.get('statusCode', 200),
                        }
                    )
                )
            elif isinstance(callback_response, bool) and callback_response:
                self.increment_metric('Hits')
                self.fire_event_publish(trigger_id, self.thread_name, request_key)

                # only required for testing in tcex framework
                self._tcex_testing(self.thread_name, trigger_id)

                # capture fired status for testing framework
                self._tcex_testing_fired_events(self.thread_name, True)
            else:
                self.increment_metric('Misses')

                # capture fired status for testing framework
                self._tcex_testing_fired_events(self.thread_name, False)
        except Exception as e:
            self.log.error(f'The callback method encountered and error ({e}).')
            self.log.trace(traceback.format_exc())
            self.increment_metric('Errors')
        finally:
            # remove temporary logging file handler
            self.tcex.logger.remove_handler_by_name(self.thread_name)

            # unregister thread from token module
            self.tcex.token.unregister_thread(message.get('triggerId'), self.thread_name)
