# -*- coding: utf-8 -*-
"""TcEx Framework Service module"""
import base64
import json
import threading
import time
import traceback
import uuid
from datetime import datetime


class ServiceBase(object):
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
        self._metric = {'errors': 0, 'hits': 0, 'misses': 0}
        self._pubsub = None
        self._start_time = datetime.now()
        self.configs = {}
        self.config_thread = None
        self.heartbeat_client = None
        self.heartbeat_server = None
        self.ready = False

    def add_metric(self, label, value):
        """Add a metric to get reported in heartbeat."""
        self._metric[label] = str(value)

    @property
    def client(self):
        """Return the correct KV store for this execution."""
        return self.tcex.playbook.db.client

    def create_config(self, trigger_id, config):
        """Add config item to service config object."""
        try:
            self.tcex.log.trace('trigger_id: {}'.format(trigger_id))
            self.tcex.log.trace('config: {}'.format(config))
            self.configs[trigger_id] = config

            # send ack response
            response = {
                'status': 'Acknowledged',
                'command': 'CreateConfig',
                'triggerId': trigger_id,
            }
            self.publish(json.dumps(response))
        except Exception as e:
            self.tcex.log.error('Could not create config for Id {} ({}).'.format(trigger_id, e))

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

        self.tcex.log.trace('initialized')
        self.config_thread = threading.Thread(
            target=self.custom_trigger_subscriber,
            args=(create_callback, delete_callback, update_callback, shutdown_callback),
        )
        self.config_thread.daemon = True  # use setter for py2
        self.config_thread.start()

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

        self.tcex.log.trace('subscriber thread started.')

        p = self.client.pubsub()
        p.subscribe(self.tcex.default_args.tc_server_channel)
        for m in p.listen():
            self.tcex.log.trace('server message: ({})'.format(m))

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
            trigger_id = msg_data.get('triggerId')
            config = msg_data.get('config')

            if not command:
                self.tcex.log.warning('Received a message without command ({})'.format(m))
                continue

            if command == 'Shutdown':
                p.unsubscribe(self.tcex.default_args.tc_server_channel)
                break

            # process config message
            self.process_message(
                command=command,
                config=config,
                trigger_id=trigger_id,
                create_callback=create_callback,
                delete_callback=delete_callback,
                update_callback=update_callback,
                shutdown_callback=shutdown_callback,
            )

        # final process config command after shutdown
        self.tcex.log.trace('final process command')
        if command == 'Shutdown':
            self.process_message(
                command=command,
                config=config,
                trigger_id=trigger_id,
                create_callback=create_callback,
                delete_callback=delete_callback,
                update_callback=update_callback,
                shutdown_callback=shutdown_callback,
            )

    def delete_config(self, trigger_id):
        """Delete config item from config object."""
        try:
            del self.configs[trigger_id]

            # send ack response
            response = {
                'status': 'Acknowledged',
                'command': 'DeleteConfig',
                'triggerId': trigger_id,
            }
            self.publish(json.dumps(response))
        except Exception as e:
            self.tcex.log.error('Could not delete config for Id {} ({}).'.format(trigger_id, e))

    def fire_event(self, callback, **kwargs):
        """Trigger a FireEvent command.

        Args:
            trigger_type (str, kwargs): Defaults to custom. The trigger type.
            trigger_callback (str, kwargs): The trigger callback method.
        """
        if not callable(callback):
            raise RuntimeError('Callback method (callback) is not a callable.')

        trigger_type = kwargs.get('trigger_type')
        if trigger_type is None:
            trigger_type = 'custom'  # default to custom

        for trigger_id, config in self.configs.items():
            self.tcex.log.trace('triggering callback for config id: {}'.format(trigger_id))
            session_id = self.session_id
            session_logfile = self.session_logfile(session_id)

            # update the playbook session id and outputVariables
            self.tcex.playbook.db.key = session_id
            self.tcex.log.trace('config: {}'.format(config))
            self.tcex.playbook.output_variables = config.get('tc_playbook_out_variables', [])

            # add temporary logging file handler for this specific session
            self.tcex.logger.add_file_handler(name=session_id, filename=session_logfile)
            self.tcex.log.info('Trigger Session ID: {}'.format(session_id))

            if trigger_type == 'custom':
                try:
                    if callback(trigger_id, config, **kwargs):
                        self.metric['hits'] += 1
                        # time.sleep(1)
                        self.fire_event_publish(trigger_id, session_id)
                    else:
                        self.metric['misses'] += 1
                except Exception as e:
                    self.tcex.log.error('The callback method encountered and error ({}).'.format(e))
                    self.tcex.log.trace(traceback.format_exc())
                    self.metric['errors'] += 1
            elif trigger_type == 'webhook':
                msg_data = kwargs.get('msg_data')
                request_key = kwargs.get('request_key')

                # TODO: this could possibly be REDIS reference
                body = self.client.hget(request_key, 'request.body')
                if body is not None:
                    body = json.loads(base64.b64decode(body))
                headers = msg_data.get('headers')
                method = msg_data.get('method')
                params = msg_data.get('queryParams')
                try:
                    if callback(method, headers, params, body, trigger_id, config):
                        self.metric['hits'] += 1
                        # time.sleep(1)
                        self.fire_event_publish(trigger_id, session_id, request_key)
                    else:
                        self.metric['misses'] += 1
                except Exception as e:
                    self.tcex.log.error('The callback method encountered and error ({}).'.format(e))
                    self.tcex.log.trace(traceback.format_exc())
                    self.metric['errors'] += 1

            # remove temporary logging file handler
            self.tcex.logger.remove_handler_by_name(session_id)

    def fire_event_publish(self, trigger_id, session_id, request_key=None):
        """Send FireEvent command"""
        msg = {
            'command': 'FireEvent',
            'triggerId': trigger_id,  # reference to single playbook
            'sessionId': session_id,  # session for the playbook execution
        }
        if request_key is not None:
            msg['requestKey'] = request_key  # reference for a specific playbook execution

        self.tcex.log.info('Firing Event ({})'.format(msg))

        # publish FireEvent command to client channel
        self.publish(json.dumps(msg))

    def heartbeat(self):
        """Start heartbeat process."""
        self.tcex.log.info('Starting heartbeat threads.')

        # publish ready command
        if self.ready is False:
            self.publish(json.dumps({'command': 'Ready'}))
            self.ready = True

        # Server Heartbeat
        self.heartbeat_server = threading.Thread(target=self.heartbeat_subscribe)
        self.heartbeat_server.daemon = True  # use setter for py2
        self.heartbeat_server.start()

        # Client Heartbeat
        self.heartbeat_client = threading.Thread(target=self.heartbeat_publish)
        self.heartbeat_client.daemon = True  # use setter for py2
        self.heartbeat_client.start()

    def heartbeat_subscribe(self):
        """Publish heartbeat on timer."""
        p = self.client.pubsub()
        p.subscribe(self.tcex.default_args.tc_server_channel)

        # heartbeat settings
        sleep_time = 0.001
        watchdog = 0
        missed_heartbeat = 0
        max_missed_heartbeat = 3

        while True:
            if watchdog > (self.tcex.default_args.tc_heartbeat_seconds / sleep_time):
                missed_heartbeat += 1
                watchdog = 0

            if missed_heartbeat >= max_missed_heartbeat:
                self.tcex.log.error('Missed server heartbeat message. Service is shutting down.')
                # send shutdown command to server channel
                shutdown_command = {
                    'command': 'Shutdown',
                    'config': {
                        'reason': 'Missed {} consecutive heartbeat commands.'.format(
                            missed_heartbeat
                        )
                    },
                }
                self.publish(json.dumps(shutdown_command), self.tcex.default_args.tc_server_channel)
                p.unsubscribe(self.tcex.default_args.tc_server_channel)
                break

            # if watchdog % 1000 == 0:
            #     self.tcex.log.trace('watchdog count: {}'.format(watchdog))

            m = p.get_message()
            if m and m.get('type') == 'message':
                # self.tcex.log.trace('server message: ({})'.format(m))
                # only process "message" on channel (exclude subscriptions, etc)

                try:
                    # load message data
                    msg_data = json.loads(m.get('data'))
                except ValueError:
                    self.tcex.log.warning('Cannot parse message ({}).'.format(m))
                    continue

                # parse message data contents
                command = msg_data.get('command')
                if command == 'Heartbeat':
                    self.tcex.log.info('Heartbeat command received')
                    # reset watchdog timer
                    missed_heartbeat = 0
                    watchdog = 0
            time.sleep(sleep_time)
            watchdog += 1

    def heartbeat_publish(self):
        """Publish heartbeat on timer."""
        while True:
            # if self.shutdown:
            #     break
            time.sleep(self.tcex.default_args.tc_heartbeat_seconds)
            response = {'command': 'Heartbeat', 'metric': self.metric}
            self.publish(json.dumps(response))
            self.tcex.log.info('Heartbeat command sent')
            self.tcex.log.debug('metric: {}'.format(self.metric))

    @property
    def metric(self):
        """Return current metrics."""
        self._metric['configs'] = len(self.configs)
        # self._metric['uptime'] = self.uptime
        return self._metric

    def process_message(
        self,
        command,
        config,
        trigger_id,
        create_callback=None,
        delete_callback=None,
        update_callback=None,
        shutdown_callback=None,
    ):
        """Process config message."""
        if command == 'CreateConfig':
            self.tcex.log.info(
                'CreateConfig - trigger_id: {} config : {}'.format(trigger_id, config)
            )
            if callable(create_callback):
                try:
                    # call callback for create config and handle exceptions to protect thread
                    create_callback(trigger_id, config)
                except Exception as e:
                    self.tcex.log.error(
                        'The create config callback method encountered and error ({}).'.format(e)
                    )
                    self.tcex.log.trace(traceback.format_exc())
            self.create_config(trigger_id, config)
        elif command == 'DeleteConfig':
            self.tcex.log.info('DeleteConfig - trigger_id: {}'.format(trigger_id))
            if callable(delete_callback):
                try:
                    # call callback for delete config and handle exceptions to protect thread
                    delete_callback(trigger_id)
                except Exception as e:
                    self.tcex.log.error(
                        'The delete config callback method encountered and error ({}).'.format(e)
                    )
                    self.tcex.log.trace(traceback.format_exc())
            self.delete_config(trigger_id)
        elif command == 'LoggingChange':
            level = config.get('level')
            self.tcex.log.info('LoggingChange - level: {}'.format(level))
            self.tcex.logger.update_handler_level(level)
        elif command == 'UpdateConfig':
            self.tcex.log.trace(
                'UpdateConfig - trigger_id: {} config : {}'.format(trigger_id, config)
            )
            if callable(update_callback):
                try:
                    # call callback for update config and handle exceptions to protect thread
                    update_callback(trigger_id, config)
                except Exception as e:
                    self.tcex.log.error(
                        'The update config callback method encountered and error ({}).'.format(e)
                    )
                    self.tcex.log.trace(traceback.format_exc())
            self.update_config(trigger_id, config)
        elif command == 'Shutdown':
            reason = (
                'A shutdown command was received on server channel. Service is shutting down.',
            )
            if config:
                reason = config.get('reason') or reason
            self.tcex.log.info('Shutdown - reason: {}'.format(reason))

            # cleanup heartbeat thread
            # self.shutdown = True  # set shutdown to True so heartbeat loop will break

            # acknowledge shutdown command
            self.publish(json.dumps({'status': 'Acknowledged', 'command': 'Shutdown'}))

            # call App shutdown callback
            if callable(shutdown_callback):
                try:
                    # call callback for shutdown and handle exceptions to protect thread
                    shutdown_callback()
                except Exception as e:
                    self.tcex.log.error(
                        'The shutdown callback method encountered and error ({}).'.format(e)
                    )
                    self.tcex.log.trace(traceback.format_exc())

            # give App time to cleanup and shutdown
            time.sleep(5)
            self.tcex.exit(0)  # final shutdown in case App did not

    def publish(self, message, channel=None):
        """Publish a message on client channel.

        Args:
            message (str): The message to be sent on client channel.
        """
        if channel is None:
            channel = self.tcex.default_args.tc_client_channel
        self.tcex.log.debug('channel: ({})'.format(channel))
        self.tcex.log.debug('message: ({})'.format(message))
        self.client.publish(channel, message)

    @property
    def session_id(self):
        """Return a uuid4 session id."""
        return str(uuid.uuid4())

    @staticmethod
    def session_logfile(session_id):
        """Return a uuid4 session id."""
        return '{}/{}.log'.format(datetime.today().strftime('%Y%m%d'), session_id)

    def update_config(self, trigger_id, config):
        """Add config item to service config object."""
        try:
            self.configs[trigger_id] = config

            # send ack response
            response = {
                'status': 'Acknowledged',
                'command': 'UpdateConfig',
                'triggerId': trigger_id,
            }
            self.publish(json.dumps(response))
        except Exception as e:
            self.tcex.log.error('Could not update config for Id {} ({}).'.format(trigger_id, e))

    # @property
    # def uptime(self):
    #     """Return the current uptime of the microservice."""
    #     return str(datetime.now() - self._start_time)

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
          "command": "WebhookEvent",
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
            self.tcex.log.trace('server message: ({})'.format(m))

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
            trigger_id = msg_data.get('triggerId')
            config = msg_data.get('config')

            self.tcex.log.trace('command: ({})'.format(command))
            self.tcex.log.trace('trigger_id: ({})'.format(trigger_id))
            self.tcex.log.trace('config: ({})'.format(config))
            if not command:
                self.tcex.log.warning('Received a message without command ({})'.format(m))
                continue
            elif command.lower() == 'webhookevent':
                request_key = msg_data.get('requestKey')
                self.tcex.log.info(
                    'WebhookEvent - trigger_id: {} request_key : {}'.format(trigger_id, request_key)
                )
                self.fire_event(
                    callback,
                    trigger_id=trigger_id,
                    msg_data=msg_data,
                    request_key=request_key,
                    trigger_type='webhook',
                )
            else:
                self.process_message(
                    command=command,
                    config=config,
                    trigger_id=trigger_id,
                    create_callback=create_callback,
                    delete_callback=delete_callback,
                    update_callback=update_callback,
                    shutdown_callback=shutdown_callback,
                )
