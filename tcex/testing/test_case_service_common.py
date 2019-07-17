# -*- coding: utf-8 -*-
"""TcEx Service Common Module"""
import json
import os
import threading
import time
from multiprocessing import Process
from random import randint

from _pytest.monkeypatch import MonkeyPatch
import paho.mqtt.client as mqtt
from .test_case_playbook_common import TestCasePlaybookCommon


class TestCaseServiceCommon(TestCasePlaybookCommon):
    """Service App TestCase Class"""

    _mqtt_client = None
    client_topic = 'client-topic-{}'.format(randint(100, 999))
    server_topic = 'server-topic-{}'.format(randint(100, 999))
    service_run_method = 'thread'  # run service as thread or multiprocess

    @property
    def default_args(self):
        """Return App default args."""
        args = super(TestCaseServiceCommon, self).default_args
        args.update(
            {
                'tc_svc_broker_host': os.getenv('TC_SVC_BROKER_HOST', 'localhost'),
                'tc_svc_broker_port': os.getenv('TC_SVC_BROKER_PORT', '1883'),
                'tc_svc_broker_service': os.getenv('TC_SVC_BROKER_SERVICE', 'mqtt'),
                'tc_svc_broker_token': os.getenv('TC_SVC_BROKER_TOKEN'),
                'tc_svc_client_topic': self.client_topic,
                'tc_svc_server_topic': self.server_topic,
                'tc_svc_hb_timeout_seconds': int(os.getenv('TC_SVC_HB_TIMEOUT_SECONDS', '60')),
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
                self._output_variables.append(
                    '#Trigger:{}:{}!{}'.format(9876, p.get('name'), p.get('type'))
                )
        return self._output_variables

    def patch_service(self):
        """Patch the micro-service."""
        from tcex.service import Service  # pylint: disable=import-error,no-name-in-module

        current_context = self.context

        @property
        def mqtt_client(self):
            self.tcex.log.trace('using monkeypatch method')
            if self._mqtt_client is None:
                self._mqtt_client = mqtt.Client(client_id='', clean_session=True)
            return self._mqtt_client

        @property
        def session_id(self):  # pylint: disable=unused-argument
            self.tcex.log.trace('using monkeypatch method')
            return current_context

        @staticmethod
        def session_logfile(session_id):  # pylint: disable=unused-argument
            self.tcex.log.trace('using monkeypatch method')
            return '{0}/{0}.log'.format(current_context)

        MonkeyPatch().setattr(Service, 'mqtt_client', mqtt_client)
        MonkeyPatch().setattr(Service, 'session_id', session_id)
        MonkeyPatch().setattr(Service, 'session_logfile', session_logfile)

    def publish(self, message, topic=None):
        """Publish message on server channel."""
        if topic is None:
            topic = self.server_topic

        # self.log.debug('topic: ({})'.format(topic))
        # self.log.debug('message: ({})'.format(message))
        # self.log.debug('broker_service: ({})'.format(self.tcex.args.tc_svc_broker_service))

        if self.tcex.args.tc_svc_broker_service.lower() == 'mqtt':
            self.mqtt_client.publish(topic, message)
        elif self.tcex.args.tc_svc_broker_service.lower() == 'redis':
            self.redis_client.publish(topic, message)

    def publish_create_config(self, trigger_id, config):
        """Send create config message.

        Args:
            trigger_id (str): The trigger id for the config message.
            config (dict): The data for the config message.
        """
        config_msg = {'command': 'CreateConfig', 'triggerId': trigger_id, 'config': config}
        config_msg['config']['tc_playbook_out_variables'] = self.output_variables
        self.publish(json.dumps(config_msg))
        time.sleep(0.5)

    def publish_delete_config(self, trigger_id):
        """Send delete config message.

        Args:
            trigger_id (str): The trigger id for the config message.
        """
        config_msg = {'command': 'DeleteConfig', 'triggerId': trigger_id}
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
            self.log.error('No profile named {} found.'.format(profile_name))
            return self._exit(1)

        # stage any staging data
        self.stager.redis.from_dict(profile.get('stage', {}).get('redis', {}))

        # build args from install.json
        args = {}
        args.update(profile.get('inputs', {}).get('required', {}))
        args.update(profile.get('inputs', {}).get('optional', {}))
        if not args:
            self.log.error('No profile named {} found.'.format(profile_name))
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
        super(TestCaseServiceCommon, cls).setup_class()
        cls.args = {}
        cls.service_file = 'SERVICE_STARTED'

    def setup_method(self):
        """Run before each test method runs."""
        super(TestCaseServiceCommon, self).setup_method()
        self.stager.redis.from_dict(self.redis_staging_data)
        self.redis_client = self.tcex.playbook.db.r

        self.patch_service()
        if not os.path.isfile(self.service_file):
            with open(self.service_file, 'w+') as f:  # noqa: F841; pylint: disable=unused-variable
                pass
            self.run_service()

    def stage_data(self, staged_data):
        """Stage the data in the profile."""
        for key, value in list(staged_data.get('redis', {}).items()):
            self.stager.redis.stage(key, value)

    @classmethod
    def teardown_class(cls):
        """Run once before all test cases."""
        super(TestCaseServiceCommon, cls).teardown_class()
        try:
            os.remove(cls.service_file)
        except FileNotFoundError:
            pass

    def teardown_method(self):
        """Run after each test method runs."""
        time.sleep(0.5)
        r = self.stager.redis.delete_context(self.context)
        self.log_data('teardown method', 'delete count', r)
        super(TestCaseServiceCommon, self).teardown_method()
