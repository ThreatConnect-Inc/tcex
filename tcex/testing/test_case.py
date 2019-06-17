# -*- coding: utf-8 -*-
"""TcEx testing Framework."""
import json
import logging
from logging.handlers import RotatingFileHandler
import os
import time
import uuid
import sys
import re
from datetime import datetime

from tcex import TcEx
from app import App  # pylint: disable=import-error
from .stage_data import Stager
from .validate_data import Validator

logger = logging.getLogger('TestCase')
rfh = RotatingFileHandler('log/tests.log', backupCount=10, maxBytes=10_485_760, mode='a')
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
    _profile_file = None
    _tcex = None
    _timer_class_start = None
    _timer_method_start = None
    context = None
    log = logger

    @staticmethod
    def _to_bool(value):
        """Return bool value from int or string."""
        return str(value).lower() in ['1', 'true']

    def app(self, args):
        """Return an instance of App."""
        return App(self.tcex(args))

    @property
    def default_args(self):
        """Return App default args."""
        return {
            'api_access_id': os.getenv('API_ACCESS_ID'),
            'api_default_org': os.getenv('API_DEFAULT_ORG'),
            'api_secret_key': os.getenv('API_SECRET_KEY'),
            'tc_api_path': os.getenv('TC_API_PATH'),
            'tc_in_path': os.getenv('TC_IN_PATH', 'log'),
            'tc_log_level': os.getenv('TC_LOG_LEVEL', 'debug'),
            'tc_log_path': os.getenv('TC_LOG_PATH', 'log'),
            'tc_log_to_api': self._to_bool(os.getenv('TC_LOG_TO_API', 'false')),
            'tc_out_path': os.getenv('TC_OUT_PATH', 'log'),
            'tc_playbook_db_context': self.context,
            'tc_playbook_db_path': os.getenv('TC_PLAYBOOK_DB_PATH', 'localhost'),
            'tc_playbook_db_port': os.getenv('TC_PLAYBOOK_DB_PORT', '6379'),
            'tc_playbook_db_type': os.getenv('TC_PLAYBOOK_DB_TYPE', 'Redis'),
            'tc_playbook_out_variables': '',
            'tc_proxy_external': self._to_bool(os.getenv('TC_PROXY_EXTERNAL', 'false')),
            'tc_proxy_host': os.getenv('TC_PROXY_HOST', 'localhost'),
            'tc_proxy_password': os.getenv('TC_PROXY_PASSWORD', ''),
            'tc_proxy_port': os.getenv('TC_PROXY_PORT', '4242'),
            'tc_proxy_tc': self._to_bool(os.getenv('TC_PROXY_TC', 'false')),
            'tc_proxy_username': os.getenv('TC_PROXY_USERNAME', ''),
            'tc_temp_path': os.getenv('TC_TEMP_PATH', 'log'),
        }

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

    def run(self, args):
        """Implement in Child Class"""
        raise NotImplementedError('Child class must implement this method.')

    def setup_class(self):
        """Run once before all test cases."""
        self._timer_class_start = time.time()
        self.log.info('{0} {1} {0}'.format('#' * 10, 'Setup Class'))
        self.log.info('[setup class] started: {}'.format(datetime.now().isoformat()))

    def setup_method(self):
        """Run before each test method runs."""
        self._timer_method_start = time.time()
        self._current_test = os.environ.get('PYTEST_CURRENT_TEST').split(' ')[0]
        test_path = os.path.dirname(self._current_test.split('::')[0])
        self._profile_file = os.path.join(self._app_path, test_path, 'profiles.json')
        self.log.info('{0} {1} {0}'.format('=' * 10, self._current_test))
        self.log.info('[setup method] started: {}'.format(datetime.now().isoformat()))
        self.context = os.getenv('TC_PLAYBOOK_DB_CONTEXT', str(uuid.uuid4()))
        self.log.info('[setup method] Context: {}'.format(self.context))

    @property
    def stager(self):
        """Return instance of Stager class."""
        return Stager(self.tcex(self.default_args), logger)

    def teardown_class(self):
        """Run once before all test cases."""
        self.log.info('{0} {1} {0}'.format('^' * 10, 'Teardown Class'))
        self.log.info(
            '[teardown class] Finished: {}, Elapsed: {}'.format(
                datetime.now().isoformat(), time.time() - self._timer_class_start
            )
        )

    def teardown_method(self):
        """Run after each test method runs."""
        self.log.info(
            '[teardown method] Finished: {}, Elapsed: {}'.format(
                datetime.now().isoformat(), time.time() - self._timer_method_start
            )
        )

    def tcex(self, args=None):
        """Return an instance of App."""
        args = args or {}
        app_args = self.default_args
        app_args.update(args)
        if (
            self._tcex is not None
            and self.context == self._tcex.default_args.tc_playbook_db_context
        ):
            print('tcex already exists', self._tcex.default_args)
            self._tcex.tcex_args.inject_params(app_args)  # during run this is required
            return self._tcex

        sys.argv = [
            sys.argv[0],
            '--tc_log_path',
            'log',
            '--tc_log_file',
            '{}-app.log'.format(self.context),
        ]
        self._tcex = TcEx()
        self._tcex.tcex_args.inject_params(app_args)  # required for stager
        print('new tcex', self._tcex.default_args)
        return self._tcex

    @property
    def validator(self):
        """Return instance of Stager class."""
        return Validator(self.tcex(self.default_args), logger)


