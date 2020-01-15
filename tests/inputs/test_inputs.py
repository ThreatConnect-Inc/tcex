# -*- coding: utf-8 -*-
"""Test the TcEx Inputs Config Module."""
import json
import sys
from random import randint
from requests import Session

from tcex.inputs import Inputs


class MockGet:
    """Mock tcex session.get() method."""

    def __init__(self, data, ok=True):
        """Initialize class properties."""
        self.data = data
        self._ok = ok

    @property
    def headers(self):
        """Mock headers property"""
        return {'content-type': 'application/json'}

    def json(self):
        """Mock json method"""
        return self.data

    @property
    def ok(self):
        """Mock ok property"""
        return self._ok

    @property
    def reason(self):
        """Mock text property"""
        return 'reason'

    @property
    def text(self):
        """Mock text property"""
        return json.dumps(self.data)


class TestInputsConfig:
    """Test TcEx Inputs Config."""

    @staticmethod
    def test_add_inputs(playbook_app):
        """Test argument_parser add_argument method with a required field and config_data.

        Args:
            playbook_app (callable, fixture): An instantiated instance of MockApp.
        """
        # update config data
        config_data = {
            'name': 'pytest',
            'logging': 'trace',
            'tc_log_to_api': True,
        }

        # initialize tcex and add required argument
        tcex = playbook_app(config_data=config_data).tcex
        tcex.parser.add_argument('--name', required=True)

        # parse args
        assert tcex.args.name == config_data.get('name')

    @staticmethod
    def test_aot_inputs(playbook_app, redis_client):
        """Test AOT input method of TcEx

        Args:
            playbook_app (callable, fixture): An instantiated instance of MockApp.
            redis_client (Redis.client, fixture): An instantiated instance of Redis Client.
        """
        # add AOT setting to App
        config_data = {
            'tc_action_channel': f'pytest-action-channel-{randint(1000,9999)}',
            'tc_aot_enabled': True,
        }
        app = playbook_app(config_data=config_data)

        # send redis rpush AOT message
        aot_config_data = {'my_bool': 'true', 'my_multi': 'one|two'}
        aot_config_data.update(app.config_data)
        aot_msg = {'type': 'execute', 'params': aot_config_data}
        redis_client.rpush(config_data.get('tc_action_channel'), json.dumps(aot_msg))

        # get a configured instance of tcex, missing AOT values
        # tcex will block, check for the AOT method, parse new config, and then run
        tcex = app.tcex

        # add custom args (install.json defined in conftest.py)
        tcex.parser.add_argument('--my_bool', action='store_true')
        tcex.parser.add_argument('--my_multi', action='append')

        # args and rargs must be called once before accessing args
        tcex.args  # pylint: disable=pointless-statement
        tcex.rargs  # pylint: disable=pointless-statement

        assert tcex.inputs.params.my_bool is True
        assert tcex.inputs.resolved_params.my_bool is True
        assert tcex.args.my_bool is True
        assert tcex.rargs.my_bool is True  # pylint: disable=no-member
        assert tcex.args.my_multi == ['one', 'two']
        assert tcex.rargs.my_multi == ['one', 'two']  # pylint: disable=no-member

    @staticmethod
    def test_args_token(tcex):
        """Test default values (e.g., token) are in args.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
        """
        assert tcex.args.tc_token
        assert tcex.args.tc_token_expires
        assert tcex.args.api_default_org == 'TCI'

    @staticmethod
    def test_config_file(tcex):
        """Test inputs.config_file() method.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
        """
        tcex.inputs.config_file('tests/inputs/config.json')
        tcex.inputs.config_file('tests/inputs/dummy-config.json')

    @staticmethod
    def test_cli_args(playbook_app, request):
        """Test args passed via cli.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
            request (pytest.request, fixture): The built-in request object from pytest.
        """
        app = playbook_app(clear_argv=False)

        # store config data
        config_data = app.config_data
        # clear the config data to test cli args
        app._config_data = {}

        # backup current sys.argv
        sys_argv_orig = sys.argv

        # build new sys.argv
        sys.argv = sys.argv[:1] + [
            '--tc_token',
            config_data.get('tc_token'),
            '--tc_token_expires',
            config_data.get('tc_token_expires'),
            '--tc_log_file',
            config_data.get('tc_log_file'),
            '--pytest_arg',
            request.node.name,
            '--unknown',
        ]

        tcex = app.tcex
        tcex.parser.add_argument('--pytest_arg')

        # parse tcex.args
        tcex.args  # pylint: disable=pointless-statement

        # assert
        assert tcex.args.pytest_arg == request.node.name

        # restore previous sys.argv
        sys.argv = sys_argv_orig

    @staticmethod
    def test_get_secure_params(playbook_app, monkeypatch):
        """Test secure params feature of TcEx inputs.

        Args:
            playbook_app (callable, fixture): An instantiated instance of MockApp.
            monkeypatch (_pytest.monkeypatch.MonkeyPatch, fixture): Pytest monkeypatch
        """
        app = playbook_app()
        tcex = app.tcex

        # monkeypatch method
        def mp_get(*args, **kwargs):  # pylint: disable=unused-argument
            return MockGet({'inputs': app.config_data})

        monkeypatch.setattr(tcex.session, 'get', mp_get)

        data = tcex.inputs._get_secure_params()

        assert data.get('tc_log_path') == 'log'

    @staticmethod
    def test_get_secure_params_mock_env_server(playbook_app, monkeypatch):
        """Test secure params feature of TcEx inputs as working on env server.

        Args:
            playbook_app (callable, fixture): An instantiated instance of MockApp.
            monkeypatch (_pytest.monkeypatch.MonkeyPatch, fixture): Pytest monkeypatch
            request (_pytest.request, fixture): Pytest request
        """
        app = playbook_app(clear_argv=False)

        # store config data
        config_data = dict(app.config_data)

        # clear the config data to test cli args
        app._config_data = {}

        # backup current sys.argv
        sys_argv_orig = sys.argv

        # build new sys.argv
        sys.argv = sys.argv[:1] + [
            '--tc_secure_params',
            '--tc_token',
            config_data.get('tc_token'),
            '--tc_token_expires',
            config_data.get('tc_token_expires'),
            '--tc_log_path',
            config_data.get('tc_log_path'),
            '--tc_log_file',
            config_data.get('tc_log_file'),
        ]

        # monkeypatch method
        secure_params = dict(app.config_data)
        secure_params['tc_log_path'] = 'bad-log.log'
        secure_params['pytest_secure_params'] = 'pytest_secure_params'

        def mp_get(*args, **kwargs):  # pylint: disable=unused-argument
            return MockGet({'inputs': secure_params})

        # monkey patch Session.get() method to return mock secureParams data
        monkeypatch.setattr(Session, 'get', mp_get)

        # get instance of tcex
        tcex = app.tcex
        tcex.parser.add_argument('--pytest_secure_params')

        # assert tc_log_path didn't change with incoming secure param value
        assert tcex.args.tc_log_path == 'log'
        # ensure secure params worked
        assert tcex.args.pytest_secure_params == 'pytest_secure_params'

        # restore previous sys.argv
        sys.argv = sys_argv_orig

    @staticmethod
    def test_get_secure_params_bad_data(tcex, monkeypatch):
        """Test secure params feature of TcEx inputs with bad data.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
            monkeypatch (_pytest.monkeypatch.MonkeyPatch, fixture): Pytest monkeypatch
        """
        # monkeypatch method
        def mp_get(*args, **kwargs):  # pylint: disable=unused-argument
            return MockGet({})

        monkeypatch.setattr(tcex.session, 'get', mp_get)

        try:
            tcex.inputs._get_secure_params()
            assert False
        except RuntimeError:
            assert True

    @staticmethod
    def test_get_secure_params_not_ok(tcex, monkeypatch):
        """Test secure params failure.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
            monkeypatch (_pytest.monkeypatch.MonkeyPatch, fixture): Pytest monkeypatch
        """
        # monkeypatch method
        def mp_get(*args, **kwargs):  # pylint: disable=unused-argument
            return MockGet(data={}, ok=False)

        monkeypatch.setattr(tcex.session, 'get', mp_get)

        try:
            tcex.inputs._get_secure_params()
        except RuntimeError:
            assert True

    @staticmethod
    def test_secure_params(playbook_app, monkeypatch):
        """Test secure params failure.

        Args:
            playbook_app (callable, fixture): An instantiated instance of MockApp.
            monkeypatch (_pytest.monkeypatch.MonkeyPatch, fixture): Pytest monkeypatch
        """
        config_data = {'tc_secure_params': True}
        app = playbook_app(config_data=config_data)

        # create fields only send in secure params
        secure_params_config_data = {'my_bool': 'true', 'my_multi': 'one|two'}
        secure_params_config_data.update(app.config_data)

        # monkeypatch session get method
        def get_secure_params(self):  # pylint: disable=unused-argument
            return secure_params_config_data

        monkeypatch.setattr(Inputs, '_get_secure_params', get_secure_params)

        # get instance of tcex
        tcex = app.tcex

        # add custom args (install.json defined in conftest.py)
        tcex.parser.add_argument('--my_bool', action='store_true')
        tcex.parser.add_argument('--my_multi', action='append')

        # args and rargs must be called once before accessing args
        tcex.args  # pylint: disable=pointless-statement
        tcex.rargs  # pylint: disable=pointless-statement

        assert tcex.args.my_bool is True
        assert tcex.rargs.my_bool is True  # pylint: disable=no-member
        assert tcex.args.my_multi == ['one', 'two']
        assert tcex.rargs.my_multi == ['one', 'two']  # pylint: disable=no-member

    @staticmethod
    def test_update_logging(playbook_app):
        """Test update logging method of inputs module

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex = playbook_app(config_data={'tc_log_level': None, 'logging': 'trace'}).tcex
        tcex.log.info('update logging test')

    @staticmethod
    def test_update_params(tcex, config_data):
        """Test secure params failure.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
            monkeypatch (_pytest.monkeypatch.MonkeyPatch, fixture): Pytest monkeypatch
        """
        # add custom config data
        config_data = {
            'my_bool': 'true',
            'my_multi': 'one|two',
            'unknown_args': True,  # coverage: test unknown args
        }

        # update params
        updated_params = tcex.inputs.update_params(config_data)
        tcex.inputs.config(updated_params)

        # add custom args (install.json defined in conftest.py)
        tcex.parser.add_argument('--my_bool', action='store_true')
        tcex.parser.add_argument('--my_multi', action='append')

        # args and rargs must be called once before accessing args
        tcex.args  # pylint: disable=pointless-statement
        tcex.rargs  # pylint: disable=pointless-statement

        assert tcex.args.my_bool is True
        assert tcex.rargs.my_bool is True  # pylint: disable=no-member
        assert tcex.args.my_multi == ['one', 'two']
        assert tcex.rargs.my_multi == ['one', 'two']  # pylint: disable=no-member
