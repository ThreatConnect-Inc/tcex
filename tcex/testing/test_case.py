# -*- coding: utf-8 -*-
"""TcEx testing Framework."""
import json
import logging
from logging.handlers import RotatingFileHandler
import os
import re
import threading
import time
import uuid
import sys
import traceback
from datetime import datetime
from random import randint

from six import string_types
from _pytest.monkeypatch import MonkeyPatch

from tcex import TcEx

from .stage_data import Stager
from .validate_data import Validator

logger = logging.getLogger('TestCase')
rfh = RotatingFileHandler('log/tests.log', backupCount=10, maxBytes=10485760, mode='a')
rfh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rfh.setFormatter(formatter)
logger.addHandler(rfh)
logger.setLevel(logging.DEBUG)


class TestCase(object):
    """Base TestCase Class"""

    _app_path = os.getcwd()
    _current_test = None
    _input_params = None
    _install_json = None
    _timer_class_start = None
    _timer_method_start = None
    context = None
    log = logger
    env = set(os.environ.get('TCEX_TEST_ENVS', 'build').split(','))
    tcex = None

    def _exit(self, code):
        """Log and return exit code"""
        self.log.info('[run] Exit Code: {}'.format(code))
        self.tcex.log.info('Exit Code: {}'.format(code))
        return code

    @staticmethod
    def _to_bool(value):
        """Return bool value from int or string."""
        return str(value).lower() in ['1', 'true']

    def app(self, args):
        """Return an instance of App."""
        from app import App  # pylint: disable=import-error

        return App(self.get_tcex(args))

    @property
    def default_args(self):
        """Return App default args."""
        args = {
            'api_access_id': os.getenv('API_ACCESS_ID'),
            'api_default_org': os.getenv('API_DEFAULT_ORG'),
            'api_secret_key': os.getenv('API_SECRET_KEY'),
            'tc_api_path': os.getenv('TC_API_PATH'),
            'tc_in_path': os.getenv('TC_IN_PATH', 'log'),
            'tc_log_level': os.getenv('TC_LOG_LEVEL', 'trace'),
            'tc_log_path': os.getenv('TC_LOG_PATH', 'log'),
            'tc_log_to_api': self._to_bool(os.getenv('TC_LOG_TO_API', 'false')),
            'tc_out_path': os.getenv('TC_OUT_PATH', 'log'),
            'tc_proxy_external': self._to_bool(os.getenv('TC_PROXY_EXTERNAL', 'false')),
            'tc_proxy_host': os.getenv('TC_PROXY_HOST', 'localhost'),
            'tc_proxy_password': os.getenv('TC_PROXY_PASSWORD', ''),
            'tc_proxy_port': os.getenv('TC_PROXY_PORT', '4242'),
            'tc_proxy_tc': self._to_bool(os.getenv('TC_PROXY_TC', 'false')),
            'tc_proxy_username': os.getenv('TC_PROXY_USERNAME', ''),
            'tc_temp_path': os.getenv('TC_TEMP_PATH', 'log'),
        }
        if os.getenv('TC_TOKEN'):
            args['tc_token'] = os.getenv('TC_TOKEN')
            args['tc_token_expires'] = os.getenv('TC_TOKEN_EXPIRES')
        return args

    def get_tcex(self, args=None):
        """Return an instance of App."""
        args = args or {}
        app_args = self.default_args
        app_args.update(args)
        if self.tcex is not None and self.context == self.tcex.default_args.tc_playbook_db_context:
            self.tcex.tcex_args.inject_params(app_args)  # during run this is required
            return self.tcex

        sys.argv = [
            sys.argv[0],
            '--tc_log_path',
            'log',
            '--tc_log_file',
            '{}-app.log'.format(self.context),
        ]
        self.tcex = TcEx()
        # TODO: validate this
        self.tcex.logger.update_handler_level('error')
        self.tcex.tcex_args.inject_params(app_args)  # required for stager
        return self.tcex

    @property
    def install_json(self):
        """Return install.json contents."""
        file_fqpn = os.path.join(self._app_path, 'install.json')
        if self._install_json is None:
            if os.path.isfile(file_fqpn):
                with open(file_fqpn, 'r') as fh:
                    self._install_json = json.load(fh)
            else:
                print(('File "{}" could not be found.'.format(file_fqpn)))
        return self._install_json

    def input_params(self):
        """Return install.json params in a dict with name param as key.

        Args:
            ij (dict, optional): Defaults to None. The install.json contents.

        Returns:
            dict: A dictionary containing the install.json input params with name as key.
        """
        if self._input_params is None:
            self._input_params = {}
            # Currently there is no support for projects with multiple install.json files.
            for p in self.install_json.get('params') or []:
                self._input_params.setdefault(p.get('name'), p)
        return self._input_params

    def log_data(self, stage, label, data):
        """Log validation data."""
        msg = '{!s:>20} : {!s:<15}: {!s:<50}'.format('[{}]'.format(stage), label, data)
        self.log.info(msg)

    def profile(self, profile_name):
        """Get a profile from the profiles.json file by name"""
        profile = None
        with open(os.path.join(self.profiles_dir, '{}.json'.format(profile_name)), 'r') as fh:
            profile = json.load(fh)
        return profile

    @property
    def profiles_dir(self):
        """Return profile fully qualified filename."""
        feature_path = os.path.dirname(self._current_test.split('::')[0])
        return os.path.join(self._app_path, feature_path, 'profiles.d')

    @property
    def profile_names(self):
        """Get a profile from the profiles.json file by name"""
        profile_names = []
        for filename in sorted(os.listdir(self.profiles_dir)):
            if filename.endswith('.json'):
                profile_names.append(filename.replace('.json', ''))
        return profile_names

    @staticmethod
    def resolve_env_args(value):
        """Resolve env args
      Args:
          value (str): The value to resolve for environment variable.
      Returns:
          str: The original string or resolved string.
      """
        env_var = re.compile(r'^\$env\.(.*)$')
        envs_var = re.compile(r'^\$envs\.(.*)$')
        if env_var.match(value):
            # read value from environment variable
            env_key = env_var.match(str(value)).groups()[0]
            value = os.environ.get(env_key, value)
        elif envs_var.match(value):
            # read secure value from environment variable
            env_key = envs_var.match(str(value)).groups()[0]
            value = os.environ.get(env_key, value)
        return value

    def run(self, args):
        """Implement in Child Class"""
        raise NotImplementedError('Child class must implement this method.')

    @classmethod
    def setup_class(cls):
        """Run once before all test cases."""
        cls._timer_class_start = time.time()
        cls.log.info('{0} {1} {0}'.format('#' * 10, 'Setup Class'))
        cls.log_data(cls, 'setup class', 'started', datetime.now().isoformat())
        cls.log_data(cls, 'setup class', 'local envs', cls.env)

    def setup_method(self):
        """Run before each test method runs."""
        self._timer_method_start = time.time()
        self._current_test = os.environ.get('PYTEST_CURRENT_TEST').split(' ')[0]
        self.log.info('{0} {1} {0}'.format('=' * 10, self._current_test))
        self.log_data('setup method', 'started', datetime.now().isoformat())
        self.context = os.getenv('TC_PLAYBOOK_DB_CONTEXT', str(uuid.uuid4()))
        self.log_data('setup method', 'context', self.context)

    @property
    def stager(self):
        """Return instance of Stager class."""
        return Stager(self.get_tcex(self.default_args), logger, self.log_data)

    @classmethod
    def teardown_class(cls):
        """Run once before all test cases."""
        cls.log.info('{0} {1} {0}'.format('^' * 10, 'Teardown Class'))
        cls.log_data(cls, 'teardown class', 'finished', datetime.now().isoformat())
        cls.log_data(cls, 'teardown class', 'elapsed', time.time() - cls._timer_class_start)

    def teardown_method(self):
        """Run after each test method runs."""
        self.log_data('teardown method', 'finished', datetime.now().isoformat())
        self.log_data('teardown method', 'elapsed', time.time() - self._timer_class_start)

    @property
    def validator(self):
        """Return instance of Stager class."""
        return Validator(self.get_tcex(self.default_args), logger, self.log_data)

    def run_app_method(self, app, method):
        """Run the provided App method."""
        try:
            getattr(app, method)()
        except SystemExit as e:
            self.log.info('[run] Exit Code: {}'.format(e.code))
            self.log.error('App failed in {}() method ({}).'.format(method, e))
            self.tcex.log.info('Exit Code: {}'.format(e.code))
            return e.code
        except Exception:
            self.log.error(
                'App encountered except in {}() method ({}).'.format(method, traceback.format_exc())
            )
            return 1
        return 0


