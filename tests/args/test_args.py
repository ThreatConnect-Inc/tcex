# -*- coding: utf-8 -*-
"""Test the TcEx Args Config Module."""
import json
import sys

from tcex import TcEx
from ..tcex_init import tcex, config_data


class MockGet:
    """Mock tcex session.get() method."""

    def __init__(self, data, ok=True):
        """Initialize class properties."""
        self.data = data
        self.ok = ok

    @property
    def headers(self):
        """Mock headers property"""
        return {'content-type': 'application/json'}

    def json(self):
        """Mock json method"""
        print('!!!!!!!!!!!!', self.data)
        return json.dumps(self.data)

    @property
    def ok(self):
        """Mock ok property"""
        return self.ok

    @property
    def text(self):
        """Mock text property"""
        return 'failed'


# pylint: disable=W0201
class TestArgsConfig:
    """Test TcEx Args Config."""

    @staticmethod
    def test_address_get():
        """Test args."""
        assert tcex.args.tc_token
        assert tcex.args.tc_token_expires
        assert tcex.args.api_default_org == 'TCI'

    # def test_load_secure_params(self, monkeypatch):
    #     """Test load_secure_params method."""
    #     get_orig = tcex.session.get

    #     # monkeypatch method
    #     def mp_get(*args, **kwargs):
    #         return MockGet()

    #     monkeypatch.setattr(tcex.session, 'get', mp_get)

    #     data = tcex.tcex_args._load_secure_params()

    #     assert data.get('tc_log_path') == 'log'

    #     # reset monkeypatched tcex.session.get()
    #     tcex.session.get = get_orig

    # def test_load_secure_params_bad_data(self, monkeypatch):
    #     """Test load_secure_params method."""
    #     get_orig = tcex.session.get

    #     # monkeypatch method
    #     def mp_get(*args, **kwargs):
    #         return MockGet(ok=True, bad_json=True)

    #     monkeypatch.setattr(tcex.session, 'get', mp_get)

    #     try:
    #         tcex.tcex_args._load_secure_params()
    #     except RuntimeError:
    #         assert True

    #     # reset monkeypatched tcex.session.get()
    #     tcex.session.get = get_orig

    # def test_load_secure_params_not_ok(self, monkeypatch):
    #     """Test load_secure_params method."""
    #     get_orig = tcex.session.get

    #     # monkeypatch method
    #     def mp_get(*args, **kwargs):
    #         return MockGet(ok=False)

    #     monkeypatch.setattr(tcex.session, 'get', mp_get)

    #     try:
    #         tcex.tcex_args._load_secure_params()
    #     except RuntimeError:
    #         assert True

    #     # reset monkeypatched tcex.session.get()
    #     tcex.session.get = get_orig

    @staticmethod
    def test_config_file():
        """Test tcex_args.config_file() method."""
        my_tcex = TcEx()
        my_tcex.tcex_args.config_file('tests/args/config.json')
        my_tcex.tcex_args.config_file('tests/args/dummy-config.json')

    @staticmethod
    def test_inject_params():
        """Test tcex_args.config_file() method."""
        my_tcex = TcEx()

        # add custom config data
        config_data['my_bool'] = 'true'
        config_data['my_multi'] = 'one|two'
        config_data['unknown_args'] = True  # test unknown args

        # inject params
        my_tcex.tcex_args.inject_params(config_data)

        # add custom args (install.json defined in conftest.py)
        my_tcex.parser.add_argument('--my_bool', action='store_true')
        my_tcex.parser.add_argument('--my_multi', action='append')

        # parser args
        args = my_tcex.args
        rargs = my_tcex.rargs

        assert args.my_bool is True
        assert rargs.my_bool is True  # pylint: disable=no-member
        assert args.my_multi == ['one', 'two']
        assert rargs.my_multi == ['one', 'two']  # pylint: disable=no-member

    @staticmethod
    def test_aot_args():
        """Test tcex_args.config_file() method."""
        tc_action_channel = 'pytest-action-channel'

        # add custom config data
        config_data['my_bool'] = 'true'
        config_data['my_multi'] = 'one|two'

        # send AOT message
        aot_msg = {'type': 'execute', 'params': config_data}
        tcex.playbook.db.rpush(tc_action_channel, json.dumps(aot_msg))

        # update sys.argv to enable aot
        sys_argv_orig = sys.argv
        sys.argv = sys.argv[:1] + ['--tc_aot_enabled', '--tc_action_channel', tc_action_channel]
        my_tcex = TcEx()

        # add custom args (install.json defined in conftest.py)
        my_tcex.parser.add_argument('--my_bool', action='store_true')
        my_tcex.parser.add_argument('--my_multi', action='append')

        # parser args
        args = my_tcex.args
        rargs = my_tcex.rargs

        assert args.my_bool is True
        assert rargs.my_bool is True  # pylint: disable=no-member
        assert args.my_multi == ['one', 'two']
        assert rargs.my_multi == ['one', 'two']  # pylint: disable=no-member

        # reset sys.argv
        sys.argv = sys_argv_orig

    # @staticmethod
    # def test_secure_params(monkeypatch):
    #     """Test load_secure_params method."""
    #     # add custom config data
    #     config_data['my_bool'] = 'true'
    #     config_data['my_multi'] = 'one|two'

    #     # monkeypatch session get method
    #     @property
    #     def mp_session(self):
    #         def get(*args, **kwargs):
    #             return MockGet({'inputs': config_data})

    #         return self.get

    #     monkeypatch.setattr(TcEx, 'session', mp_session)

    #     # update sys.argv to enable secure_params
    #     sys_argv_orig = sys.argv
    #     sys.argv = sys.argv[:1] + [
    #         '--tc_secure_params',
    #         '--tc_token',
    #         config_data.get('tc_token'),
    #         '--tc_token_expires',
    #         config_data.get('tc_token_expires'),
    #     ]
    #     my_tcex = TcEx()

    #     # add custom args (install.json defined in conftest.py)
    #     my_tcex.parser.add_argument('--my_bool', action='store_true')
    #     my_tcex.parser.add_argument('--my_multi', action='append')

    #     # parser args
    #     args = my_tcex.args
    #     rargs = my_tcex.rargs

    #     assert args.my_bool is True
    #     assert rargs.my_bool is True  # pylint: disable=no-member
    #     assert args.my_multi == ['one', 'two']
    #     assert rargs.my_multi == ['one', 'two']  # pylint: disable=no-member

    #     # reset sys.argv
    #     sys.argv = sys_argv_orig
