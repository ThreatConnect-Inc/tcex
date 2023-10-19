"""TcEx Framework Module"""
# standard library
import json
import os
from collections.abc import Callable
from pathlib import Path
from uuid import uuid4

# first-party
from tcex import TcEx
from tcex.registry import registry
from tests.mock_app import MockApp


class TestInputsConfig:
    """Test TcEx Inputs Config."""

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
            'tc_log_path': os.getcwd(),
            'tc_token': None,
            'tc_expires': None,
            'tc_verify': True,
            'external_config_item': 'some-custom-value',
        }
        # get instance of tcex with config_file kwargs
        tcex = TcEx(config=config_data)

        # print(tcex.inputs.model.json(indent=2))
        assert tcex.inputs.model.external_config_item == config_data.get(  # type: ignore
            'external_config_item'
        )

    @staticmethod
    def test_config_file_kwarg(playbook_app: Callable[..., MockApp]):
        """Test config file input method of TcEx"""
        # have mockApp create an install.json file
        _ = playbook_app()

        # reset registry between tests
        registry._reset()
        config_file = Path('app_config.json')

        # external App config file data
        config_data = {
            'api_default_org': 'TCI',
            'tc_playbook_kvstore_context': str(uuid4()),
            'tc_api_access_id': os.getenv('TC_API_ACCESS_ID'),
            'tc_api_path': os.getenv('TC_API_PATH'),
            'tc_api_secret_key': os.getenv('TC_API_SECRET_KEY'),
            'tc_log_path': os.getcwd(),
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

        # print(tcex.inputs.model.json(indent=2))
        assert tcex.inputs.model.external_config_item == config_data.get(  # type: ignore
            'external_config_item'
        )

        # cleanup config
        config_file.unlink()

    @staticmethod
    def test_input_token(tcex: TcEx):
        """Test default values (e.g., token) are in args."""
        # print(tcex.inputs.model.tc_token.get_secret_value())
        # print(tcex.inputs.model.tc_token_expires)
        assert tcex.inputs.model.tc_token
        assert tcex.inputs.model.tc_token_expires
        assert tcex.inputs.model.api_default_org == 'TCI'


#     @staticmethod
#     def test_update_logging(playbook_app: Callable[..., MockApp]):
#         """Test update logging method of inputs module"""
#         tcex = playbook_app(config_data={'tc_log_level': None, 'logging': 'trace'}).tcex
#         tcex.log.info('update logging test')
#
#     @staticmethod
#     def test_update_params(tcex: TcEx, config_data):
#         """Test secure params failure."""
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
#     def test_duplicate_args(playbook_app: Callable[..., MockApp]):
#         """APP-964 handle args that have been defined multiple times."""
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