class TestCaseApp(TestCase):
    """App TestCase Class"""

    _output_variables = None
    redis_client = None

    @staticmethod
    def create_shelf_dir(shelf_path):
        """Creates a directory in log with the context name containing the batch data."""
        if not os.path.isdir(shelf_path):
            os.makedirs(shelf_path)
            with open(os.path.join(shelf_path, 'DEBUG'), 'a'):
                os.utime(os.path.join(shelf_path, 'DEBUG'), None)

    def run(self, args):  # pylint: disable=too-many-return-statements
        """Run the Playbook App.

        Args:
            args (dict): The App CLI args.
        Returns:
            [type]: [description]
        """
        # resolve env vars
        for k, v in list(args.items()):
            if isinstance(v, string_types):
                args[k] = self.resolve_env_args(v)

        self.log_data('run', 'args', args)
        app = self.app(args)

        # Start
        exit_code = self.run_app_method(app, 'start')
        if exit_code != 0:
            return exit_code

        # Run
        exit_code = self.run_app_method(app, 'run')
        if exit_code != 0:
            return exit_code

        # Write Output
        exit_code = self.run_app_method(app, 'write_output')
        if exit_code != 0:
            return exit_code

        # Done
        exit_code = self.run_app_method(app, 'done')
        if exit_code != 0:
            return exit_code

        return self._exit(app.tcex.exit_code)

    def run_profile(self, profile_name):
        """Run an App using the profile name."""
        profile = self.profile(profile_name)
        if not profile:
            self.log.error('No profile named {} found.'.format(profile_name))
            return self._exit(1)

        args = {'tc_temp_path': os.path.join(self._app_path, 'log', self.context)}
        self.create_shelf_dir(args['tc_temp_path'])

        # build args from install.json
        args.update(profile.get('inputs', {}).get('required', {}))
        args.update(profile.get('inputs', {}).get('optional', {}))
        if not args:
            self.log.error('No profile named {} found.'.format(profile_name))
            return self._exit(1)

        # run the App
        exit_code = self.run(args)

        return self._exit(exit_code)


