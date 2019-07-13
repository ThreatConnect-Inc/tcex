# -*- coding: utf-8 -*-
"""TcEx Service Common Module"""
import json
import os
import threading
import time
from multiprocessing import Process
from random import randint
from _pytest.monkeypatch import MonkeyPatch
from tcex import TcEx
from .test_case_playbook_common import TestCasePlaybookCommon


class TestCaseServiceCommon(TestCasePlaybookCommon):
    """Service App TestCase Class"""

    # TODO: Update after merge of services branch
    if hasattr(TcEx, 'service'):
        from tcex.tcex_service import TcExService  # pylint: disable=import-error,no-name-in-module

        # store original method before monkeypatching the method
        setattr(TcExService, 'fire_event_orig', TcExService.fire_event)

    client_channel = 'client-channel-{}'.format(randint(100, 999))
    server_channel = 'server-channel-{}'.format(randint(100, 999))
    service_run_method = 'thread'  # run service as thread or multiprocess

    @property
    def default_args(self):
        """Return App default args."""
        args = super(TestCaseServiceCommon, self).default_args
        args.update(
            {
                'tc_client_channel': self.client_channel,
                'tc_server_channel': self.server_channel,
                'tc_heartbeat_seconds': int(os.getenv('TC_HEARTBEAT_SECONDS', '60')),
            }
        )
        return args

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
        from tcex.tcex_service import TcExService  # pylint: disable=import-error,no-name-in-module

        current_context = self.context

        def set_session_id(self, *args, **kwargs):
            """Set the session id via monkeypatch"""
            kwargs['session_id'] = current_context
            return self.fire_event_orig(*args, **kwargs)

        MonkeyPatch().setattr(TcExService, 'fire_event', set_session_id)

    def publish_create_config(self, trigger_id, config):
        """Send create config message."""
        config_msg = {'command': 'CreateConfig', 'triggerId': trigger_id, 'config': config}
        config_msg['config']['outputVariables'] = self.output_variables
        self.redis_client.publish(self.server_channel, json.dumps(config_msg))
        time.sleep(0.5)

    def publish_delete_config(self, trigger_id):
        """Send create config message."""
        config_msg = {'command': 'DeleteConfig', 'triggerId': trigger_id}
        self.redis_client.publish(self.server_channel, json.dumps(config_msg))

    def publish_shutdown(self):
        """Publish shutdown message."""
        config_msg = {'command': 'Shutdown'}
        self.redis_client.publish(self.server_channel, json.dumps(config_msg))
        time.sleep(0.5)

    def publish_update_config(self, trigger_id, config):
        """Send create config message."""
        config_msg = {'command': 'UpdateConfig', 'triggerId': trigger_id, 'config': config}
        config_msg['config']['outputVariables'] = self.output_variables
        self.redis_client.publish(self.server_channel, json.dumps(config_msg))
        time.sleep(0.5)

    def run(self, args):
        """Implement in Child Class"""
        raise NotImplementedError('Child class must implement this method.')

    def run_profile(self, profile_name):
        """Run an App using the profile name."""
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
        # cls.publish_shutdown(cls)
        # cls.redis_client.publish('server-channel-123', '{"command": "Shutdown"}')

    def teardown_method(self):
        """Run after each test method runs."""
        time.sleep(0.5)
        r = self.stager.redis.delete_context(self.context)
        self.log_data('teardown method', 'delete count', r)
        super(TestCaseServiceCommon, self).teardown_method()
