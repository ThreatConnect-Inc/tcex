# -*- coding: utf-8 -*-
"""TcEx Service Common Module"""
import base64
import json
import os
import subprocess
import sys
import threading
import time
import uuid
from multiprocessing import Process
from random import randint

import paho.mqtt.client as mqtt


from .test_case_playbook_common import TestCasePlaybookCommon


class TestCaseServiceCommon(TestCasePlaybookCommon):
    """Service App TestCase Class"""

    _mqtt_client = None
    app_process = None
    client_topic = f'client-topic-{randint(100, 999)}'
    tcex_testing_context = None
    server_topic = f'server-topic-{randint(100, 999)}'
    service_run_method = 'subprocess'  # run service as subprocess, multiprocess, or thread
    shutdown = False
    shutdown_complete = False
    sleep_after_publish_config = 0.5
    sleep_after_publish_webhook_event = 0.5
    sleep_after_service_start = 5
    sleep_before_delete_config = 2
    sleep_before_shutdown = 0.5

    @property
    def context_tracker(self):
        """Return the current context trackers."""
        if not self._context_tracker:
            self._context_tracker = json.loads(
                self.redis_client.hget(self.tcex_testing_context, '_context_tracker') or '[]'
            )
        return self._context_tracker

    @property
    def default_args(self):
        """Return App default args."""
        args = super().default_args
        args.update(
            {
                'tc_svc_broker_host': os.getenv('TC_SVC_BROKER_HOST', 'localhost'),
                'tc_svc_broker_port': int(os.getenv('TC_SVC_BROKER_PORT', '1883')),
                'tc_svc_broker_service': os.getenv('TC_SVC_BROKER_SERVICE', 'mqtt'),
                'tc_svc_broker_token': os.getenv('TC_SVC_BROKER_TOKEN'),
                'tc_svc_client_topic': self.client_topic,
                'tc_svc_server_topic': self.server_topic,
                'tc_svc_hb_timeout_seconds': int(os.getenv('TC_SVC_HB_TIMEOUT_SECONDS', '300')),
            }
        )
        return args

    @property
    def mqtt_client(self):
        """Return a mqtt client instance."""
        if self._mqtt_client is None:
            self._mqtt_client = mqtt.Client()
            self._mqtt_client.connect(
                self.tcex.args.tc_svc_broker_host,
                self.tcex.args.tc_svc_broker_port,
                self.tcex.args.tc_svc_broker_timeout,
            )
        return self._mqtt_client

    @property
    def output_variables(self):
        """Return playbook output variables"""
        if self._output_variables is None:
            self._output_variables = []
            # Currently there is no support for projects with multiple install.json files.
            for p in self.install_json.get('playbook', {}).get('outputVariables') or []:
                # "#Trigger:9876:app.data.count!String"
                self._output_variables.append(f"#Trigger:{9876}:{p.get('name')}!{p.get('type')}")
        return self._output_variables

    def publish(self, message, topic=None):
        """Publish message on server channel."""
        if topic is None:
            topic = self.server_topic

        # self.log.debug(f'topic: ({topic})')
        # self.log.debug(f'message: ({message})')
        # self.log.debug(f'broker_service: ({self.tcex.args.tc_svc_broker_service})')

        if self.tcex.args.tc_svc_broker_service.lower() == 'mqtt':
            self.mqtt_client.publish(topic, message)
        elif self.tcex.args.tc_svc_broker_service.lower() == 'redis':
            self.redis_client.publish(topic, message)

    def publish_create_config(self, message):
        """Send create config message.

        Args:
            trigger_id (str): The trigger id for the config message.
            message (dict): The entire message with trigger_id and config.
        """
        # build config message
        message['apiToken'] = '000000000'
        message['expireSeconds'] = int(time.time() + 86400)
        message['command'] = 'CreateConfig'
        message['config']['tc_playbook_out_variables'] = self.output_variables
        message['triggerId'] = message.pop('trigger_id')
        self.publish(json.dumps(message))
        time.sleep(self.sleep_after_publish_config)

    def publish_delete_config(self, message):
        """Send delete config message.

        Args:
            message (str): The message coming in on Broker channel
        """
        time.sleep(self.sleep_before_delete_config)
        # using triggerId here instead of trigger_id do to pop in publish_create_config
        config_msg = {'command': 'DeleteConfig', 'triggerId': message.get('triggerId')}
        self.publish(json.dumps(config_msg))

    def publish_shutdown(self):
        """Publish shutdown message."""
        config_msg = {'command': 'Shutdown'}
        self.publish(json.dumps(config_msg))

    def publish_webhook_event(
        self,
        trigger_id,
        body=None,
        headers=None,
        method='GET',
        query_params=None,
        request_key='abc123',
    ):
        """Send create config message.

        Args:
            trigger_id (str): The trigger ID.
            headers (list, optional): A list of headers name/value pairs. Defaults to [].
            method (str, optional): The method. Defaults to 'GET'.
            query_params (list, optional): A list of query param name/value pairs. Defaults to [].
        """
        body = body or ''
        if isinstance(body, dict):
            body = json.dumps(body)

        body = self.redis_client.hset(
            request_key, 'request.body', base64.b64encode(body.encode('utf-8'))
        )
        event = {
            'command': 'WebhookEvent',
            'method': method,
            'queryParams': query_params or [],
            'headers': headers or [],
            'body': 'request.body',
            'requestKey': request_key,
            'triggerId': trigger_id,
        }
        self.publish(json.dumps(event))
        time.sleep(self.sleep_after_publish_webhook_event)

    def run(self, args):
        """Implement in Child Class"""
        raise NotImplementedError('Child class must implement this method.')

    def run_profile(self, profile_name):
        """Run an App using the profile name.

        Args:
            profile_name (str): The name of the profile to run.

        Returns:
            int: The exit code for the App execution.
        """
        profile = self.profile(profile_name)
        if not profile:
            self.log.error(f'No profile named {profile_name} found.')
            return self._exit(1)

        # stage any staging data
        self.stager.redis.from_dict(profile.get('stage', {}).get('redis', {}))

        # build args from install.json
        args = {}
        args.update(profile.get('inputs', {}).get('required', {}))
        args.update(profile.get('inputs', {}).get('optional', {}))
        if not args:
            self.log.error(f'No profile named {profile_name} found.')
            return self._exit(1)

        # run the App
        self.run(args)

        return self._exit(0)

    def run_service(self):
        """Run the micro-service."""
        self.log_data('run', 'service method', self.service_run_method)
        if self.service_run_method == 'subprocess':
            # create required .app_params encrypted file
            self.app_init_create_config(self.args, self.output_variables, self.tcex_testing_context)

            # run the Service App as a subprocess
            self.app_process = subprocess.Popen(['python', 'run.py'])
        elif self.service_run_method == 'thread':
            # backup sys.argv
            sys_argv_orig = sys.argv

            # clear sys.argv
            sys.argv = sys.argv[:1]

            # run App in a thread
            t = threading.Thread(target=self.run, args=(self.args,), daemon=True)
            t.start()

            # restore sys.argv
            sys.argv = sys_argv_orig
        elif self.service_run_method == 'multiprocess':
            p = Process(target=self.run, args=(self.args,), daemon=True)
            p.start()

        # give app some time to initialize before continuing
        time.sleep(self.sleep_after_service_start)

    @classmethod
    def setup_class(cls):
        """Run once before all test cases."""
        super().setup_class()
        cls.args = {}
        cls.service_file = 'SERVICE_STARTED'  # started file flag

        # generate a context used in service.py to write context during fire event
        cls.tcex_testing_context = str(uuid.uuid4())

    def setup_method(self):
        """Run before each test method runs."""
        super().setup_method()
        self.stager.redis.from_dict(self.redis_staging_data)
        self.redis_client = self.tcex.redis_client

        # only start service if it hasn't been started already base on file flag.
        if not os.path.isfile(self.service_file):
            open(self.service_file, 'w+').close()  # create service started file flag
            self.run_service()

            # start shutdown monitor thread
            t = threading.Thread(target=self.shutdown_monitor, daemon=True)
            t.start()

    def shutdown_monitor(self):
        """Monitor for shutdown flag."""
        while not self.shutdown:
            time.sleep(0.5)

        # shutdown the App
        self.publish_shutdown()

        # give Service App x seconds to shutdown before terminating
        for _ in range(1, 10):
            time.sleep(0.5)
            if self.app_process.poll() is not None:
                break
        else:
            self.log.debug(f'terminating process: {self.app_process.pid}')
            self.app_process.terminate()  # terminate subprocess

        # remove started file flag
        try:
            os.remove(self.service_file)
        except OSError:
            pass

        # set shutdown_complete
        self.shutdown_complete = True

    def stage_data(self, staged_data):
        """Stage the data in the profile."""
        for key, value in list(staged_data.get('redis', {}).items()):
            self.stager.redis.stage(key, value)

    @classmethod
    def teardown_class(cls):
        """Run once before all test cases."""
        super().teardown_class()
        # set shutdown flag for shutdown_monitor and wait until shutdown is done
        cls.shutdown = True
        for _ in range(1, 12):
            if cls.shutdown_complete:
                break
            time.sleep(0.5)

    def teardown_method(self):
        """Run after each test method runs."""
        time.sleep(self.sleep_before_shutdown)
        # run test_case_playbook_common teardown_method
        super().teardown_method()

        # clean up tcex testing context after populate_output has run
        self.clear_context(self.tcex_testing_context)
