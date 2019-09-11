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


class Services(object):
    """Service methods for customer Service (e.g., Triggers).

    Args:
        tcex (object): Instance of TcEx.
    """

    def __init__(self, tcex):
        """Initialize the Class properties."""
        self.tcex = tcex
        self.log = self.tcex.log

        # properties
        self._client = None
        self._connected = False
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

        # default metrics per service type
        if self.tcex.ij.runtime_level.lower() in ['triggerservice', 'webhooktriggerservice']:
            self._metrics = {'active playbooks': 0, 'errors': 0, 'hits': 0, 'misses': 0}
        else:
            self._metrics = {'errors': 0, 'requests': 0, 'responses': 0}

        # config callbacks
        self.api_event_callback = None
        self.create_config_callback = None
        self.delete_config_callback = None
        self.update_config_callback = None
        self.shutdown_callback = None
        self.webhook_event_callback = None

    def add_metric(self, label, value):
        """Add a metric.

        Metrics are reported in heartbeat message.

        Args:
            label (str): The metric label (e.g., hits) to add.
            value (int|str): The value for the metric.
        """
        self._metrics[label] = value

    def create_config(self, trigger_id, config, message, status):
        """Add config item to service config object.

        Args:
            trigger_id (int): The trigger ID for the current config.
            config (dict): The config for the current trigger.
            message (str): A simple message for the action.
            status (str): The passed/fail status for the App handling of config.
        """
        try:
            # add config to configs
            self.configs[trigger_id] = config

            # send ack response
            response = {
                'command': 'Acknowledged',
                'message': message,
                'status': status,
                'type': 'CreateConfig',
                'triggerId': trigger_id,
            }
            self.publish(json.dumps(response))
        except Exception as e:
            self.tcex.log.error('Could not create config for Id {} ({}).'.format(trigger_id, e))
            self.tcex.log.trace(traceback.format_exc())

    def delete_config(self, trigger_id, message, status):
        """Delete config item from config object.

        Args:
            trigger_id (int): The trigger ID for the current config.
            message (str): A simple message for the action.
            status (str): The passed/fail status for the App handling of config.
        """
        try:
            # delete config from configs dict
            del self.configs[trigger_id]

            # send ack response
            response = {
                'command': 'Acknowledged',
                'message': message,
                'status': status,
                'type': 'DeleteConfig',
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
        if not callable(callback):
            raise RuntimeError('Callback method (callback) is not a callable.')

        for trigger_id, config in self.configs.items():
            try:
                self.tcex.log.trace('triggering callback for config id: {}'.format(trigger_id))
                # get a session_id specifically for this thread
                session_id = self.session_id

                # get instance of playbook specifically for this thread
                playbook = self.tcex.playbook
                # update the playbook hash/key/session_id and output_variables
                playbook.db.key = session_id
                playbook.output_variables = config.get('tc_playbook_out_variables', [])

                self.tcex.log.info('Trigger Session ID: {}'.format(session_id))

                args = (callback, playbook, trigger_id, config)
                # current thread has session_id as name
                self.message_thread(session_id, self.fire_event_trigger, args, kwargs)
            except Exception:
                self.tcex.log.trace(traceback.format_exc())

    def fire_event_trigger(self, callback, playbook, trigger_id, config, **kwargs):
        """Fire event for trigger.

        Args:
            callback (callable): The App callback method for firing an event.
            playbook (tcex.Playbook): A configure playbook instance for using to interact with
                KvStore.
            trigger_id (int): The current trigger Id.
            config (dict): A dict containing the configuration information.
        """
        # tokens are registered with a key, in this case the key is the trigger_id. each thread
        # is required to be registered to a key to use during lookup.
        self.tcex.token.register_thread(trigger_id, self.thread_name)

        # add a logging handler for this thread
        self.tcex.logger.add_thread_file_handler(
            name=self.thread_name,
            filename=self.session_logfile,
            level=self.tcex.default_args.tc_log_level,
            path=self.tcex.default_args.tc_log_path,
        )
        self.tcex.log.info('Handling fire event trigger ({})'.format(self.thread_name))

        try:
            if callback(playbook, trigger_id, config, **kwargs):
                # self.tcex.log.info('Trigger ID {} hit.'.format(trigger_id))
                self.increment_metric('hits')
                self.fire_event_publish(trigger_id, self.thread_name)
            else:
                self.increment_metric('misses')
                self.tcex.log.info('Trigger ID {} missed.'.format(trigger_id))
        except Exception as e:
            self.increment_metric('errors')
            self.tcex.log.error('The callback method encountered and error ({}).'.format(e))
            self.tcex.log.trace(traceback.format_exc())
        finally:
            # remove temporary logging file handler
            self.tcex.logger.remove_handler_by_name(self.thread_name)

            # unregister thread from token
            self.tcex.token.unregister_thread(trigger_id, self.thread_name)

    def fire_event_publish(self, trigger_id, session_id, request_key=None):
        """Send FireEvent command.

        Args:
            trigger_id (int): The ID of the trigger.
            session_id (str): The generated session for this fired event.
            request_key (str): The request key for this response.
        """
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
        """Convert name/value array to a query string.

        Args:
            params (dict): The query params for the request.

        Returns:
            str: The query params reformatted as a string.
        """
        query_string = []
        try:
            for q in params:
                query_string.append('{}={}'.format(q.get('name'), q.get('value')))
        except AttributeError as e:
            self.tcex.log.error('Bad params data provided {} ({})'.format(params, e))
            self.tcex.log.trace(traceback.format_exc())
        return '&'.join(query_string)

    def format_request_headers(self, headers):
        """Convert name/value array to a headers dict.

        Args:
            headers (dict): The dict of key/value header data.

        Returns:
            dict: The restructured header data.
        """
        headers_ = {}
        try:
            for h in headers:
                # TODO: either support tuple or csv list of values
                # headers_.setdefault(h.get('name').lower(), []).append(h.get('value'))
                headers_.setdefault(h.get('name').lower(), str(h.get('value')))

        except AttributeError as e:
            self.tcex.log.error('Bad header data provided {} ({})'.format(headers, e))
            self.tcex.log.trace(traceback.format_exc())
        return headers_

    def format_response_headers(self, headers):
        """Convert name/value array to a query string.

        Args:
            headers (dict): The dict header data to be converted to key/value pairs.

        Returns:
            dict: The restructured header data.
        """
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
        # start heartbeat monitor thread
        t = threading.Thread(name='heartbeat', target=self.heartbeat_monitor)
        t.daemon = True  # use setter for py2
        t.start()
        self.tcex.log.info('Heartbeat monitor started')

    def heartbeat_monitor(self):
        """Publish heartbeat on timer."""
        while True:
            if self.heartbeat_watchdog > (
                self.tcex.default_args.tc_svc_hb_timeout_seconds / self.heartbeat_sleep_time
            ):
                self.tcex.log.error('Missed server heartbeat message. Service is shutting down.')
                self.process_shutdown('Missed heartbeat commands.')
                break
            time.sleep(self.heartbeat_sleep_time)
            self.heartbeat_watchdog += 1

    def increment_metric(self, label, value=1):
        """Increment a metric if already exists.

        Args:
            label (str): The metric label (e.g., hits) to increment.
            value (int): The increment value. Defaults to 1.
        """
        if self._metrics.get(label) is not None:
            self._metrics[label] += value

    def listen(self):
        """List for message coming from broker."""
        self.tcex.log.trace('listen with {} broker'.format(self.tcex.args.tc_svc_broker_service))
        if self.tcex.args.tc_svc_broker_service.lower() == 'mqtt':
            target = self.listen_mqtt
        elif self.tcex.args.tc_svc_broker_service.lower() == 'redis':
            target = self.listen_redis

        t = threading.Thread(name='broker-listener', target=target, args=())
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

    def message_thread(self, name, target, args, kwargs=None):
        """Start a message thread.

        Args:
            name (str): The name of the thread.
            target (callable): The method to call for the thread.
            args (tuple): The args to pass to the target method.
        """
        # self.tcex.log.trace('message thread: {} - {}'.format(type(target), args))
        try:
            t = threading.Thread(name=name, target=target, args=args, kwargs=kwargs)
            t.daemon = True  # use setter for py2
            t.start()
        except Exception:
            self.tcex.log.trace(traceback.format_exc())

    @property
    def metrics(self):
        """Return current metrics."""
        # update default active playbook metric
        self.update_metric('active playbooks', len(self.configs))
        return self._metrics

    @metrics.setter
    def metrics(self, metrics):
        """Return current metrics."""
        if isinstance(metrics, dict):
            self._metrics = metrics
        else:
            self.tcex.log.error('Invalid data provided for metrics.')

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

    def playbook(self, session_id, variables):
        """Return a configure playbook instance.

        Args:
            session_id (str): The current session Id.
            variables (list): The requested output variables.

        Returns:
            tcex.Playbook: An instance of Playbooks.
        """
        playbook = self.tcex.playbook
        playbook.db.key = session_id
        playbook.output_variables = variables or []
        return playbook

    def process_config(self, message):
        """Process config message.

        Args:
            message (dict): The broker message.
        """
        command = message.get('command')
        config = message.get('config')
        status = 'Success'
        trigger_id = message.get('triggerId')

        if command.lower() == 'createconfig':
            self.tcex.log.info(
                'CreateConfig - trigger_id: {} config : {}'.format(trigger_id, config)
            )

            # register config apiToken
            self.tcex.token.register_token(
                trigger_id, message.get('apiToken'), message.get('expireSeconds')
            )

            if callable(self.create_config_callback):
                message = 'Config created'
                try:
                    # call callback for create config and handle exceptions to protect thread
                    self.create_config_callback(trigger_id, config)  # pylint: disable=not-callable
                except Exception as e:
                    message = 'The create config callback method encountered an error ({}).'.format(
                        e
                    )
                    self.tcex.log.error(message)
                    self.tcex.log.trace(traceback.format_exc())
                    status = 'Failed'

            # create config after callback to report status and message
            self.create_config(trigger_id, config, message, status)
        elif command.lower() == 'deleteconfig':
            self.tcex.log.info('DeleteConfig - trigger_id: {}'.format(trigger_id))

            # unregister config apiToken
            self.tcex.token.unregister_token(trigger_id)

            if callable(self.delete_config_callback):
                message = 'Delete created'
                try:
                    # call callback for delete config and handle exceptions to protect thread
                    self.delete_config_callback(trigger_id)  # pylint: disable=not-callable
                except Exception as e:
                    message = 'The delete config callback method encountered an error ({}).'.format(
                        e
                    )
                    self.tcex.log.error(message)
                    self.tcex.log.trace(traceback.format_exc())
                    status = 'Failed'

            # delete config
            self.delete_config(trigger_id, message, status)

    def process_run_service(self, message):
        """Process Webhook event messages.

        {
          "command": "RunService",
          "apiToken": "abc123",
          "bodyVariable": "request.body",
          "headers": [ { key/value pairs } ],
          "method": "GET",
          "queryParams": [ { key/value pairs } ],
          "requestKey": "123abc"
        }

        Args:
            message (dict): The broker message.
        """
        # register config apiToken (before any logging)
        self.tcex.token.register_token(
            self.thread_name, message.get('apiToken'), message.get('expireSeconds')
        )
        self.tcex.log.info('Processing RunService Command')
        self.tcex.log.debug('message: {}'.format(message))

        # thread event used to block response until body is written
        e = threading.Event()

        # process message
        request_key = message.get('requestKey')
        body = None
        try:
            # read body from redis
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
            # TODO: research required field for wsgi and update
            # TODO: move to a method
            environ = {
                'wsgi.errors': self.tcex.log.error,  # sys.stderr
                # 'wsgi.file_wrapper': <class 'wsgiref.util.FileWrapper'>
                'wsgi.input': body,
                'wsgi.multithread': True,
                'wsgi.multiprocess': False,
                'wsgi.run_once': True,
                'wsgi.url_scheme': 'https',
                'wsgi.version': (1, 0),
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
                'SERVER_NAME': '',
                'SERVER_PORT': '',
                'SERVER_PROTOCOL': 'HTTP/1.1',
                # 'SERVER_SOFTWARE': 'WSGIServer/0.2',
            }
            if headers.get('content-type') is not None:
                environ['CONTENT_TYPE'] = (headers.get('content-type'),)
            if headers.get('content-length') is not None:
                environ['CONTENT_LENGTH'] = headers.get('content-length')
            self.tcex.log.trace('environ: {}'.format(environ))
            self.increment_metric('requests')
        except Exception as e:
            self.tcex.log.error('Failed building environ ({})'.format(e))
            self.tcex.log.trace(traceback.format_exc())
            self.increment_metric('errors')
            return  # stop processing

        def response_handler(*args, **kwargs):  # pylint: disable=unused-argument
            """Handle WSGI Response"""
            kwargs['e'] = e  # add event to kwargs for blocking
            kwargs['request_key'] = request_key
            t = threading.Thread(
                name='response-handler',
                target=self.process_run_service_response,
                args=args,
                kwargs=kwargs,
            )
            t.daemon = True  # use setter for py2
            t.start()

        if callable(self.api_event_callback):
            try:
                body = self.api_event_callback(  # pylint: disable=not-callable
                    environ, response_handler
                )

                # decode body entries
                # TODO: validate this logic
                body = [base64.b64encode(b).decode('utf-8') for b in body][0]
                # write body to Redis
                self.redis_client.hset(request_key, 'response.body', body)

                # set thread event to True to trigger response
                self.tcex.log.info('API response body written')
                e.set()
            except Exception as e:
                self.tcex.log.error(
                    'The api event callback method encountered and error ({}).'.format(e)
                )
                self.tcex.log.trace(traceback.format_exc())
                self.increment_metric('errors')

        # unregister config apiToken
        self.tcex.token.unregister_token(self.thread_name)

    def process_run_service_response(self, *args, **kwargs):
        """Handle service event responses.

        ('200 OK', [('content-type', 'application/json'), ('content-length', '103')])
        """
        self.tcex.log.info('API response received, waiting on body to be written')
        kwargs.get('e').wait(10)  # wait for thread event - (set on body write)
        self.tcex.log.trace('response args: {}'.format(args))
        try:
            status_code, status = args[0].split(' ', 1)
            response = {
                'bodyVariable': 'response.body',
                'command': 'Acknowledged',
                'headers': self.format_response_headers(args[1]),
                'requestKey': kwargs.get('request_key'),  # pylint: disable=cell-var-from-loop
                'status': status,
                'statusCode': status_code,
                'type': 'RunService',
            }
            self.tcex.log.info('API response sent')
            self.publish(json.dumps(response))
            self.increment_metric('responses')
        except Exception as e:
            self.tcex.log.error('Failed creating response body ({})'.format(e))
            self.tcex.log.trace(traceback.format_exc())
            self.increment_metric('errors')

    def process_shutdown(self, reason):
        """Handle a shutdown message.

        Args:
            reason (str): The reason for the shutdown.
        """
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
        """Process Webhook event messages.

        Args:
            message (dict): The message data from the broker.
        """
        # session auth shared data is thread name which needs to map back to config triggerId
        self.tcex.token.register_thread(message.get('triggerId'), self.thread_name)

        # add logger for current session
        self.tcex.logger.add_thread_file_handler(
            name=self.thread_name,
            filename=self.session_logfile,
            level=self.tcex.default_args.tc_log_level,
            path=self.tcex.default_args.tc_log_path,
        )
        self.tcex.log.trace('Process webhook event trigger')

        # get config using triggerId passed in WebhookEvent data
        config = self.configs.get(message.get('triggerId'))
        if config is None:
            self.tcex.log.error(
                'Could not find config for triggerId {}'.format(message.get('triggerId'))
            )

        # get an instance of playbooks for App
        playbook = self.playbook(self.thread_name, config.get('tc_playbook_out_variables'))

        try:
            request_key = message.get('requestKey')
            body = self.redis_client.hget(request_key, 'request.body')
            if body is not None:
                body = json.loads(base64.b64decode(body))
            headers = message.get('headers')
            method = message.get('method')
            params = message.get('queryParams')
            trigger_id = message.get('triggerId')
            if self.webhook_event_callback(  # pylint: disable=not-callable
                playbook, method, headers, params, body, config
            ):
                self.increment_metric('hits')
                self.fire_event_publish(trigger_id, self.thread_name, request_key)
            else:
                self.increment_metric('misses')
        except Exception as e:
            self.tcex.log.error('The callback method encountered and error ({}).'.format(e))
            self.tcex.log.trace(traceback.format_exc())
            self.increment_metric('errors')
        finally:
            # remove temporary logging file handler
            self.tcex.logger.remove_handler_by_name(self.thread_name)

            # unregister thread from token
            self.tcex.token.unregister_thread(message.get('triggerId'), self.thread_name)

    def publish(self, message, topic=None):
        """Publish a message on client topic.

        Args:
            message (str): The message to be sent on client topic.
            topic (str): The broker topic. Default to None.
        """
        if topic is None:
            topic = self.tcex.default_args.tc_svc_client_topic
        self.tcex.log.debug('publish topic: ({})'.format(topic))
        self.tcex.log.debug('publish message: ({})'.format(message))

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
        """Handle any event coming in on server_topic.

        Args:
            message (dict): The broker message.
        """
        self.tcex.log.trace('message: {}'.format(message))
        # parse the command type
        command = message.get('command')

        self.tcex.log.info('Command received: {}'.format(command))
        if command.lower() == 'heartbeat':
            self.heartbeat_watchdog = 0
            self.heartbeat_miss_count = 0

            # send heartbeat -acknowledge- command
            response = {'command': 'Heartbeat', 'metric': self.metrics}
            self.publish(json.dumps(response))
            self.tcex.log.info('Heartbeat command sent')
            self.tcex.log.debug('metrics: {}'.format(self.metrics))
        elif command.lower() == 'loggingchange':
            # {"command": "LoggingChange", "level": "DEBUG"}
            level = message.get('level')
            self.tcex.log.info('LoggingChange - level: {}'.format(level))
            self.tcex.logger.update_handler_level(level)
        elif command.lower() == 'runservice':
            self.message_thread(self.session_id, self.process_run_service, (message,))
        elif command.lower() == 'shutdown':
            # {"command": "Shutdown", "reason": "Service disabled by user."}
            reason = message.get('reason')
            self.process_shutdown(reason)
        elif command.lower() == 'webhookevent':
            self.message_thread(self.session_id, self.process_webhook, (message,))
        else:
            # any other message is a config message
            self.message_thread('process-config', self.process_config, (message,))

    @property
    def session_id(self):
        """Return a uuid4 session id."""
        return str(uuid.uuid4())

    @property
    def session_logfile(self):
        """Return a uuid4 session id."""
        return '{}/{}.log'.format(datetime.today().strftime('%Y%m%d'), self.thread_name)

    @property
    def thread_name(self):
        """Return a uuid4 session id."""
        return threading.current_thread().name

    def update_metric(self, label, value):
        """Update a metric if already exists.

        Args:
            label (str): The metric label (e.g., hits) to update.
            value (int|str): The updated value for the metric.
        """
        if self._metrics.get(label) is not None:
            self._metrics[label] = value
