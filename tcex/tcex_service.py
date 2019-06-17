# -*- coding: utf-8 -*-
"""TcEx Framework Service module"""
import json
import threading
import uuid


class TcExService(object):
    """Service methods for customer Service (e.g., Triggers)."""

    def __init__(self, tcex):
        """Initialize the Class properties.

        Args:
            tcex (object): Instance of TcEx.
        """
        self.tcex = tcex
        self.log = self.tcex.log
        self._client = None
        self.p = None
        self.configs = {}

    # def api_service(self, callback):
    #     """Run subscribe method

    #     {
    #       "command": "RunService",
    #       "requestKey": "abcdefghi",
    #       "method": "GET",
    #       "queryParams": [ { key/value pairs } ],
    #       "headers": [ { key/value pairs } ],
    #       "bodySessionId": "85be2761..."
    #       "responseBodySessionId": "91eee889..."
    #     }
    #     """
    #     if not self.tcex.default_args.tc_server_channel:
    #         self.tcex.exit(1, 'No server channel provided.')

    #     p = self.client.pubsub()
    #     p.subscribe(self.tcex.default_args.tc_server_channel)
    #     for m in p.listen():
    #         # only process message on channel (exclude subscriptions)
    #         if m.get('type') != 'message':
    #             continue

    #         try:
    #             # load message data
    #             msg_data = json.loads(m.get('data'))
    #         except ValueError:
    #             self.tcex.log.warning('Cannot parse message ({}).'.format(m))
    #             continue

    #         session_id = str(uuid.uuid4())

    #         # parse message data contents
    #         command = msg_data.get('command')
    #         # parameters for config commands
    #         config_id = msg_data.get('configId')
    #         params = msg_data.get('params')
    #         request_key = msg_data.get('requestKey')

    #         if not command:
    #             self.tcex.log.warning('Received a message without command ({})'.format(m))
    #             continue
    #         elif command == 'CreateConfig':
    #             self.create_config(config_id, params)
    #         elif command == 'DeleteConfig':
    #             self.delete_config(config_id)
    #         elif command == 'UpdateConfig':
    #             self.update_config(config_id, params)
    #         elif command == 'Shutdown':
    #             self.tcex.log.info(
    #                 'A shutdown command was received on server channel. Service is shutting down.'
    #             )
    #             p.unsubscribe()
    #         elif command == 'RunService':
    #             body = msg_data.get('body')  # variable reference for REDIS lookup
    #             headers = msg_data.get('headers')
    #             method = msg_data.get('method')
    #             params = msg_data.get('queryParams')
    #             path = msg_data.get('path')

    @property
    def client(self):
        """Return the correct KV store for this execution."""
        if self._client is None:
            if self.tcex.default_args.tc_playbook_db_type == 'Redis':
                from .tcex_redis import TcExRedis

                self._client = TcExRedis(
                    self.tcex.default_args.tc_playbook_db_path,
                    self.tcex.default_args.tc_playbook_db_port,
                    self.tcex.default_args.tc_playbook_db_context,
                )
            elif self.tcex.default_args.tc_playbook_db_type == 'TCKeyValueAPI':
                raise RuntimeError('Services are not supported on Environment Server.')
            else:
                raise RuntimeError(
                    'Invalid DB Type: ({})'.format(self.tcex.default_args.tc_playbook_db_type)
                )
        return self._client.r

    def create_config(self, config_id, params):
        """Add config item to service config object."""
        try:
            self.configs[config_id] = params

            response = {
                'status': 'Acknowledged',
                'type': 'CreateConfig',
                'configId': config_id,
                'outputVariables': ['<string array of expected output variables for this config>'],
            }
            self.client.publish('channel', response)
        except Exception:
            self.tcex.log.error('Could not create config item.')

    def custom_trigger(
        self,
        create_callback=None,
        update_callback=None,
        delete_callback=None,
        shutdown_callback=None,
    ):
        """Add custom trigger

        Args:
            create_callback (callable): Method or function to call when create config command
                received. Default to None.
            update_callback (callable): Method or function to call when update config command
                received. Default to None.
            delete_callback (callable): Method or function to call when delete config command
                received. Default to None.
            shutdown_callback (callable): Method or function to call when shutdown command received.
                Default to None.
        """
        t = threading.Thread(
            target=self.custom_trigger_subscriber,
            args=(create_callback, update_callback, delete_callback, shutdown_callback),
            daemon=True,
        )
        t.start()

    def custom_trigger_subscriber(
        self,
        create_callback=None,
        update_callback=None,
        delete_callback=None,
        shutdown_callback=None,
    ):
        """Add custom trigger subscriber

        Args:
            create_callback (callable): Method or function to call when create config command
                received. Default to None.
            update_callback (callable): Method or function to call when update config command
                received. Default to None.
            delete_callback (callable): Method or function to call when delete config command
                received. Default to None.
            shutdown_callback (callable): Method or function to call when shutdown command received.
                Default to None.
        """
        if not self.tcex.default_args.tc_server_channel:
            self.tcex.exit(1, 'No server channel provided.')

        p = self.client.pubsub()
        p.subscribe(self.tcex.default_args.tc_server_channel)
        for m in p.listen():
            # only process message on channel (exclude subscriptions)
            if m.get('type') != 'message':
                continue

            try:
                # load message data
                msg_data = json.loads(m.get('data'))
            except ValueError:
                self.tcex.log.warning('Cannot parse message ({}).'.format(m))
                continue

            # session_id = str(uuid.uuid4())

            # parse message data contents
            command = msg_data.get('command')
            # parameters for config commands
            config_id = msg_data.get('configId')
            params = msg_data.get('params')
            # request_key = msg_data.get('requestKey')

            if not command:
                self.tcex.log.warning('Received a message without command ({})'.format(m))
                continue
            elif command == 'CreateConfig':
                self.create_config(config_id, params)
                if callable(create_callback):
                    create_callback(msg_data)
            elif command == 'DeleteConfig':
                self.delete_config(config_id)
                if callable(delete_callback):
                    delete_callback(msg_data)
            elif command == 'UpdateConfig':
                self.update_config(config_id, params)
                if callable(update_callback):
                    update_callback(msg_data)
            elif command == 'Shutdown':
                if callable(shutdown_callback):
                    shutdown_callback(msg_data)
                self.tcex.log.info(
                    'A shutdown command was received on server channel. Service is shutting down.'
                )
                p.unsubscribe()

    def delete_config(self, config_id):
        """Delete config item from config object."""
        try:
            del self.configs[config_id]
        except AttributeError:
            self.tcex.log.warning('Could not delete config item.')

    def fire_event(self, session_id, config_id):
        """Publish a message on client channel.

        Args:
            message (str): The message to be sent on client channel.
        """
        message = {'configId': config_id, 'sessionId': session_id}
        self.client.publish(self.tcex.default_args.tc_client_channel, message)

    def publish(self, message):
        """Publish a message on client channel.

        Args:
            message (str): The message to be sent on client channel.
        """
        self.client.publish(self.tcex.default_args.tc_client_channel, message)

    def run_service(self, message, callback):
        """Run the provided service.

        {
            "command": "RunService",
            "method": "GET",
            "queryParams": [ { key/value pairs } ],
            "headers": [ { key/value pairs } ],
            "bodySessionId": "85be2761..."
            "responseBodySessionId": "91eee889..."
        }

        Args:
            message (dict): The message received on the service channel.
            callback (callable): The function/method to call.  This method should take the
                following args (method, params, headers, body, response.
        """
        method = message.get('method')
        params = message.get('queryParams')
        headers = message.get('headers')

        # TODO: what is this and what is responseBody....
        body = message.get('bodySessionId')

        for config_id, params in self.configs:
            callback(method, params, headers, body, config_id, params)

    @property
    def session_id(self):
        """Return a uuid4 session id."""
        return str(uuid.uuid4())

    def shutdown(self):
        """Shut down service."""
        message = {'status': 'Acknowledged', 'type': 'Shutdown'}
        self.publish(json.dumps(message))
        self.p.unsubscribe(self.tcex.default_args.tc_server_channel)
        self.tcex.exit(
            0, 'A shutdown command was received on server channel. Service is shutting down.'
        )

    def update_config(self, config_id, params):
        """Add config item to service config object."""
        try:
            self.configs[config_id] = params

            response = {
                'status': 'Acknowledged',
                'type': 'UpdateConfig',
                'configId': config_id,
                'outputVariables': ['<string array of expected output variables for this config>'],
            }
            self.client.publish('channel', response)
        except Exception:
            self.tcex.log.error('Could not create config item.')

    def webhook_trigger(self, callback):
        """Add webhook subscriber

        {
          "command": "WebHookEvent",
          "requestKey": "abcdefghi",
          "method": "GET",
          "queryParams": [{"one': 1}],
          "headers": [{"one': 1}],
          "body": "variable"
        }

        Args:
            callback (callable): Method or function to call when webhook is triggered.
        """
        if not self.tcex.default_args.tc_server_channel:
            raise RuntimeError('No server channel provided.')
        if not callable(callback):
            raise RuntimeError('Callback method is not a callable.')

        p = self.client.pubsub()
        p.subscribe(self.tcex.default_args.tc_server_channel)
        for m in p.listen():
            # only process message on channel (exclude subscriptions)
            if m.get('type') != 'message':
                continue

            try:
                # load message data
                msg_data = json.loads(m.get('data'))
            except ValueError:
                self.tcex.log.warning('Cannot parse message ({}).'.format(m))
                continue

            session_id = str(uuid.uuid4())

            # parse message data contents
            command = msg_data.get('command')
            # parameters for config commands
            config_id = msg_data.get('configId')
            params = msg_data.get('params')
            request_key = msg_data.get('requestKey')

            if not command:
                self.tcex.log.warning('Received a message without command ({})'.format(m))
                continue
            elif command == 'CreateConfig':
                self.create_config(config_id, params)
            elif command == 'DeleteConfig':
                self.delete_config(config_id)
            elif command == 'UpdateConfig':
                self.update_config(config_id, params)
            elif command == 'Shutdown':
                self.tcex.log.info(
                    'A shutdown command was received on server channel. Service is shutting down.'
                )
                p.unsubscribe()
            elif command == 'WebHookEvent':
                body = msg_data.get('body')  # variable reference for REDIS lookup
                headers = msg_data.get('headers')
                method = msg_data.get('method')
                params = msg_data.get('queryParams')

                for config_id, config in self.configs:
                    if callback(session_id, method, params, headers, body, config):
                        self.publish(
                            {
                                'command': 'FireEvent',
                                'configId': config_id,  # reference to single playbook
                                'requestKey': request_key,  # reference to playbook execution
                                'sessionId': session_id,  # session Id where outputs are written
                            }
                        )
