# -*- coding: utf-8 -*-
"""TcEx testing Framework."""
import json
import logging
import os
import random
import re
import string
import time
import traceback
import uuid
from datetime import datetime
import jmespath

import pytest
from tcex import TcEx
from tcex.inputs import FileParams

from ..logger import RotatingFileHandlerCustom
from .stage_data import Stager
from .validate_data import Validator

logger = logging.getLogger('TestCase')
lfh = RotatingFileHandlerCustom(filename='log/tests.log')
lfh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
lfh.setFormatter(formatter)
logger.addHandler(lfh)
logger.setLevel(logging.DEBUG)


class TestCase:
    """Base TestCase Class"""

    _app_path = os.getcwd()
    _current_test = None
    _input_params = None
    _install_json = None
    _stager = None
    _staged_tc_data = []
    _tc_output_variables = {}
    _timer_class_start = None
    _timer_method_start = None
    _validator = None
    app = None
    context = None
    enable_update_profile = False
    log = logger
    env = set(os.getenv('TCEX_TEST_ENVS', 'build').split(','))
    tcex = None

    @staticmethod
    def _convert_variable_name(variable_name):
        """Convert a TC output variable to the correct name"""
        if not variable_name.startswith('${tcenv.'):
            variable_name = '${tcenv.' + variable_name
        if not variable_name.endswith('}'):
            variable_name = variable_name + '}'
        return variable_name

    def _exit(self, code):
        """Log and return exit code"""
        self.log.info(f'[run] Exit Code: {code}')
        return code

    @staticmethod
    def _to_bool(value):
        """Return bool value from int or string."""
        return str(value).lower() in ['1', 'true']

    def add_tc_output_variable(self, variable_name, variable_value):
        """Add a TC output variable to the output variable dict"""
        self._tc_output_variables[variable_name] = variable_value

    def app_init(self, args):
        """Return an instance of App."""
        from app import App  # pylint: disable=import-error

        # return App(self.get_tcex(args))
        args = args or {}

        # update App paths
        args['tc_in_path'] = os.path.join(
            self.default_args.get('tc_in_path'), self.test_case_feature
        )
        args['tc_log_path'] = os.path.join(
            self.default_args.get('tc_log_path'), self.test_case_feature, self.test_case_name
        )
        args['tc_out_path'] = os.path.join(
            self.default_args.get('tc_out_path'), self.test_case_feature, self.test_case_name
        )
        args['tc_temp_path'] = os.path.join(
            self.default_args.get('tc_temp_path'), self.test_case_feature, self.test_case_name
        )

        # update default args with app args
        app_args = dict(self.default_args)
        app_args.update(args)
        # app_args['tc_log_file'] = f'{self.test_case_name}.log'
        app_args['tc_logger_name'] = self.context

        if self.install_json.get('runtimeLevel').lower() in [
            'triggerservice',
            'webhooktriggerservice',
        ]:
            # service Apps will get their args/params from encrypted file in the "in" directory
            data = json.dumps(app_args, sort_keys=True).encode('utf-8')
            key = ''.join(random.choice(string.ascii_lowercase) for i in range(16))

            fp = FileParams()
            fp.EVP_EncryptInit(fp.EVP_aes_128_cbc(), key.encode('utf-8'), b'\0' * 16)
            encrypted_data = fp.EVP_EncryptUpdate(data) + fp.EVP_EncryptFinal()

            app_params_json = os.path.join(self.test_case_feature_dir, '.app_params.json')
            with open(app_params_json, 'wb') as fh:
                fh.write(encrypted_data)

            # create environment variable for tcex inputs method to pick up to read encrypted file
            os.environ['TC_APP_PARAM_KEY'] = key
            os.environ['TC_APP_PARAM_FILE'] = app_params_json

            # tcex will read args/params from encrypted file
            tcex = TcEx()
        else:
            tcex = TcEx(config=app_args)

        return App(tcex)

    @staticmethod
    def check_environment(environments):
        """Check if test case matches current environments, else skip test.

        Args:
            environments (list): The test case environments.
        """
        test_envs = environments or ['build']
        os_envs = set(os.environ.get('TCEX_TEST_ENVS', 'build').split(','))
        if not os_envs.intersection(set(test_envs)):
            pytest.skip('Profile skipped based on current environment.')

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

    def generate_tc_output_variables(self, staged_tc_data):
        """Generate all of the TC output variables given the profiles staged data"""
        for staged_data in staged_tc_data:
            self.add_tc_output_variable(staged_data.get('key'), staged_data.get('data'))

    def update_profile(self, profile_name):
        """Update the profile format"""
        with open(os.path.join(self.test_case_profile_dir, f'{profile_name}.json'), 'r+') as fh:
            data = json.load(fh)
            data = self.update_staged_threatconnect_data(data)
            fh.seek(0)
            fh.write(json.dumps(data, indent=2, sort_keys=True))
            fh.truncate()

    @staticmethod
    def update_staged_threatconnect_data(data):
        """Update the stage threatconnect profile section"""
        if 'stage' not in data.keys():
            return data
        tc_data = data.get('stage').get('threatconnect', None)
        if not isinstance(tc_data, list):
            return data

        data['stage']['threatconnect'] = {}
        if not tc_data:
            return data

        counter = 0
        for item in tc_data:
            data['stage']['threatconnect'][f'item_{counter}'] = item
            counter += 1

        return data

    def init_profile(self, profile_name):
        """Get a profile from the profiles.json file by name

        Args:
            profile_name (str): The profile name.

        Returns:
            dict: The profile data.
        """
        try:
            self.update_profile(profile_name)
            with open(os.path.join(self.test_case_profile_dir, f'{profile_name}.json'), 'r') as fh:
                profile = json.load(fh)
        except OSError:
            self.log.error(f'No profile {profile_name} provided.')
            return self._exit(1)
        profile['name'] = profile_name

        profile = self.populate_system_variables(profile)
        self._staged_tc_data = self.stager.threatconnect.entities(
            profile.get('stage', {}).get('threatconnect', {}), self.owner(profile)
        )
        self.generate_tc_output_variables(self._staged_tc_data)
        profile = self.populate_threatconnect_variables(profile)
        self.stager.redis.from_dict(profile.get('stage', {}).get('redis', {}))
        return profile

    @property
    def install_json(self):
        """Return install.json contents."""
        file_fqpn = os.path.join(self._app_path, 'install.json')
        if self._install_json is None:
            if os.path.isfile(file_fqpn):
                with open(file_fqpn, 'r') as fh:
                    self._install_json = json.load(fh)
            else:
                print(f'File "{file_fqpn}" could not be found.')
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
        msg = f"{f'[{stage}]'!s:>20} : {label!s:<15}: {data!s:<50}"
        getattr(self.log, level)(msg)

    @staticmethod
    def owner(profile):
        """Get the owner provided a profile"""
        return (
            profile.get('required', {}).get('owner')
            or profile.get('optional', {}).get('owner')
            or profile.get('owner')
        )

    @staticmethod
    def populate_system_variables(profile):
        """Replace all System variables with their correct value"""
        profile_str = json.dumps(profile)
        system_var_regex = r'\${env.(.*?)}'
        for m in re.finditer(system_var_regex, profile_str):
            old_string = '${env.' + m.group(1) + '}'
            if os.getenv(m.group(1)):
                profile_str = profile_str.replace(old_string, os.getenv(m.group(1)))

        return json.loads(profile_str)

    def populate_threatconnect_variables(self, profile):
        """Replace all of the TC output variables in the profile with their correct value"""
        profile_str = json.dumps(profile)
        for key, value in self._tc_output_variables.items():
            regex = r'\${tcenv\.' + str(key) + '([^}]*)'
            for m in re.finditer(regex, profile_str):
                if m.group(1):
                    key = '${tcenv.' + key + m.group(1) + '}'
                    group = m.group(1)[1:]
                    value = jmespath.search(group, value)
                    profile_str = profile_str.replace(key, str(value))
        return json.loads(profile_str)

    def populate_exit_message(self):
        """Generate validation rules from App outputs."""
        message_tc_file = os.path.join(
            self.default_args.get('tc_out_path'),
            self.test_case_feature,
            self.test_case_name,
            'message.tc',
        )
        message_tc = ''
        if os.path.isfile(message_tc_file):
            with open(message_tc_file, 'r') as mh:
                message_tc = mh.read()

        profile_filename = os.path.join(self.test_case_profile_dir, f'{self.profile_name}.json')
        with open(profile_filename, 'r+') as fh:
            profile_data = json.load(fh)

            if profile_data.get('exit_message') is None or isinstance(
                profile_data.get('exit_message'), str
            ):
                # update the profile
                profile_data['exit_message'] = {'expected_output': message_tc, 'op': 'eq'}

                fh.seek(0)
                fh.write(json.dumps(profile_data, indent=2, sort_keys=True))
                fh.truncate()

    def profile(self, profile_name):
        """Stages and sets up the profile given a profile name"""
        return self.init_profile(profile_name)

    @property
    def profile_name(self):
        """Return partially parsed test case data."""
        name_pattern = r'^test_[a-zA-Z0-9_]+\[(.+)\]$'
        try:
            return re.search(name_pattern, self.test_case_data[-1]).group(1)
        except AttributeError:
            return None

    @property
    def profile_names(self):
        """Get a profile from the profiles.json file by name"""
        profile_names = []
        for filename in sorted(os.listdir(self.test_case_profile_dir)):
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
            value = os.getenv(env_key, value)
        elif envs_var.match(value):
            # read secure value from environment variable
            env_key = envs_var.match(str(value)).groups()[0]
            value = os.getenv(env_key, value)
        return value

    def run(self, args):
        """Implement in Child Class"""
        raise NotImplementedError('Child class must implement this method.')

    def run_app_method(self, app, method):
        """Run the provided App method."""
        try:
            getattr(app, method)()
        except SystemExit as e:
            self.log.info(f'[run] Exit Code: {e.code}')
            self.log.error(f'App failed in {method}() method ({e}).')
            app.tcex.log.info(f'Exit Code: {e.code}')
            return e.code
        except Exception:
            self.log.error(
                f'App encountered except in {method}() method ({traceback.format_exc()}).'
            )
            return 1
        return 0

    @classmethod
    def setup_class(cls):
        """Run once before all test cases."""
        cls._timer_class_start = time.time()
        cls.log.info(f"{'#' * 10} Setup Class {'#' * 10}")
        TestCase.log_data(TestCase(), 'setup class', 'started', datetime.now().isoformat())
        TestCase.log_data(TestCase(), 'setup class', 'local envs', cls.env)

    def setup_method(self):
        """Run before each test method runs."""
        self._timer_method_start = time.time()
        self._current_test = os.getenv('PYTEST_CURRENT_TEST').split(' ')[0]
        self.log.info(f"{'=' * 10} {self._current_test} {'=' * 10}")
        self.log_data('setup method', 'started', datetime.now().isoformat())

        # create and log current context
        self.context = os.getenv('TC_PLAYBOOK_DB_CONTEXT', str(uuid.uuid4()))
        self.log_data('setup method', 'context', self.context)

        # setup per method instance of tcex
        args = dict(self.default_args)
        args['tc_log_file'] = os.path.join(self.test_case_feature, self.test_case_name, 'setup.log')
        args['tc_logger_name'] = f'tcex-{self.test_case_feature}-{self.test_case_name}'
        self.tcex = TcEx(config=args)

        # initialize new stager instance
        self._stager = self.stager_init()

        # initialize new validator instance
        self._validator = self.validator_init()

    @property
    def stager(self):
        """Return instance of Stager class."""
        return self._stager

    def stager_init(self):
        """Return instance of Stager class."""
        tc_log_file = os.path.join(self.test_case_feature, self.test_case_name, 'stage.log')

        # args data
        args = dict(self.default_args)

        # override default log level if profiled
        args['tc_log_level'] = 'warning'

        # set log path to be the feature and test case name
        args['tc_log_file'] = tc_log_file

        # set a logger name to have a logger specific for stager
        args['tc_logger_name'] = 'tcex-stager'

        tcex = TcEx(config=args)
        return Stager(tcex, logger, self.log_data)

    @classmethod
    def teardown_class(cls):
        """Run once before all test cases."""
        cls.log.info(f"{'^' * 10} Teardown Class {'^' * 10}")
        TestCase.log_data(TestCase(), 'teardown class', 'finished', datetime.now().isoformat())
        TestCase.log_data(
            TestCase(), 'teardown class', 'elapsed', time.time() - cls._timer_class_start
        )

    def teardown_method(self):
        """Run after each test method runs."""
        if self.enable_update_profile:
            self.populate_exit_message()
        self.log_data('teardown method', 'finished', datetime.now().isoformat())
        self.log_data('teardown method', 'elapsed', time.time() - self._timer_class_start)

    @property
    def test_case_data(self):
        """Return partially parsed test case data."""
        return os.getenv('PYTEST_CURRENT_TEST').split(' ')[0].split('::')

    @property
    def test_case_feature(self):
        """Return partially parsed test case data."""
        return self.test_case_data[0].split('/')[1].replace('/', '-')

    @property
    def test_case_feature_dir(self):
        """Return profile fully qualified filename."""
        return os.path.join(self._app_path, 'tests', self.test_case_feature)

    @property
    def test_case_profile_dir(self):
        """Return profile fully qualified filename."""
        return os.path.join(self._app_path, 'tests', self.test_case_feature, 'profiles.d')

    @property
    def test_case_name(self):
        """Return partially parsed test case data."""
        return self.test_case_data[-1].replace('/', '-').replace('[', '-').replace(']', '')

    def validate_exit_message(self, test_exit_message, op='eq', **kwargs):
        """Validate App exit message."""
        if test_exit_message is not None:
            message_tc_file = os.path.join(
                self.default_args.get('tc_out_path'),
                self.test_case_feature,
                self.test_case_name,
                'message.tc',
            )
            app_exit_message = None
            if os.path.isfile(message_tc_file):
                with open(message_tc_file, 'r') as mh:
                    app_exit_message = mh.read()

                if app_exit_message:
                    passed, assert_error = self.validator.compare(
                        app_exit_message, test_exit_message, op=op, **kwargs
                    )
                    assert passed, assert_error
                else:
                    assert False, 'The message.tc file was empty.'
            else:
                assert False, f'No message.tc file found at ({message_tc_file}).'

    @property
    def validator(self):
        """Return instance of Stager class."""
        return self._validator

    def validator_init(self):
        """Return instance of Stager class."""
        tc_log_file = os.path.join(self.test_case_feature, self.test_case_name, 'validate.log')

        # args data
        args = dict(self.default_args)

        # override default log level if profiled
        args['tc_log_level'] = 'warning'

        # set log path to be the feature and test case name
        args['tc_log_file'] = tc_log_file

        # set a logger name to have a logger specific for stager
        args['tc_logger_name'] = 'tcex-validator'

        tcex = TcEx(config=args)
        return Validator(tcex, logger, self.log_data)
