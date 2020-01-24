# -*- coding: utf-8 -*-
"""TcEx Service Common Module"""
import base64
import json
import os
import threading
import time
import uuid
from multiprocessing import Process
from random import randint

import paho.mqtt.client as mqtt
from _pytest.monkeypatch import MonkeyPatch

from .test_case_playbook_common import TestCasePlaybookCommon


class TestCaseServiceCommon(TestCasePlaybookCommon):
    """Service App TestCase Class"""

    _mqtt_client = None
    client_topic = f'client-topic-{randint(100, 999)}'
    server_topic = f'server-topic-{randint(100, 999)}'
    service_run_method = 'thread'  # run service as thread or multiprocess

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

    def patch_service(self):
        """Patch the micro-service."""
        from tcex.services import Services  # pylint: disable=import-error,no-name-in-module

        tc_svc_broker_host = self.default_args.get('tc_svc_broker_host', 'localhost')
        tc_svc_broker_port = int(self.default_args.get('tc_svc_broker_port', 1883))
        tc_svc_broker_timeout = int(self.default_args.get('tc_svc_hb_timeout_seconds', 60))

        @property
        def mqtt_client(self):
            self.tcex.log.trace('using monkeypatch method')
            if self._mqtt_client is None:
                self._mqtt_client = mqtt.Client(client_id='', clean_session=True)
                self.mqtt_client.connect(
                    tc_svc_broker_host, tc_svc_broker_port, tc_svc_broker_timeout
                )
            return self._mqtt_client

        redis_client = self.redis_client

        @staticmethod
        def session_id_(trigger_id=None):  # pylint: disable=unused-argument
            """Patch session_id method to track trigger id -> session_id for validation."""
            # write to redis
            context = str(uuid.uuid4())  # create unique uuid for event trigger
            self.context_tracker.append(context)  # add context/session_id to tracker

            self.tcex.log.trace('using monkeypatch method')
            if trigger_id is not None:
                redis_client.hset(context, '_trigger_id', trigger_id)
            return context

        MonkeyPatch().setattr(Services, 'mqtt_client', mqtt_client)
        MonkeyPatch().setattr(Services, 'session_id', session_id_)

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
        time.sleep(0.5)

    def publish_delete_config(self, message):
        """Send delete config message.

        Args:
            trigger_id (str): The trigger id for the config message.
        """
        time.sleep(0.5)
        # using triggerId here instead of trigger_id do to pop in publish_create_config
        config_msg = {'command': 'DeleteConfig', 'triggerId': message.get('triggerId')}
        self.publish(json.dumps(config_msg))

    def publish_shutdown(self):
        """Publish shutdown message."""
        config_msg = {'command': 'Shutdown'}
        self.publish(json.dumps(config_msg))
        time.sleep(0.5)

    def publish_update_config(self, trigger_id, config):
        """Send create config message.

        Args:
            trigger_id (str): The trigger id for the config message.
            config (dict): The data for the config message.
        """
        config_msg = {'command': 'UpdateConfig', 'triggerId': trigger_id, 'config': config}
        config_msg['config']['outputVariables'] = self.output_variables
        self.publish(json.dumps(config_msg))
        time.sleep(0.5)

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
        time.sleep(0.5)

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
        if self.service_run_method == 'thread':
            t = threading.Thread(target=self.run, args=(self.args,))
            t.daemon = True  # use setter for py2
            t.start()
            time.sleep(1)
        elif self.service_run_method == 'multiprocess':
            p = Process(target=self.run, args=(self.args,))
            p.daemon = True
            p.start()
            # p.join()
        time.sleep(5)

    @classmethod
    def setup_class(cls):
        """Run once before all test cases."""
        super().setup_class()
        cls.args = {}
        cls.service_file = 'SERVICE_STARTED'  # started file flag

    def setup_method(self):
        """Run before each test method runs."""
        super().setup_method()
        self.stager.redis.from_dict(self.redis_staging_data)
        self.redis_client = self.tcex.redis_client

        # patch service for each profile (test case)
        self.patch_service()

        # only start service if it hasn't been started already base on file flag.
        if not os.path.isfile(self.service_file):
            open(self.service_file, 'w+').close()  # create service started file flag
            self.run_service()

    def stage_data(self, staged_data):
        """Stage the data in the profile."""
        for key, value in list(staged_data.get('redis', {}).items()):
            self.stager.redis.stage(key, value)

    @classmethod
    def teardown_class(cls):
        """Run once before all test cases."""
        super().teardown_class()
        try:
            os.remove(cls.service_file)
        except OSError:
            pass

    def teardown_method(self):
        """Run after each test method runs."""
        time.sleep(0.5)
        super().teardown_method()
