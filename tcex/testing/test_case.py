# -*- coding: utf-8 -*-
"""TcEx testing Framework."""
# standard library
import json
import os
import random
import string
import time
import traceback
import uuid
from datetime import datetime

# third-party
import pytest
import urllib3
from requests import Session

# first-party
from tcex import TcEx
from tcex.app_config_object.install_json import InstallJson
from tcex.env_store import EnvStore
from tcex.profile import Profile
from tcex.utils import Utils

from .stage_data import Stager
from .test_logger import logger
from .test_session import TestSession
from .validate_data import Validator

# disable ssl warning message
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TestCase:
    """Base TestCase Class"""

    _app_path = os.getcwd()
    _current_test = None
    _default_args = None
    _profile = None
    _session_admin = None
    _session_exchange = None
    _stager = None
    _staged_tc_data = []
    _timer_class_start = None
    _timer_method_start = None
    _validator = None
    app = None
    context = None
    enable_update_profile = False
    env = set(os.getenv('TCEX_TEST_ENVS', 'build').split(','))
    env_store = EnvStore(logger=logger)
    ij = InstallJson(logger=logger)
    initialized = False
    log = logger
    redis_client = None
    session = Session()
    tcex = None
    tcex_testing_context = None
    utils = Utils()

    def _reset_property_flags(self):
        """Reset all control flag."""
        # used to prevent pytest from executing @property methods
        self.initialized = False
        self.tcex = False

    def _log_args(self, args):
        """Log args masking any that are marked encrypted and log warning for unknown args.

        Args:
            args (dict): A dictionary of args.
        """
        for name, value in sorted(args.items()):
            input_data = self.ij.params_dict.get(name)
            if input_data is None and name not in self.default_args:
                # if name is not in install.json and not a default arg log a warning
                if name not in ['tcex_testing_context']:  # values that should not cause a warning
                    self.log.data('run', 'input', f'{name}: unknown arg.', 'warning')
            elif input_data is not None and input_data.get('encrypt') is True:
                self.log.data('run', 'input', f'{name}: ***')
            else:
                self.log.data('run', 'input', f'{name}: {value}')

    @staticmethod
    def _to_bool(value):
        """Return bool value from int or string."""
        return str(value).lower() in ['1', 'true']

    def _update_args(self, args):
        """Update args before running App."""

        if self.ij.runtime_level.lower() in ['playbook']:
            # set requested output variables
            args['tc_playbook_out_variables'] = self.profile.tc_playbook_out_variables

        # update path args
        self._update_path_args(args)

        # update default args with app args
        app_args = self.default_args.copy()
        app_args.update(args)

        # update default args with app args
        app_args['tc_logger_name'] = self.context

        # safely log all args to tests.log
        self._log_args(app_args)

        return app_args

    def _update_path_args(self, args):
        """Update path in args for each test profile."""
        # service Apps do not have a profile when this is needed.
        profile = self.profile or Profile(default_args=self.default_args.copy())
        args['tc_in_path'] = profile.tc_in_path
        args['tc_log_path'] = profile.tc_log_path
        args['tc_out_path'] = profile.tc_out_path
        args['tc_temp_path'] = profile.tc_temp_path

    @property
    def api_access_id(self):
        """Return TC API Access ID"""
        return self.env_store.getenv('/ninja/tc/tci/exchange_admin/api_access_id')

    @property
    def api_secret_key(self):
        """Return TC API Secret Key"""
        return self.env_store.getenv('/ninja/tc/tci/exchange_admin/api_secret_key')

    @staticmethod
    def check_environment(environments, os_environments=None):
        """Check if test case matches current environments, else skip test.

        Args:
            environments (list): The test case environments.
            os_environments (list): The user/os defined environment.
        """
        test_envs = environments or ['build']
        os_envs = set(os.environ.get('TCEX_TEST_ENVS', 'build').split(','))
        if os_environments:
            os_envs = set(os_environments)
        if not os_envs.intersection(set(test_envs)):
            pytest.skip('Profile skipped based on current environment.')

    def create_config(self, args):
        """Create files necessary to start a Service App."""
        config = self._update_args(args)

        # service Apps will get their args/params from encrypted file in the "in" directory
        data = json.dumps(config, sort_keys=True).encode('utf-8')
        key = ''.join(random.choice(string.ascii_lowercase) for i in range(16))
        encrypted_data = self.utils.encrypt_aes_cbc(key, data)

        # ensure that the in directory exists
        os.makedirs(config.get('tc_in_path'), exist_ok=True)

        # write the file in/.app_params.json
        app_params_json = os.path.join(config.get('tc_in_path'), '.test_app_params.json')
        with open(app_params_json, 'wb') as fh:
            fh.write(encrypted_data)

        # create environment variable for tcex inputs method to pick up to read encrypted file
        os.environ['TC_APP_PARAM_KEY'] = key
        os.environ['TC_APP_PARAM_FILE'] = app_params_json

    @property
    def default_args(self):
        """Return App default args."""
        if self._default_args is None and self.initialized:
            self._default_args = {
                # local override TCI_EXCHANGE_ADMIN_API_ACCESS_ID
                'api_access_id': self.api_access_id,
                'api_default_org': os.getenv('API_DEFAULT_ORG', 'TCI'),
                # local override TCI_EXCHANGE_ADMIN_API_SECRET_KEY
                'api_secret_key': self.api_secret_key,
                'tc_api_path': self.tc_api_path,
                'tc_in_path': os.getenv('TC_IN_PATH', 'log'),
                'tc_log_level': os.getenv('TC_LOG_LEVEL', 'trace'),
                'tc_log_path': os.getenv('TC_LOG_PATH', 'log'),
                'tc_log_to_api': self._to_bool(os.getenv('TC_LOG_TO_API', 'false')),
                'tc_logger_name': 'tcex',
                'tc_out_path': os.getenv('TC_OUT_PATH', 'log'),
                'tc_proxy_external': self._to_bool(os.getenv('TC_PROXY_EXTERNAL', 'false')),
                # local override TC_PROXY_HOST
                'tc_proxy_host': self.env_store.getenv(
                    '/ninja/proxy/tc_proxy_host', default='localhost'
                ),
                # local override TC_PROXY_PASSWORD
                'tc_proxy_password': self.env_store.getenv(
                    '/ninja/proxy/tc_proxy_password', default=''
                ),
                # local override TC_PROXY_PORT
                'tc_proxy_port': self.env_store.getenv(
                    '/ninja/proxy/tc_proxy_port', default='4242'
                ),
                'tc_proxy_tc': self._to_bool(os.getenv('TC_PROXY_TC', 'false')),
                # local override TC_PROXY_USERNAME
                'tc_proxy_username': self.env_store.getenv(
                    '/ninja/proxy/tc_proxy_username', default=''
                ),
                'tc_temp_path': os.getenv('TC_TEMP_PATH', 'log'),
            }

            # try to use token when possible
            token = os.getenv('TC_TOKEN', self.tc_token)
            if token is not None:
                # if token was successfully retrieved from TC use token and remove hmac values
                self._default_args['tc_token'] = token
                self._default_args['tc_token_expires'] = '1700000000'
                del self._default_args['api_access_id']
                del self._default_args['api_secret_key']
        return self._default_args

    def init_profile(self, profile_name, pytestconfig=None, monkeypatch=None, options=None):
        """Stages and sets up the profile given a profile name"""
        self._profile = Profile(
            default_args=self.default_args.copy(),
            name=profile_name,
            pytestconfig=pytestconfig,
            monkeypatch=monkeypatch,
            redis_client=self.redis_client,
            tcex_testing_context=self.tcex_testing_context,
            logger=self.log,
            options=options,
        )

        # Override test environments if specified
        os_environments = None
        if pytestconfig:
            os_environments = pytestconfig.option.environment

        # check profile environment
        self.check_environment(self._profile.environments, os_environments)

        # migrate profile to latest schema
        self._profile.migrate()

        # merge profile inputs (add new / remove non-defined)
        self._profile.merge_inputs()

        # populate profile (env vars, etc)
        self._profile.data = self._profile.populate.replace_env_variables(self._profile.data)

        # validate input fields, this method requires env vars to be populated
        valid, message = self._profile.validate_inputs()

        # stage ThreatConnect data based on current profile, also used in teardown method
        self._staged_tc_data = self.stager.threatconnect.entities(
            self._profile.stage_threatconnect, self._profile.owner
        )
        # insert staged data for replacement
        self._profile.tc_staged_data = self._staged_tc_data

        # Replace staged_data
        self._profile.data = self._profile.populate.replace_tc_variables(self._profile.data)

        # replace all references and all staged variable
        self._profile.init()

        # stage kvstore data based on current profile
        self.stager.redis.from_dict(self._profile.stage_kvstore)

        return valid, message

    @property
    def profile(self):
        """Return profile instance."""
        return self._profile

    def run(self):
        """Implement in Child Class"""
        raise NotImplementedError('Child class must implement this method.')

    def run_app_method(self, app, method):
        """Run the provided App method."""
        try:
            getattr(app, method)()
        except SystemExit as e:
            self.log.data('run', 'Exit Code', e.code)
            if e.code != 0 and self.profile and e.code not in self.profile.exit_codes:
                self.log.data(
                    'run',
                    'App failed',
                    f'App exited with code of {e.code} in method {method}',
                    'error',
                )
            app.tcex.log.info(f'Exit Code: {e.code}')
            return e.code
        except Exception:
            self.log.data(
                'run',
                'App failed',
                f'App encountered except in {method}() method ({traceback.format_exc()})',
                'error',
            )
            return 1
        return 0

    @property
    def session_admin(self):
        """Return requests Session object for TC admin account.

        The credential this session uses require special activation in the ThreatConnect Platform
        and is not intended for normal use.
        """
        # APP-102 - adding a session for TC API Admin role request
        api_access_id = self.env_store.getenv('/ninja/tc/system/admin_api/api_access_id')
        api_secret_key = self.env_store.getenv('/ninja/tc/system/admin_api/api_secret_key')
        if (
            self._session_admin is None
            and api_access_id is not None
            and api_secret_key is not None
            and self.tc_api_path is not None
        ):
            # support for a proxy is not a typical use case, but can be added later if needed
            self._session_admin = TestSession(
                api_access_id=api_access_id,
                api_secret_key=api_secret_key,
                api_path=self.tc_api_path,
                logger=self.log,
            )
        return self._session_admin

    @property
    def session_exchange(self):
        """Return requests Session object for TC admin account.

        The credential this session uses require special activation in the ThreatConnect Platform
        and is not intended for normal use.
        """
        # APP-102 - adding a session for TC Exchange Admin role request
        if (
            self._session_exchange is None
            and self.api_access_id is not None
            and self.api_secret_key is not None
            and self.tc_api_path is not None
        ):
            # support for a proxy is not a typical use case, but can be added later if needed
            self._session_exchange = TestSession(
                api_access_id=self.api_access_id,
                api_secret_key=self.api_secret_key,
                api_path=self.tc_api_path,
                logger=self.log,
            )
        return self._session_exchange

    @classmethod
    def setup_class(cls):
        """Run once before all test cases."""
        cls.initialized = True
        cls._timer_class_start = time.time()
        cls.log.title('Setup Class', '#')
        TestCase.log.data('setup class', 'started', datetime.now().isoformat())
        TestCase.log.data('setup class', 'local envs', cls.env)

    def setup_method(self):
        """Run before each test method runs."""
        self._timer_method_start = time.time()
        self._current_test = os.getenv('PYTEST_CURRENT_TEST').split(' ')[0]
        self.log.title(self._current_test, '=')
        self.log.data('setup method', 'started', datetime.now().isoformat())

        # create and log current context
        self.context = os.getenv('TC_PLAYBOOK_DB_CONTEXT', str(uuid.uuid4()))
        self.log.data('setup method', 'context', self.context)

        # setup per method instance of tcex
        args = self.default_args.copy()
        args['tc_log_file'] = os.path.join(self.test_case_log_test_dir, 'setup.log')
        args['tc_logger_name'] = f'tcex-{self.test_case_feature}-{self.test_case_name}'
        self.tcex = TcEx(config=args)

        # initialize new stager instance
        self._stager = self.stager_init()

        # initialize new validator instance
        self._validator = self.validator_init()
        # Adding this for batch to created the -batch and errors files
        with open(os.path.join(self.test_case_log_test_dir, 'DEBUG'), 'w+') as fp:
            fp.close()

    @property
    def stager(self):
        """Return instance of Stager class."""
        return self._stager

    def stager_init(self):
        """Return instance of Stager class."""
        tc_log_file = os.path.join(self.test_case_log_test_dir, 'stage.log')

        # args data
        args = self.default_args.copy()

        # override default log level if profiled
        args['tc_log_level'] = 'warning'

        # set log path to be the feature and test case name
        args['tc_log_file'] = tc_log_file

        # set a logger name to have a logger specific for stager
        args['tc_logger_name'] = 'tcex-stager'

        tcex = TcEx(config=args)
        return Stager(tcex, logger)

    @property
    def tc_api_path(self):
        """Return TC Api Path."""
        return os.getenv('TC_API_PATH')

    @property
    def tc_token(self):
        """Return a valid API token.

        note:: requires TC >= 6.0
        """
        if self.tc_api_path is None:  # no API path, no token
            return None
        data = None
        token = None
        token_url_path = self.env_store.getenv('/ninja/tc/token/url_path', env_type='remote')
        if token_url_path is None:
            # could not retrieve URL path
            return None

        # determine the token type
        token_type = 'api'
        if self.ij.runtime_level.lower() in ['triggerservice', 'webhooktriggerservice']:
            data = {'serviceId': os.getenv('TC_TOKEN_SVC_ID', '407')}
            token_type = 'svc'

        # retrieve token from API using HMAC auth
        r = self.session_exchange.post(f'{token_url_path}/{token_type}', json=data, verify=True)
        if r.status_code == 200:
            token = r.json().get('data')
            self.log.data('setup', 'Using Token', token)
            self.log.data('setup', 'Token Elapsed', r.elapsed, 'trace')
        return token

    @classmethod
    def teardown_class(cls):
        """Run once before all test cases."""
        cls.initialized = False
        cls.log.title('Teardown Class', '^')
        TestCase.log.data('teardown class', 'finished', datetime.now().isoformat())
        TestCase.log.data('teardown class', 'elapsed', time.time() - cls._timer_class_start)

    def teardown_method(self):
        """Run after each test method runs."""
        if self.enable_update_profile and self.ij.runtime_level.lower() not in [
            'triggerservice',
            'webhooktriggerservice',
        ]:
            # exit message can not be validated for a Service App
            self.profile.update_exit_message()

        # delete threatconnect staged data
        self.stager.threatconnect.delete_staged(self._staged_tc_data)

        # log running times
        self.log.data('teardown method', 'finished', datetime.now().isoformat())
        self.log.data('teardown method', 'elapsed', time.time() - self._timer_class_start)

        # APP-262 - close out loggers
        self.tcex.logger.shutdown()
        self.stager.tcex.logger.shutdown()
        self.validator.tcex.logger.shutdown()

        # APP-262 - disconnect redis
        self.tcex.redis_client.connection_pool.disconnect()
        self.stager.tcex.redis_client.connection_pool.disconnect()
        self.validator.tcex.redis_client.connection_pool.disconnect()

        # update profile for session data
        self.profile.session_manager.update_profile()

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
    def test_case_log_feature_dir(self):
        """Return profile fully qualified filename."""
        return os.path.join(self._app_path, os.getenv('TC_LOG_PATH', 'log'), self.test_case_feature)

    @property
    def test_case_log_test_dir(self):
        """Return profile fully qualified filename."""
        return os.path.join(self.test_case_log_feature_dir, self.test_case_name)

    @property
    def test_case_name(self):
        """Return partially parsed test case data."""
        return self.test_case_data[-1].replace('/', '-').replace('[', '-').replace(']', '')

    def validate_exit_message(self, test_exit_message, op='eq', **kwargs):
        """Validate App exit message."""
        if test_exit_message is not None:
            message_tc_file = os.path.join(
                os.getenv('TC_OUT_PATH', 'log'),
                self.test_case_feature,
                self.test_case_name,
                'message.tc',
            )
            app_exit_message = None
            if os.path.isfile(message_tc_file):
                with open(message_tc_file, 'r') as mh:
                    app_exit_message = mh.read()

                if app_exit_message:
                    kwargs['title'] = 'Exit Message Validation'
                    kwargs['log_app_data'] = json.dumps(app_exit_message)
                    if op == 'eq':
                        kwargs['log_test_data'] = json.dumps(test_exit_message)

                    # compare
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
        tc_log_file = os.path.join(self.test_case_log_test_dir, 'validate.log')

        # args data
        args = self.default_args.copy()

        # override default log level if profiled
        args['tc_log_level'] = 'warning'

        # set log path to be the feature and test case name
        args['tc_log_file'] = tc_log_file

        # set a logger name to have a logger specific for stager
        args['tc_logger_name'] = 'tcex-validator'

        tcex = TcEx(config=args)
        return Validator(tcex, logger)
