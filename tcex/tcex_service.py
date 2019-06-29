# -*- coding: utf-8 -*-
"""TcEx Framework Service module"""
import json
import threading
import time
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

        # properties
        self._client = None
        self._metric = {'hits': 0, 'misses': 0}
        self.configs = {}
        self.default_handlers = self.tcex.log.handlers

    # def api_service(self, callback):
    #     """Run subscribe method

    #     {
    #       "command": "RunService",
    #       "requestKey": "123abc",
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
    #         # only process "message" on channel (exclude subscriptions)
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
    #             self.delete_config(config_id, config)
    #         elif command == 'UpdateConfig':
    #             self.update_config(config_id, params)
    #         elif command == 'Shutdown':
    #             self.tcex.log.info(
    #                 'A shutdown command was received on server channel. Service is shutting down.'
    #             )
    #             p.unsubscribe()
    #             time.sleep(5)  # give app time to cleanup
    #             self.tcex.exit(0)
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

    def create_config(self, config_id, config):
        """Add config item to service config object."""
        try:
            self.configs[config_id] = config

            # send ack response
            response = {'status': 'Acknowledged', 'type': 'CreateConfig', 'configId': config_id}
            self.publish(json.dumps(response))
        except Exception as e:
            self.tcex.log.error('Could not create config for Id {} ({}).'.format(config_id, e))

    def custom_trigger(
        self,
        create_callback=None,
        delete_callback=None,
        update_callback=None,
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
        if not self.tcex.default_args.tc_server_channel:
            raise RuntimeError('No server channel provided.')

        # start heartbeat
        self.heartbeat()

        self.tcex.log.trace('custom trigger initialized.')
        t = threading.Thread(
            target=self.custom_trigger_subscriber,
            args=(create_callback, delete_callback, update_callback, shutdown_callback),
        )
        t.daemon = True  # use setter for py2
        t.start()

    def custom_trigger_subscriber(
        self,
        create_callback=None,
        delete_callback=None,
        update_callback=None,
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

        self.tcex.log.trace('custom trigger subscriber thread started.')

        p = self.client.pubsub()
        p.subscribe(self.tcex.default_args.tc_server_channel)
        for m in p.listen():
            self.tcex.log.trace('message: ({})'.format(m))
            # only process "message" on channel (exclude subscriptions, etc)
            if m.get('type') != 'message':
                continue

            try:
                # load message data
                msg_data = json.loads(m.get('data'))
            except ValueError:
                self.tcex.log.warning('Cannot parse message ({}).'.format(m))
                continue

            # parse message data contents
            command = msg_data.get('command')
            # parameters for config commands
            config_id = msg_data.get('configId')
            config = msg_data.get('config')

            if not command:
                self.tcex.log.warning('Received a message without command ({})'.format(m))
                continue

            # process config message
            self.process_config_message(
                p=p,
                command=command,
                config=config,
                config_id=config_id,
                create_callback=create_callback,
                delete_callback=delete_callback,
                update_callback=update_callback,
                shutdown_callback=shutdown_callback,
            )

    def delete_config(self, config_id, config):  # pylint: disable=unused-argument
        """Delete config item from config object."""
        try:
            del self.configs[config_id]

            # send ack response
            response = {'status': 'Acknowledged', 'type': 'DeleteConfig', 'configId': config_id}
            self.publish(json.dumps(response))
        except Exception as e:
            self.tcex.log.error('Could not delete config for Id {} ({}).'.format(config_id, e))

    def fire_event(self, callback, **kwargs):
        """Trigger a FireEvent command.

        Args:
            trigger_type (str, kwargs): Defaults to custom. The trigger type.
            trigger_callback (str, kwargs): The trigger callback method.
        """
        if not callable(callback):
            raise RuntimeError('Callback method (trigger_callback) is not a callable.')

        trigger_type = kwargs.get('trigger_type')
        if trigger_type is None:
            trigger_type = 'custom'  # default to custom

        for config_id, config in self.configs.items():
            self.tcex.log.trace('trigger callback for config id: {}'.format(config_id))

            # generate session id
            session_id = str(uuid.uuid4())
            self.tcex.logger.add_file_handler(name=session_id, filename='{}.log'.format(session_id))
            self.tcex.log.info('Trigger Session ID: {}'.format(session_id))

            if trigger_type == 'custom':
                if callback(session_id, config, **kwargs):
                    self.metric['hits'] += 1
                    self.fire_event_publish(config_id, session_id)
                else:
                    self.metric['misses'] += 1
            elif trigger_type == 'webhook':
                msg_data = kwargs.get('msg_data')
                request_key = kwargs.get('request_key')

                # TODO: this could possibly be REDIS reference
                body = msg_data.get('body')
                headers = msg_data.get('headers')
                method = msg_data.get('method')
                params = msg_data.get('queryParams')
                if callback(session_id, method, headers, params, body, config):
                    self.metric['hits'] += 1
                    self.fire_event_publish(config_id, session_id, request_key)
                else:
                    self.metric['misses'] += 1
            self.tcex.logger.remove_handler_by_name(session_id)

    def fire_event_publish(self, config_id, session_id, request_key=None):
        """Send FireEvent command"""
        msg = {
            'command': 'FireEvent',
            'configId': config_id,  # reference to single playbook
            'sessionId': session_id,  # session for the playbook execution
        }
        if request_key is not None:
            msg['requestKey'] = request_key  # reference for a specific playbook execution

        # publish FireEvent command to client channel
        self.publish(json.dumps(msg))

    def heartbeat(self):
        """Start heartbeat process."""
        self.tcex.log.info('Starting heartbeat thread.')
        t = threading.Thread(target=self.heartbeat_publish)
        t.daemon = True  # use setter for py2
        t.start()

    def heartbeat_publish(self):
        """Publish heartbeat on timer."""
        while True:
            time.sleep(self.tcex.default_args.tc_heartbeat_seconds)
            response = {'command': 'Heartbeat', 'metric': self.metric}
            self.publish(json.dumps(response))
            self.tcex.log.info('Heartbeat command sent')
            self.tcex.log.debug('metric: {}'.format(self.metric))

    @property
    def metric(self):
        """Return current metrics."""
        self._metric['config'] = len(self.configs)
        return self._metric

    def process_config_message(
        self,
        p,
        command,
        config,
        config_id,
        create_callback=None,
        delete_callback=None,
        update_callback=None,
        shutdown_callback=None,
    ):
        """Process config message."""
        self.tcex.log.trace('in process config message')
        if command == 'CreateConfig':
            self.tcex.log.trace('process config CreateConfig')
            self.create_config(config_id, config)
            if callable(create_callback):
                create_callback(config_id, config)
        elif command == 'DeleteConfig':
            self.tcex.log.trace('process config DeleteConfig')
            self.delete_config(config_id, config)
            if callable(delete_callback):
                delete_callback(config_id, config)
        elif command == 'UpdateConfig':
            self.tcex.log.trace('process config UpdateConfig')
            self.update_config(config_id, config)
            if callable(update_callback):
                update_callback(config_id, config)
        elif command == 'Shutdown':
            self.tcex.log.trace('process config Shutdown')
            message = {'status': 'Acknowledged', 'type': 'Shutdown'}
            self.publish(json.dumps(message))
            self.tcex.log.info(
                'A shutdown command was received on server channel. Service is shutting down.'
            )
            if callable(shutdown_callback):
                shutdown_callback()
            p.unsubscribe()
            time.sleep(5)  # give app time to cleanup and exit on it's own
            self.tcex.exit(0)

    def publish(self, message):
        """Publish a message on client channel.

        Args:
            message (str): The message to be sent on client channel.
        """
        self.tcex.log.trace('message: ({})'.format(message))
        self.client.publish(self.tcex.default_args.tc_client_channel, message)

    # def run_service(self, message, callback):
    #     """Run the provided service.

    #     {
    #         "command": "RunService",
    #         "method": "GET",
    #         "queryParams": [ { key/value pairs } ],
    #         "headers": [ { key/value pairs } ],
    #         "bodySessionId": "85be2761..."
    #         "responseBodySessionId": "91eee889..."
    #     }

    #     Args:
    #         message (dict): The message received on the service channel.
    #         callback (callable): The function/method to call.  This method should take the
    #             following args (method, params, headers, body, response.
    #     """
    #     method = message.get('method')
    #     params = message.get('queryParams')
    #     headers = message.get('headers')

    #     # TODO: what is this and what is responseBody....
    #     body = message.get('bodySessionId')

    #     for config_id, config in self.configs:
    #         callback(method, params, headers, body, config_id, config)

    @property
    def session_id(self):
        """Return a uuid4 session id."""
        return str(uuid.uuid4())

    # def shutdown(self):
    #     """Shut down service."""
    #     message = {'status': 'Acknowledged', 'type': 'Shutdown'}
    #     self.publish(json.dumps(message))
    #     # self.p.unsubscribe(self.tcex.default_args.tc_server_channel)
    #     self.tcex.exit(
    #         0, 'A shutdown command was received on server channel. Service is shutting down.'
    #     )

    def update_config(self, config_id, config):
        """Add config item to service config object."""
        try:
            # self.configs[config_id] = config
            self.configs[config_id] = config.get('current')

            # send ack response
            response = {'status': 'Acknowledged', 'type': 'UpdateConfig', 'configId': config_id}
            self.publish(json.dumps(response))
        except Exception as e:
            self.tcex.log.error('Could not update config for Id {} ({}).'.format(config_id, e))

    def webhook_trigger(
        self,
        callback,
        create_callback=None,
        delete_callback=None,
        update_callback=None,
        shutdown_callback=None,
    ):
        """Add webhook subscriber

        {
          "command": "WebHookEvent",
          "requestKey": "123abc",
          "method": "GET",
          "queryParams": [{"one': 1}],
          "headers": [{"one': 1}],
          "body": "variable"
        }

        Args:
            callback (callable): Method or function to call when webhook is triggered.
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
            raise RuntimeError('No server channel provided.')
        if not callable(callback):
            raise RuntimeError('Callback method is not a callable.')

        # start heartbeat
        self.heartbeat()

        # subscribe to redis channel
        p = self.client.pubsub()
        p.subscribe(self.tcex.default_args.tc_server_channel)
        for m in p.listen():
            self.tcex.log.trace('message: ({})'.format(m))
            # only process "message" on channel (exclude subscriptions, etc)
            if m.get('type') != 'message':
                continue

            try:
                # load message data
                msg_data = json.loads(m.get('data'))
            except ValueError:
                self.tcex.log.warning('Cannot parse message ({}).'.format(m))
                continue
            self.tcex.log.trace('msg_data: ({})'.format(msg_data))

            # parse message data contents
            command = msg_data.get('command')
            # parameters for config commands
            config_id = msg_data.get('configId')
            config = msg_data.get('config')

            self.tcex.log.trace('command: ({})'.format(command))
            self.tcex.log.trace('config_id: ({})'.format(config_id))
            self.tcex.log.trace('config: ({})'.format(config))
            if not command:
                self.tcex.log.warning('Received a message without command ({})'.format(m))
                continue
            elif command == 'WebHookEvent':
                self.tcex.log.trace('webhookevent triggered')

                request_key = msg_data.get('requestKey')
                self.tcex.log.trace('request_key: ({})'.format(request_key))
                self.fire_event(
                    callback, msg_data=msg_data, request_key=request_key, trigger_type='webhook'
                )
            else:
                self.tcex.log.trace('calling process config message')
                self.process_config_message(
                    p=p,
                    command=command,
                    config=config,
                    config_id=config_id,
                    create_callback=create_callback,
                    delete_callback=delete_callback,
                    update_callback=update_callback,
                    shutdown_callback=shutdown_callback,
                )
