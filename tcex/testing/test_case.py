# -*- coding: utf-8 -*-
"""TcEx testing Framework."""
import json
import logging
import os
import re
import time
import uuid
import sys
import traceback
from datetime import datetime
from tcex import TcEx
from tcex.tcex_logger import FileHandlerCustom
from .stage_data import Stager
from .validate_data import Validator

logger = logging.getLogger('TestCase')
lfh = FileHandlerCustom('log/tests.log')
lfh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
lfh.setFormatter(formatter)
logger.addHandler(lfh)
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
            '{}/app.log'.format(self.context),
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

    def log_data(self, stage, label, data, level='info'):
        """Log validation data."""
        msg = '{!s:>20} : {!s:<15}: {!s:<50}'.format('[{}]'.format(stage), label, data)
        getattr(self.log, level)(msg)

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