class TestCasePlaybookCommon(TestCase):
    """Playbook TestCase Class"""

    _output_variables = None
    redis_client = None
    redis_staging_data = {
        '#App:1234:empty!String': '',
        '#App:1234:null!String': None,
        '#App:1234:non-ascii!String': 'ドメイン.テスト',
    }

    @property
    def default_args(self):
        """Return App default args."""
        args = super(TestCasePlaybookCommon, self).default_args
        args.update(
            {
                'tc_playbook_db_context': self.context,
                'tc_playbook_db_path': os.getenv('TC_PLAYBOOK_DB_PATH', 'localhost'),
                'tc_playbook_db_port': os.getenv('TC_PLAYBOOK_DB_PORT', '6379'),
                'tc_playbook_db_type': os.getenv('TC_PLAYBOOK_DB_TYPE', 'Redis'),
                'tc_playbook_out_variables': '',
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
                # "#App:9876:app.data.count!String"
                self._output_variables.append(
                    '#App:{}:{}!{}'.format(9876, p.get('name'), p.get('type'))
                )
        return self._output_variables

    def populate_output_variables(self, profile_name):
        """Generate validation rules from App outputs."""
        profile_filename = os.path.join(self.profiles_dir, '{}.json'.format(profile_name))
        with open(profile_filename, 'r+') as fh:
            profile_data = json.load(fh)
            if profile_data.get('outputs') is None:
                redis_data = self.redis_client.hgetall(self.context)
                outputs = {}
                for variable, data in redis_data.items():
                    variable = variable.decode('utf-8')
                    data = data.decode('utf-8')
                    if variable in self.output_variables:
                        outputs[variable] = {'expected_output': json.loads(data), 'op': 'eq'}
                profile_data['outputs'] = outputs
                fh.seek(0)
                fh.write(json.dumps(profile_data, indent=2, sort_keys=True))
                fh.truncate()

    def run(self, args):
        """Implement in Child Class"""
        raise NotImplementedError('Child class must implement this method.')

    def stage_data(self, staged_data):
        """Stage the data in the profile."""
        for key, value in list(staged_data.get('redis', {}).items()):
            self.stager.redis.stage(key, value)


class TestCasePlaybook(TestCasePlaybookCommon):
    """Playbook TestCase Class"""

    def run(self, args):  # pylint: disable=too-many-return-statements
        """Run the Playbook App.

        Args:
            args (dict): The App CLI args.

        Returns:
            [type]: [description]
        """
        # resolve env vars
        for k, v in args.items():
            if isinstance(v, string_types):
                args[k] = self.resolve_env_args(v)

        args['tc_playbook_out_variables'] = ','.join(self.output_variables)
        self.log_data('run', 'args', args)
        app = self.app(args)

        # Start
        exit_code = self.run_app_method(app, 'start')
        if exit_code != 0:
            return exit_code

        # Run
        try:
            if hasattr(app.args, 'tc_action') and app.args.tc_action is not None:
                tc_action = app.args.tc_action
                tc_action_formatted = tc_action.lower().replace(' ', '_')
                tc_action_map = 'tc_action_map'
                if hasattr(app, tc_action):
                    getattr(app, tc_action)()
                elif hasattr(app, tc_action_formatted):
                    getattr(app, tc_action_formatted)()
                elif hasattr(app, tc_action_map):
                    app.tc_action_map.get(app.args.tc_action)()  # pylint: disable=no-member
            else:
                app.run()
        except SystemExit as e:
            self.log.error('App failed in run() method ({}).'.format(e))
            return self._exit(e.code)
        except Exception:
            self.log.error(
                'App encountered except in run() method ({}).'.format(traceback.format_exc())
            )
            return self._exit(1)

        # Write Output
        exit_code = self.run_app_method(app, 'write_output')
        if exit_code != 0:
            return exit_code

        # Done
        exit_code = self.run_app_method(app, 'done')
        if exit_code != 0:
            return exit_code

        return self._exit(app.tcex.exit_code)

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
        exit_code = self.run(args)

        # populate the output variables
        # TODO: [INT-1320] investigate improvements
        if exit_code == 0:
            self.populate_output_variables(profile_name)

        return self._exit(exit_code)

    def setup_method(self):
        """Run before each test method runs."""
        super(TestCasePlaybook, self).setup_method()
        self.stager.redis.from_dict(self.redis_staging_data)
        self.redis_client = self.tcex.playbook.db.r

    def teardown_method(self):
        """Run after each test method runs."""
        r = self.stager.redis.delete_context(self.context)
        self.log_data('teardown method', 'delete count', r)
        super(TestCasePlaybook, self).teardown_method()


class TestCaseTriggerService(TestCasePlaybookCommon):
    """Playbook TestCase Class"""

    # TODO: Update after merge of services branch
    if hasattr(TcEx, 'service'):
        from tcex.tcex_service import TcExService  # pylint: disable=no-name-in-module

        # store original method before monkeypatching the method
        setattr(TcExService, 'fire_event_orig', TcExService.fire_event)

    client_channel = 'client-channel-{}'.format(randint(100, 999))
    server_channel = 'server-channel-{}'.format(randint(100, 999))

    @property
    def default_args(self):
        """Return App default args."""
        args = super(TestCaseTriggerService, self).default_args
        args.update(
            {
                'tc_client_channel': self.client_channel,
                'tc_server_channel': self.server_channel,
                'tc_heartbeat_seconds': int(os.getenv('TC_HEARTBEAT_SECONDS', '60')),
            }
        )
        return args

    def run(self, args):  # pylint: disable=too-many-return-statements
        """Run the Playbook App.

        Args:
            args (dict): The App CLI args.

        Returns:
            [type]: [description]
        """
        # resolve env vars
        for k, v in args.items():
            if isinstance(v, string_types):
                args[k] = self.resolve_env_args(v)

        args['tc_playbook_out_variables'] = ','.join(self.output_variables)
        self.log_data('run', 'args', args)
        app = self.app(args)

        # Setup
        exit_code = self.run_app_method(app, 'setup')
        if exit_code != 0:
            return exit_code

        # Trigger
        try:
            # configure custom trigger message handler
            app.tcex.service.custom_trigger(
                create_callback=app.create_config_callback,
                delete_callback=app.delete_config_callback,
                update_callback=app.update_config_callback,
                shutdown_callback=app.shutdown_callback,
            )
        except SystemExit as e:
            self.log.error('App failed in run() method ({}).'.format(e))
            return self._exit(e.code)
        except Exception:
            self.log.error(
                'App encountered except in run() method ({}).'.format(traceback.format_exc())
            )
            return self._exit(1)

        # Run
        exit_code = self.run_app_method(app, 'run')
        if exit_code != 0:
            return exit_code

        # Teardown
        exit_code = self.run_app_method(app, 'teardown')
        if exit_code != 0:
            return exit_code

        return self._exit(app.tcex.exit_code)

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

    def patch_service(self):
        """Patch the micro-service."""
        from tcex.tcex_service import TcExService  # pylint: disable=no-name-in-module

        current_context = self.context

        def set_session_id(self, *args, **kwargs):
            """Set the session id via monkeypatch"""
            kwargs['session_id'] = current_context
            return self.fire_event_orig(*args, **kwargs)

        MonkeyPatch().setattr(TcExService, 'fire_event', set_session_id)

    def publish_create_config(self, config_id, config):
        """Send create config message."""
        config_msg = {'command': 'CreateConfig', 'configId': config_id, 'config': config}
        config_msg['config']['outputVariables'] = self.output_variables
        self.redis_client.publish(self.server_channel, json.dumps(config_msg))
        time.sleep(0.5)

    def publish_delete_config(self, config_id):
        """Send create config message."""
        config_msg = {'command': 'DeleteConfig', 'configId': config_id}
        self.redis_client.publish(self.server_channel, json.dumps(config_msg))

    def publish_shutdown(self):
        """Publish shutdown message."""
        config_msg = {'command': 'Shutdown'}
        self.redis_client.publish(self.server_channel, json.dumps(config_msg))
        time.sleep(0.5)

    def publish_update_config(self, config_id, config):
        """Send create config message."""
        config_msg = {'command': 'UpdateConfig', 'configId': config_id, 'config': config}
        config_msg['config']['outputVariables'] = self.output_variables
        self.redis_client.publish(self.server_channel, json.dumps(config_msg))
        time.sleep(0.5)

    def run_service(self):
        """Run the micro-service."""
        t = threading.Thread(target=self.run, args=(self.args,))
        t.daemon = True  # use setter for py2
        t.start()
        time.sleep(1)

    @classmethod
    def setup_class(cls):
        """Run once before all test cases."""
        super(TestCaseTriggerService, cls).setup_class()
        cls.args = {}
        cls.service_file = 'SERVICE_STARTED'

    def setup_method(self):
        """Run before each test method runs."""
        super(TestCaseTriggerService, self).setup_method()
        self.stager.redis.from_dict(self.redis_staging_data)
        self.redis_client = self.tcex.playbook.db.r

        if not os.path.isfile(self.service_file):
            with open(self.service_file, 'w+') as f:  # noqa: F841; pylint: disable=unused-variable
                pass
            self.run_service()
        self.patch_service()

    def stage_data(self, staged_data):
        """Stage the data in the profile."""
        for key, value in list(staged_data.get('redis', {}).items()):
            self.stager.redis.stage(key, value)

    @classmethod
    def teardown_class(cls):
        """Run once before all test cases."""
        super(TestCaseTriggerService, cls).teardown_class()
        os.remove(cls.service_file)
        # cls.publish_shutdown(cls)
        # cls.redis_client.publish('server-channel-123', '{"command": "Shutdown"}')

    def teardown_method(self):
        """Run after each test method runs."""
        time.sleep(0.5)
        r = self.stager.redis.delete_context(self.context)
        self.log_data('teardown method', 'delete count', r)
        super(TestCaseTriggerService, self).teardown_method()
