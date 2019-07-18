# -*- coding: utf-8 -*-
"""TcEx Framework Service module"""
import base64
import json
import ssl
import threading
import time
import traceback
import uuid
from datetime import datetime

# py2to3 will convert this to "from io"
from StringIO import StringIO  # pylint: disable=import-error

import paho.mqtt.client as mqtt


class Service(object):
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
        self._connected = False
        self._metric = {'errors': 0, 'hits': 0, 'misses': 0}
        self._mqtt_client = None
        self._ready = False
        self._redis_client = None
        self._start_time = datetime.now()
        self.configs = {}
        self.config_thread = None
        self.heartbeat_max_misses = 3
        self.heartbeat_miss_count = 0
        self.heartbeat_sleep_time = 1
        self.heartbeat_watchdog = 0
        self.ready = False
        self.shutdown = False

        # config callbacks
        self.api_event_callback = None
        self.create_config_callback = None
        self.delete_config_callback = None
        self.update_config_callback = None
        self.shutdown_callback = None
        self.webhook_event_callback = None

    def add_metric(self, label, value):
        """Add a metric to get reported in heartbeat."""
        self._metric[label] = str(value)

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
            callback (callable): The trigger method in the App to call.
        """
        trigger_type = kwargs.get('trigger_type', 'trigger_event')
        self.tcex.log.info('Firing event for {} trigger'.format(trigger_type))
        if not callable(callback):
            raise RuntimeError('Callback method (callback) is not a callable.')

        for trigger_id, config in self.configs.items():
            try:
                self.tcex.log.trace('triggering callback for config id: {}'.format(trigger_id))
                # get a session_id specifically for this thread
                session_id = self.session_id
                session_logfile = self.session_logfile(session_id)

                # get instance of playbook specifically for this thread
                playbook = self.tcex.playbook
                # update the playbook hash/key/session_id and output_variables
                playbook.db.key = session_id
                playbook.output_variables = config.get('tc_playbook_out_variables', [])

                # TODO: change this to a new logger on its owns
                # add temporary logging file handler for this specific session
                self.tcex.logger.add_file_handler(name=session_id, filename=session_logfile)
                self.tcex.log.info('Trigger Session ID: {}'.format(session_id))

                if trigger_type == 'trigger_event':
                    args = (callback, playbook, session_id, trigger_id, config)
                    self.message_thread(self.fire_event_trigger, args, kwargs)
                elif trigger_type == 'webhook_event':
                    args = (
                        callback,
                        playbook,
                        session_id,
                        trigger_id,
                        config,
                        kwargs.get('message', {}),
                    )
                    self.message_thread(self.fire_event_webhook, args)
            except Exception:
                self.tcex.log.trace(traceback.format_exc())

    def fire_event_trigger(self, callback, playbook, session_id, trigger_id, config, **kwargs):
        """Fire event for trigger"""
        self.tcex.log.info('Firing event trigger {}'.format(type(callback)))
        try:
            if callback(playbook, trigger_id, config, **kwargs):
                self.metric['hits'] += 1
                # time.sleep(1)
                self.fire_event_publish(trigger_id, session_id)
            else:
                self.metric['misses'] += 1
        except Exception as e:
            self.tcex.log.error('The callback method encountered and error ({}).'.format(e))
            self.tcex.log.trace(traceback.format_exc())
            self.metric['errors'] += 1

        # TODO: close new logger
        # remove temporary logging file handler
        self.tcex.logger.remove_handler_by_name(session_id)

    def fire_event_webhook(self, callback, playbook, session_id, trigger_id, config, message):
        """Fire event for webhook trigger"""
        try:
            request_key = message.get('requestKey')
            body = self.redis_client.hget(request_key, 'request.body')
            if body is not None:
                body = json.loads(base64.b64decode(body))
            headers = message.get('headers')
            method = message.get('method')
            params = message.get('queryParams')
            if callback(playbook, method, headers, params, body, trigger_id, config):
                self.metric['hits'] += 1
                self.fire_event_publish(trigger_id, session_id, request_key)
            else:
                self.metric['misses'] += 1
        except Exception as e:
            self.tcex.log.error('The callback method encountered and error ({}).'.format(e))
            self.tcex.log.trace(traceback.format_exc())
            self.metric['errors'] += 1

        # TODO: close new logger
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

        # publish FireEvent command to client topic
        self.publish(json.dumps(msg))

    def format_query_string(self, params):
        """Convert name/value array to a query string."""
        query_string = ''
        try:
            for q in params:
                query_string += '{}={}'.format(q.get('name'), q.get('value'))
        except AttributeError as e:
            self.tcex.log.error('Bad params data provided {} ({})'.format(params, e))
            self.tcex.log.trace(traceback.format_exc())
        return query_string

    def format_request_headers(self, headers):
        """Convert name/value array to a query string."""
        headers_ = {}
        try:
            for h in headers:
                headers_.setdefault(h.get('name').lower(), []).append(h.get('value'))
        except AttributeError as e:
            self.tcex.log.error('Bad header data provided {} ({})'.format(headers, e))
            self.tcex.log.trace(traceback.format_exc())
        return headers_

    def format_response_headers(self, headers):
        """Convert name/value array to a query string."""
        headers_ = []
        try:
            for h in headers:
                headers_.append({'name': h[0], 'value': h[1]})
        except AttributeError as e:
            self.tcex.log.error('Bad header data provided {} ({})'.format(headers, e))
            self.tcex.log.trace(traceback.format_exc())
        return headers_

    def heartbeat(self):
        """Start heartbeat process."""
        self.tcex.log.info('Starting heartbeat threads.')

        # start heartbeat monitor thread
        t = threading.Thread(target=self.heartbeat_monitor)
        t.daemon = True  # use setter for py2
        t.start()

    def heartbeat_monitor(self):
        """Publish heartbeat on timer."""
        while True:
            if self.heartbeat_watchdog > (
                self.tcex.default_args.tc_svc_hb_timeout_seconds / self.heartbeat_sleep_time
            ):
                self.heartbeat_miss_count += 1
                self.tcex.log.warning('Missed {} heartbeats'.format(self.heartbeat_miss_count))
                self.heartbeat_watchdog = 0

            if self.heartbeat_miss_count >= self.heartbeat_max_misses:
                self.tcex.log.error('Missed server heartbeat message. Service is shutting down.')
                self.process_shutdown(
                    'Missed {} consecutive heartbeat commands.'.format(self.heartbeat_miss_count)
                )
                break

            time.sleep(self.heartbeat_sleep_time)
            self.heartbeat_watchdog += 1

    def listen(self):
        """List for message coming from broker."""
        self.tcex.log.trace('listen with broker {}'.format(self.tcex.args.tc_svc_broker_service))
        if self.tcex.args.tc_svc_broker_service.lower() == 'mqtt':
            target = self.listen_mqtt
        elif self.tcex.args.tc_svc_broker_service.lower() == 'redis':
            target = self.listen_redis

        t = threading.Thread(target=target, args=())
        t.daemon = True  # use setter for py2
        t.start()

    def listen_mqtt(self):
        """Listen for message coming from broker."""
        try:
            self.mqtt_client.on_connect = self.on_connect
            self.mqtt_client.on_message = self.on_message_mqtt

            # only needed when debugging
            # if self.tcex.log.getEffectiveLevel() == 5:
            #     # self.mqtt_client.on_disconnect = self.on_disconnect
            #     self.mqtt_client.on_publish = self.on_publish
            #     self.mqtt_client.on_subscribe = self.on_subscribe
            #     # self.mqtt_client.on_unsubscribe = self.on_unsubscribe
            #     self.mqtt_client.on_log = self.on_log
            self.mqtt_client.loop_forever()
        except Exception as e:
            self.tcex.log.trace('error in listen_mqtt: {}'.format(e))
            self.tcex.log.trace(traceback.format_exc())

    def listen_redis(self):
        """Listen for message coming from broker."""
        self.tcex.log.info(
            'Listening Redis topic {}'.format(self.tcex.default_args.tc_svc_server_topic)
        )
        p = self.redis_client.pubsub(ignore_subscribe_messages=True)
        p.subscribe(self.tcex.default_args.tc_svc_server_topic)
        for message in p.listen():
            self.on_message_redis(message)

    def loop_forever(self):
        """Block and wait for shutdown."""
        self.tcex.log.info('Looping until shutdown')
        while True:
            time.sleep(1)
            if self.shutdown is True:
                break

    def message_thread(self, target, args, kwargs=None):
        """Start a message thread."""
        self.tcex.log.trace('message thread: {} - {}'.format(type(target), args))
        try:
            t = threading.Thread(target=target, args=args, kwargs=kwargs)
            t.daemon = True  # use setter for py2
            t.start()
        except Exception:
            self.tcex.log.trace(traceback.format_exc())

    @property
    def metric(self):
        """Return current metrics."""
        self._metric['configs'] = len(self.configs)
        # self._metric['uptime'] = self.uptime
        return self._metric

    @property
    def mqtt_client(self):
        """Return the correct KV store for this execution."""
        if self._mqtt_client is None:
            try:
                self._mqtt_client = mqtt.Client(client_id='', clean_session=True)
                self.mqtt_client.connect(
                    self.tcex.args.tc_svc_broker_host,
                    int(self.tcex.args.tc_svc_broker_port),
                    int(self.tcex.args.tc_svc_broker_timeout),
                )
                self._mqtt_client.tls_set(
                    ca_certs=self.tcex.args.tc_svc_broker_cacert_file,
                    cert_reqs=ssl.CERT_REQUIRED,
                    tls_version=ssl.PROTOCOL_TLSv1_2,
                )
                # username must be a empty string
                self._mqtt_client.username_pw_set('', password=self.tcex.args.tc_svc_broker_token)
                self._mqtt_client.tls_insecure_set(False)
            except Exception as e:
                self.tcex.log.error('Failed connection to MQTT service ({})'.format(e))
                self.tcex.log.trace(traceback.format_exc())
                self.process_shutdown('Failure connecting to mqtt')

        return self._mqtt_client

    def on_connect(self, client, userdata, flags, rc):  # pylint: disable=unused-argument
        """On connect method for mqtt broker."""
        self.tcex.log.info('Message broker connection status: {}'.format(str(rc)))

        self.tcex.log.info(
            'Subscribing to topic: {}'.format(self.tcex.default_args.tc_svc_server_topic)
        )
        self.mqtt_client.subscribe(self.tcex.default_args.tc_svc_server_topic)
        self._connected = True

    def on_log(self, client, userdata, level, buf):  # pylint: disable=unused-argument
        """Handle MQTT on_log events."""
        self.tcex.log.trace('on_log - buf: {}, level: {}'.format(buf, level))

    def on_message_mqtt(self, client, userdata, message):  # pylint: disable=unused-argument
        """On message for mqtt."""
        self.tcex.log.trace('on_message - message.payload: {}'.format(message.payload))
        self.tcex.log.trace('on_message - message.topic: {}'.format(message.topic))
        try:
            # messages on server topic must be json objects
            m = json.loads(message.payload)
        except ValueError:
            self.tcex.log.warning('Cannot parse message ({}).'.format(m))
            return

        if message.topic == self.tcex.default_args.tc_svc_server_topic:
            self.server_topic(m)

    def on_message_redis(self, message):  # pylint: disable=unused-argument
        """Subscribe and listen to "message" on Redis topic."""
        self.tcex.log.trace('on_message - message {}'.format(message))
        # only process "message" on topic (exclude subscriptions, etc)
        if message.get('type') != 'message':
            return

        try:
            # load message data
            m = json.loads(message.get('data'))
        except ValueError:
            self.tcex.log.warning('Cannot parse message ({}).'.format(message))
            return
        self.server_topic(m)

    def on_publish(self, client, userdata, result):  # pylint: disable=unused-argument
        """Handle MQTT on_log events."""
        self.tcex.log.trace('on_publish - {}'.format(result))

    def on_subscribe(self, client, userdata, mid, granted_qos):  # pylint: disable=unused-argument
        """Handle MQTT on_log events."""
        self.tcex.log.trace('on_subscribe - mid: {}, granted_qos: {}'.format(mid, granted_qos))

    def process_config(self, command, config, trigger_id):
        """Process config message."""
        if command.lower() == 'createconfig':
            self.tcex.log.info(
                'CreateConfig - trigger_id: {} config : {}'.format(trigger_id, config)
            )
            if callable(self.create_config_callback):
                try:
                    # call callback for create config and handle exceptions to protect thread
                    self.create_config_callback(trigger_id, config)  # pylint: disable=not-callable
                except Exception as e:
                    self.tcex.log.error(
                        'The create config callback method encountered and error ({}).'.format(e)
                    )
                    self.tcex.log.trace(traceback.format_exc())
            self.create_config(trigger_id, config)
        elif command.lower() == 'deleteconfig':
            self.tcex.log.info('DeleteConfig - trigger_id: {}'.format(trigger_id))
            if callable(self.delete_config_callback):
                try:
                    # call callback for delete config and handle exceptions to protect thread
                    self.delete_config_callback(trigger_id)  # pylint: disable=not-callable
                except Exception as e:
                    self.tcex.log.error(
                        'The delete config callback method encountered and error ({}).'.format(e)
                    )
                    self.tcex.log.trace(traceback.format_exc())
            self.delete_config(trigger_id)
        elif command.lower() == 'updateconfig':
            self.tcex.log.trace(
                'UpdateConfig - trigger_id: {} config : {}'.format(trigger_id, config)
            )
            if callable(self.update_config_callback):
                try:
                    # call callback for update config and handle exceptions to protect thread
                    self.update_config_callback(trigger_id, config)  # pylint: disable=not-callable
                except Exception as e:
                    self.tcex.log.error(
                        'The update config callback method encountered and error ({}).'.format(e)
                    )
                    self.tcex.log.trace(traceback.format_exc())
            self.update_config(trigger_id, config)

    def process_run_service(self, message):
        """Process Webhook event messages.

        {
          "command": "RunService",
          "requestKey": "123abc",
          "method": "GET",
          "queryParams": [ { key/value pairs } ],
          "headers": [ { key/value pairs } ],
          "bodyVariable": "request.body"
        }
        """
        self.tcex.log.info('process request: {}'.format('message'))
        e = threading.Event()  # thread event
        request_key = message.get('requestKey')
        body = None
        # read body from redis
        try:
            body_variable = message.get('bodyVariable')
            if body_variable is not None:
                body = self.redis_client.hget(request_key, message.get('bodyVariable'))
                if body is not None:
                    body = StringIO(json.loads(base64.b64decode(body)))
        except Exception as e:
            self.tcex.log.error('Failed reading body to Redis ({})'.format(e))
            self.tcex.log.trace(traceback.format_exc())
        headers = self.format_request_headers(message.get('headers'))
        method = message.get('method')
        params = message.get('queryParams')
        path = message.get('path')

        try:
            environ = {
                'wsgi.errors': self.tcex.log.error,  # sys.stderr
                # 'wsgi.file_wrapper': <class 'wsgiref.util.FileWrapper'>
                'wsgi.input': body,
                'wsgi.multithread': True,
                'wsgi.multiprocess': False,
                'wsgi.run_once': True,
                'wsgi.url_scheme': 'https',
                'wsgi.version': (1, 0),
                'CONTENT_TYPE': headers.get('content-type', ''),
                'CONTENT_LENGTH': headers.get('content-length', 0),
                # 'GATEWAY_INTERFACE': 'CGI/1.1',
                # 'HTTP_ACCEPT': '',
                'HTTP_ACCEPT': headers.get('accept', ''),
                # 'HTTP_ACCEPT_ENCODING': '',
                # 'HTTP_ACCEPT_LANGUAGE': '',
                # 'HTTP_COOKIE': '',
                # 'HTTP_DNT': 1,
                # 'HTTP_CONNECTION': 'keep-alive',
                # 'HTTP_HOST': '',
                # 'HTTP_UPGRADE_INSECURE_REQUESTS': 1,
                'HTTP_USER_AGENT': headers.get('user-agent', ''),
                'PATH_INFO': path,
                'QUERY_STRING': self.format_query_string(params),
                # 'REMOTE_ADDR': '',
                # 'REMOTE_HOST': '',
                'REQUEST_METHOD': method.upper(),
                'SCRIPT_NAME': '/',
                # 'SERVER_NAME': '',
                # 'SERVER_PORT': '',
                'SERVER_PROTOCOL': 'HTTP/1.1',
                # 'SERVER_SOFTWARE': 'WSGIServer/0.2',
            }
        except Exception as e:
            self.tcex.log.error('Failed building environ ({})'.format(e))
            self.tcex.log.trace(traceback.format_exc())

        def response_handler(*args, **kwargs):  # pylint: disable=unused-argument
            """Handle WSGI Response"""
            kwargs['e'] = e
            kwargs['request_key'] = request_key
            t = threading.Thread(target=self.process_run_service_response, args=args, kwargs=kwargs)
            t.daemon = True  # use setter for py2
            t.start()

        if callable(self.api_event_callback):
            try:
                self.redis_client.hset(request_key, 'response.ready', 0)
                body = self.api_event_callback(  # pylint: disable=not-callable
                    environ, response_handler
                )

                # decode body entries
                # TODO: validate this logic
                body = [base64.b64encode(b).decode('utf-8') for b in body][0]
                # write body to Redis
                self.redis_client.hset(request_key, 'response.body', json.dumps(body))
                self.tcex.log.trace('body written')
                e.set()
            except Exception as e:
                self.tcex.log.error(
                    'The api event callback method encountered and error ({}).'.format(e)
                )
                self.tcex.log.trace(traceback.format_exc())

    def process_run_service_response(self, *args, **kwargs):
        """Handle service event responses.

        ('200 OK', [('content-type', 'application/json'), ('content-length', '103')])
        """
        kwargs.get('e').wait(10)  # wait until body has been written
        self.tcex.log.trace('args: {}'.format(args))
        response = {}
        try:
            status_code, status = args[0].split(' ', 1)
            response = {
                'bodyVariable': 'response.body',
                'command': 'Acknowledge',
                'headers': self.format_response_headers(args[1]),
                'requestKey': kwargs.get('request_key'),  # pylint: disable=cell-var-from-loop
                'status': status,
                'statusCode': status_code,
                'type': 'RunService',
            }
            self.tcex.log.debug('API service response: {}'.format(response))
        except Exception as e:
            self.tcex.log.error('Failed creating response body ({})'.format(e))
            self.tcex.log.trace(traceback.format_exc())
            return
        self.publish(json.dumps(response))

    def process_shutdown(self, reason):
        """Handle a shutdown message."""
        reason = reason or (
            'A shutdown command was received on server topic. Service is shutting down.'
        )
        self.tcex.log.info('Shutdown - reason: {}'.format(reason))

        # acknowledge shutdown command
        self.publish(json.dumps({'status': 'Acknowledged', 'command': 'Shutdown'}))

        # call App shutdown callback
        if callable(self.shutdown_callback):
            try:
                # call callback for shutdown and handle exceptions to protect thread
                self.shutdown_callback()  # pylint: disable=not-callable
            except Exception as e:
                self.tcex.log.error(
                    'The shutdown callback method encountered and error ({}).'.format(e)
                )
                self.tcex.log.trace(traceback.format_exc())

        # unsubscribe and disconnect from the broker
        if self.tcex.args.tc_svc_broker_service.lower() == 'mqtt':
            self.mqtt_client.unsubscribe(self.tcex.default_args.tc_svc_server_topic)
            self.mqtt_client.disconnect()

        # delay shutdown to give App time to cleanup
        self.shutdown = True
        time.sleep(5)
        self.tcex.exit(0)  # final shutdown in case App did not

    def process_webhook(self, message):
        """Process Webhook event messages."""
        self.tcex.log.trace('webhook event')
        self.fire_event(self.webhook_event_callback, message=message, trigger_type='webhook_event')

    def publish(self, message, topic=None):
        """Publish a message on client topic.

        Args:
            message (str): The message to be sent on client topic.
        """
        if topic is None:
            topic = self.tcex.default_args.tc_svc_client_topic
        self.tcex.log.debug('topic: ({})'.format(topic))
        self.tcex.log.debug('message: ({})'.format(message))

        if self.tcex.args.tc_svc_broker_service.lower() == 'mqtt':
            r = self.mqtt_client.publish(topic, message)
            self.tcex.log.trace('publish response: {}'.format(r))
        elif self.tcex.args.tc_svc_broker_service.lower() == 'redis':
            self.redis_client.publish(topic, message)

    @property
    def ready(self):
        """Return ready boolean."""
        return self._ready

    @ready.setter
    def ready(self, bool_val):
        """Set ready boolean."""
        if isinstance(bool_val, bool) and bool_val is True:
            # wait until connected to send ready command
            while not self._connected:
                if self.shutdown:
                    break
                time.sleep(1)
            else:  # pylint: disable=useless-else-on-loop
                self.tcex.log.info('Service is Ready')
                self.publish(json.dumps({'command': 'Ready'}))
                self._ready = True

    @property
    def redis_client(self):
        """Return the correct KV store for this execution."""
        if self._redis_client is None:
            self._redis_client = self.tcex.playbook.db.client
        return self._redis_client

    def server_topic(self, message):
        """Handle any event coming in on server_topic."""
        self.tcex.log.trace('message: {}'.format(message))
        # parse the command type
        command = message.get('command')

        self.tcex.log.info('Command received: {}'.format(command))
        if command.lower() == 'webhookevent':
            self.message_thread(self.process_webhook, (message,))
        elif command.lower() == 'heartbeat':
            self.heartbeat_watchdog = 0
            self.heartbeat_miss_count = 0

            # send heartbeat -acknowledge- command
            response = {'command': 'Heartbeat', 'metric': self.metric}
            self.publish(json.dumps(response))
            self.tcex.log.info('Heartbeat command sent')
            self.tcex.log.debug('metric: {}'.format(self.metric))
        elif command.lower() == 'loggingchange':
            # {"command": "LoggingChange", "level": "DEBUG"}
            level = message.get('level')
            self.tcex.log.info('LoggingChange - level: {}'.format(level))
            self.tcex.logger.update_handler_level(level)
        elif command.lower() == 'runservice':
            self.message_thread(self.process_run_service, (message,))
        elif command.lower() == 'shutdown':
            # {"command": "Shutdown", "reason": "Service disabled by user."}
            reason = message.get('reason')
            self.process_shutdown(reason)
        else:
            # any other message is a config message
            config = message.get('config', {})
            self.message_thread(self.process_config, (command, config, message.get('triggerId')))

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