class TestCasePlaybook(TestCase):
    """Playbook TestCase Class"""

    _output_variables = None
    redis_staging_data = []
    redis_client = None

    def _exit(self, code):
        """Log and return exit code"""
        self.log.info('[runner] Exit Code: {}'.format(code))
        self.tcex().log.info('Exit Code: {}'.format(code))
        return code

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
        profiles_data = None
        with open(self._profile_file, 'r') as profiles:
            profiles_data = json.load(profiles)
            if profile_name not in list(profiles_data.keys()):
                return
            if profiles_data.get(profile_name).get('outputs') is not None:
                return

        if not profiles_data:
            return

        with open(self._profile_file, 'w') as profiles:
            redis_data = self.redis_client.hgetall(self.context)
            outputs = {}
            for item in list(redis_data.items()):
                if item[0].decode('UTF-8') in self.output_variables:
                    outputs[item[0].decode('UTF-8')] = {
                        'expected_output': re.sub(r'(^")|("$)', '', item[1].decode('UTF-8')),
                        'op': 'eq',
                    }
            profiles_data.get(profile_name)['outputs'] = outputs
            json.dump(profiles_data, profiles, indent=2)

    def profile(self, profile_name):
        """Get a profile from the profiles.json file by name"""
        profile = None
        with open(self._profile_file, 'r') as profiles:
            data = json.load(profiles)
            profile = data.get(profile_name, None)
        return profile

    def run(self, args):  # pylint: disable=too-many-return-statements
        """Run the Playbook App.

        Args:
            args (dict): The App CLI args.

        Returns:
            [type]: [description]
        """
        args['tc_playbook_out_variables'] = ','.join(self.output_variables)
        app = self.app(args)

        # Start
        try:
            app.start()
        except SystemExit as e:
            self.log.error('App failed in start() method ({}).'.format(e))
            return self._exit(e)
        except Exception as err:
            self.log.error('App encountered except in start() method ({}).'.format(err))
            return self._exit(1)

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
            return self._exit(e)
        except Exception as err:
            self.log.error('App encountered except in run() method ({}).'.format(err))
            return self._exit(1)

        # Write Output
        try:
            app.write_output()
        except SystemExit as e:
            self.log.error('App failed in write_output() method ({}).'.format(e))
            return self._exit(e)
        except Exception as err:
            self.log.error('App encountered except in write_output() method ({}).'.format(err))
            return self._exit(1)

        # Done
        try:
            app.done()
        except SystemExit as e:
            self.log.error('App failed in done() method ({}).'.format(e))
            return self._exit(e)
        except Exception as err:
            self.log.error('App encountered except in done() method ({}).'.format(err))
            return self._exit(1)

        return self._exit(app.tcex.exit_code)

    def run_profile(self, profile_name):
        """Run an App using the profile name."""
        profile = self.profile(profile_name)
        if not profile:
            self.log.error('No profile named {} found.'.format(profile_name))
            return self._exit(1)

        # stage any staging data
        # self.stage_data(profile.get('stage', {}))
        # self.stager.redis.from_dict(profile.get('stage', {}))
        self.stager.redis.from_dict(profile.get('stage', {}).get('redis', {}))

        # build args from install.json
        args = {}
        args.update(profile.get('inputs', {}).get('required', {}))
        args.update(profile.get('inputs', {}).get('optional', {}))
        if not args:
            self.log.error('No profile named {} found.'.format(profile_name))
            self._exit(1)

        # run the App
        exit_code = self.run(args)

        # populate the output variables
        self.populate_output_variables(profile_name)

        return self._exit(exit_code)

    def setup_method(self):
        """Run before each test method runs."""
        super().setup_method()
        self.stager.redis.from_dict(self.redis_staging_data)
        self.redis_client = self.tcex().playbook.db.r

    def stage_data(self, staged_data):
        """Stage the data in the profile."""
        for key, value in list(staged_data.get('redis', {}).items()):
            self.stager.redis.stage(key, value)

        # TODO: stage threatconnect data

    def teardown_method(self):
        """Run after each test method runs."""
        r = self.stager.redis.delete_context(self.context)
        self.log.info('[teardown method] Delete Key Count: {}'.format(r))
        super().teardown_method()
