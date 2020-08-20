"""TcEx Framework Service Trigger Common module."""
# standard library
import json
import traceback
from datetime import datetime
from typing import Optional

from .common_service import CommonService


class CommonServiceTrigger(CommonService):
    """TcEx Framework Service Trigger Common module.

    Shared service logic between the supported service types:
    * Custom Trigger Service
    * Webhook Trigger Service
    """

    def __init__(self, tcex: object):
        """Initialize the Class properties.

        Args:
            tcex: Instance of TcEx.
        """
        super().__init__(tcex)

        # properties
        self._metrics = {'Active Playbooks': 0, 'Errors': 0, 'Hits': 0, 'Misses': 0}
        self.configs = {}
        self.config_thread = None

        # config callbacks
        self.create_config_callback = None
        self.delete_config_callback = None

    def _tcex_testing(self, session_id: str, trigger_id: int) -> None:
        """Write data required for testing framework to Redis.

        Args:
            session_id: The context/session id value for the current operation.
            trigger_id: The trigger ID for the current playbook.
        """
        if self.args.tcex_testing_context is not None:
            _context_tracker: str = (
                self.redis_client.hget(self.args.tcex_testing_context, '_context_tracker') or '[]'
            )
            _context_tracker = json.loads(_context_tracker)
            _context_tracker.append(session_id)
            self.redis_client.hset(
                self.args.tcex_testing_context, '_context_tracker', json.dumps(_context_tracker),
            )
            self.redis_client.hset(session_id, '_trigger_id', trigger_id)

            # log
            self.log.info(
                'feature=service, event=testing-context-tracker, '
                f'context={session_id}, trigger-id={trigger_id}'
            )

    def _tcex_testing_fired_events(self, session_id: str, fired: bool) -> None:
        """Write fired event data to KV Store to be used in test validation.

        Args:
            session_id: The context/session id value for the current operation.
            fired: The value to increment the count by.
        """
        if self.args.tcex_testing_context is not None:
            self.redis_client.hset(
                session_id, '#Trigger:9876:_fired!String', json.dumps(str(fired).lower())
            )

    @property
    def command_map(self) -> dict:
        """Return the command map for the current Service type."""
        command_map = super().command_map
        command_map.update(
            {
                'createconfig': self.process_create_config_command,
                'deleteconfig': self.process_delete_config_command,
            }
        )
        return command_map

    def create_config(self, trigger_id: int, config: dict, message: str, status: bool) -> None:
        """Add config item to service config object.

        Args:
            trigger_id: The trigger ID for the current config.
            config: The config for the current trigger.
            message: A simple message for the action.
            status: The passed/fail status for the App handling of config.
        """
        try:
            if status is True:
                # add config to configs
                self.configs[trigger_id] = config

            # send ack response
            self.message_broker.publish(
                json.dumps(
                    {
                        'command': 'Acknowledged',
                        'message': message,
                        'status': 'Success' if status is True else 'Failed',
                        'type': 'CreateConfig',
                        'triggerId': trigger_id,
                    }
                ),
                self.tcex.default_args.tc_svc_client_topic,
            )
        except Exception as e:
            self.log.error(f'Could not create config for Id {trigger_id} ({e}).')
            self.log.error(
                'feature=service, event=create-config-callback-exception, '
                f'trigger-id={trigger_id}, error="""{e}"""'
            )
            self.log.trace(traceback.format_exc())

    def delete_config(self, trigger_id: int, message: str, status: str) -> None:
        """Delete config item from config object.

        Args:
            trigger_id: The trigger ID for the current config.
            message: A simple message for the action.
            status: The passed/fail status for the App handling of config.
        """
        try:
            # always delete config from configs dict, even when status is False
            del self.configs[trigger_id]

            # send ack response
            self.message_broker.publish(
                json.dumps(
                    {
                        'command': 'Acknowledged',
                        'message': message,
                        'status': 'Success' if status is True else 'Failed',
                        'type': 'DeleteConfig',
                        'triggerId': trigger_id,
                    }
                ),
                self.tcex.default_args.tc_svc_client_topic,
            )
        except Exception as e:
            self.log.error(
                'feature=service, event=delete-config-callback-exception, '
                f'trigger-id={trigger_id}, error="""{e}"""'
            )
            self.log.trace(traceback.format_exc())

    def fire_event_publish(
        self, trigger_id: int, session_id: str, request_key: Optional[str] = None
    ) -> None:
        """Send FireEvent command.

        Args:
            trigger_id: The ID of the trigger.
            session_id: The generated session for this fired event.
            request_key: The request key for this response.
        """
        msg = {
            'command': 'FireEvent',
            'triggerId': trigger_id,  # reference to single playbook
            'sessionId': session_id,  # session for the playbook execution
        }
        if request_key is not None:
            msg['requestKey'] = request_key  # reference for a specific playbook execution
        self.log.info(f'feature=service, event=fire-event, msg={msg}')

        # publish FireEvent command to client topic
        self.message_broker.publish(json.dumps(msg), self.tcex.default_args.tc_svc_client_topic)

    def process_create_config_command(self, message: dict) -> None:
        """Process the CreateConfig command.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            {
                "appId": 387,
                "command": "CreateConfig",
                "triggerId": 1,
                "config": {
                    "password": "test-pass",
                    "username": "test-user",
                    "cc_action": "pass",
                    "tc_playbook_out_variables": "#Trigger:1:testing.body!String"
                },
                "apiToken": "SVC:8:QQuyIp:1596817138182:387:+9vBOAT8Y56caHRcjLa4IwAqABoatsYOU ... ",
                "expireSeconds": 1596817138
            }

        Args:
            message: The message payload from the server topic.
        """
        config: dict = message.get('config')
        status = True
        trigger_id: int = message.get('triggerId')
        self.log.info(
            f'feature=service, event=create-config, trigger_id={trigger_id}, config={config}'
        )

        # register config apiToken
        self.tcex.token.register_token(
            trigger_id, message.get('apiToken'), message.get('expireSeconds')
        )

        msg = 'Create Config'
        if callable(self.create_config_callback):
            kwargs = {}
            if self.tcex.ij.runtime_level.lower() == 'webhooktriggerservice':
                # only webhook triggers get and require the PB url
                kwargs['url'] = message.get('url')

            try:
                # call callback for create config and handle exceptions to protect thread
                # pylint: disable=not-callable
                response: Optional[dict] = self.create_config_callback(trigger_id, config, **kwargs)
                if isinstance(response, dict):
                    status = response.get('status')
                    msg = response.get('msg')

                # if callback does not return a boolean value assume it worked
                if not isinstance(status, bool):
                    status = True
            except Exception as e:
                status = False
                msg = str(e)
                self.log.error(
                    f'feature=service, event=create-config-callback-exception, error="""{e}"""'
                )
                self.log.error(message)
                self.log.trace(traceback.format_exc())

        # create config after callback to report status and message
        self.create_config(trigger_id, config, msg, status)

    def process_delete_config_command(self, message: dict) -> None:
        """Process the DeleteConfig command.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            {
                "appId": 387,
                "command": "DeleteConfig",
                "triggerId": 1
            }

        Args:
            message: The message payload from the server topic.
        """
        status = True
        trigger_id: int = message.get('triggerId')
        self.log.info(f'feature=service, event=delete-config, trigger_id={trigger_id}')

        # unregister config apiToken
        self.tcex.token.unregister_token(trigger_id)

        msg = 'Delete Config'
        if callable(self.delete_config_callback):
            try:
                # call callback for delete config and handle exceptions to protect thread
                # pylint: disable=not-callable
                status: Optional[bool] = self.delete_config_callback(trigger_id)

                # if callback does not return a boolean value assume it worked
                if not isinstance(status, bool):
                    status = True
            except Exception as e:
                self.log.error(
                    f'feature=service, event=delete-config-callback-exception, error="""{e}"""'
                )
                self.log.trace(traceback.format_exc())
                status = False

        # delete config
        self.delete_config(trigger_id, msg, status)

    @property
    def session_logfile(self) -> str:
        """Return a uuid4 session id."""
        return f'''{datetime.today().strftime('%Y%m%d')}/{self.thread_name}.log'''
