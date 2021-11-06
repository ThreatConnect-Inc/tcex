"""Test the TcEx Inputs Config Module."""
# standard library
import json
import os
from pathlib import Path
from random import randint
from typing import TYPE_CHECKING

# third-party
from pydantic import BaseModel, Extra

# first-party
from tcex import TcEx
from tcex.pleb.registry import registry

if TYPE_CHECKING:
    # third-party
    import redis

    from ..mock_app import MockApp


class TestInputsConfig:
    """Test TcEx Inputs Config."""

    @staticmethod
    def test_aot_inputs(playbook_app: 'MockApp', redis_client: 'redis.Redis'):
        """Test AOT input method of TcEx

        Args:
            playbook_app (fixture): An instance of MockApp.
            redis_client (fixture): An instance of Redis Client.
        """
        registry._reset()

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_bool: bool
            my_multi: list

            class Config:
                """."""

                extra = Extra.allow

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
        tcex.inputs.add_model(PytestModel)

        # print(tcex.inputs.data.json(indent=2))
        assert tcex.inputs.data.my_bool is True
        assert tcex.inputs.data.my_multi == ['one', 'two']

    @staticmethod
    def test_config_kwarg():
        """Test config file input method of TcEx"""
        registry._reset()
        # external App config file data
        config_data = {
            'api_default_org': 'TCI',
            'tc_api_access_id': os.getenv('TC_API_ACCESS_ID'),
            'tc_api_path': os.getenv('TC_API_PATH'),
            'tc_api_secret_key': os.getenv('TC_API_SECRET_KEY'),
            'tc_token': None,
            'tc_expires': None,
            'tc_verify': True,
            'external_config_item': 'some-custom-value',
        }
        # get instance of tcex with config_file kwargs
        tcex = TcEx(config=config_data)

        # print(tcex.inputs.data.json(indent=2))
        assert tcex.inputs.data.external_config_item == config_data.get('external_config_item')

    @staticmethod
    def test_config_file_kwarg():
        """Test config file input method of TcEx"""
        registry._reset()
        config_file = Path('app_config.json')

        # external App config file data
        config_data = {
            'api_default_org': 'TCI',
            'tc_api_access_id': os.getenv('TC_API_ACCESS_ID'),
            'tc_api_path': os.getenv('TC_API_PATH'),
            'tc_api_secret_key': os.getenv('TC_API_SECRET_KEY'),
            'tc_token': None,
            'tc_expires': None,
            'tc_verify': True,
            'external_config_item': 'some-custom-value',
        }

        # write temp config
        with config_file.open(mode='w') as fh:
            json.dump(config_data, fh)

        # get instance of tcex with config_file kwargs
        tcex = TcEx(config_file=config_file)

        # print(tcex.inputs.data.json(indent=2))
        assert tcex.inputs.data.external_config_item == config_data.get('external_config_item')

        # cleanup config
        config_file.unlink()

    @staticmethod
    def test_input_token(tcex):
        """Test default values (e.g., token) are in args.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
        """
        registry._reset()
        # print(tcex.inputs.data.tc_token.get_secret_value())
        # print(tcex.inputs.data.tc_token_expires)
        assert tcex.inputs.data.tc_token
        assert tcex.inputs.data.tc_token_expires
        assert tcex.inputs.data.api_default_org == 'TCI'


#     @staticmethod
#     def test_update_logging(playbook_app):
#         """Test update logging method of inputs module
#
#         Args:
#             playbook_app (callable, fixture): The playbook_app fixture.
#         """
#         tcex = playbook_app(config_data={'tc_log_level': None, 'logging': 'trace'}).tcex
#         tcex.log.info('update logging test')
#
#     @staticmethod
#     def test_update_params(tcex, config_data):
#         """Test secure params failure.
#
#         Args:
#             tcex (TcEx, fixture): An instantiated instance of TcEx.
#             monkeypatch (_pytest.monkeypatch.MonkeyPatch, fixture): Pytest monkeypatch
#         """
#         # add custom config data
#         config_data = {
#             'my_bool': 'true',
#             'my_multi': 'one|two',
#             'unknown_args': True,  # coverage: test unknown args
#         }
#
#         # update params
#         updated_params = tcex.inputs.update_params(config_data)
#         tcex.inputs.config(updated_params)
#
#         # add custom args (install.json defined in conftest.py)
#         tcex.parser.add_argument('--my_bool', action='store_true')
#         tcex.parser.add_argument('--my_multi', action='append')
#
#         # args and rargs must be called once before accessing args
#         tcex.args  # pylint: disable=pointless-statement
#         tcex.rargs  # pylint: disable=pointless-statement
#
#         assert tcex.args.my_bool is True
#         assert tcex.rargs.my_bool is True  # pylint: disable=no-member
#         assert tcex.args.my_multi == ['one', 'two']
#         assert tcex.rargs.my_multi == ['one', 'two']  # pylint: disable=no-member
#
#     @staticmethod
#     def test_duplicate_args(playbook_app):
#         """APP-964 handle args that have been defined multiple times.
#
#         Args:
#             playbook_app (callable, fixture): An instantiated instance of MockApp.
#         """
#         # update config data
#         config_data = {
#             'name': 'pytest',
#             'logging': 'trace',
#             'tc_log_to_api': True,
#         }
#
#         # initialize tcex and add required argument
#         tcex = playbook_app(config_data=config_data).tcex
#         tcex.parser.add_argument('--name', required=True)
#         tcex.parser.add_argument('--name', required=True)
#
#         assert tcex.args.name == 'pytest'
#
#         # parse args
