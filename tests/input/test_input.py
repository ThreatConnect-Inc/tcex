"""TestInputsConfig for TcEx Framework input configuration validation.

This module contains test cases for the TcEx Framework input configuration functionality,
including testing various input methods such as config kwargs, config file parsing,
token validation, and input parameter processing for different application types.

Classes:
    TestInputsConfig: Test cases for TcEx input configuration validation

TcEx Module Tested: tcex.input.config
"""


import json
import os
from collections.abc import Callable
from pathlib import Path
from uuid import uuid4


from tcex import TcEx
from tcex.registry import registry
from tests.mock_app import MockApp


class TestInputsConfig:
    """TestInputsConfig for TcEx Framework input configuration validation.

    This class provides comprehensive test coverage for TcEx Framework input configuration
    functionality including config kwargs, config file parsing, token validation, and
    input parameter processing across different application deployment scenarios.

    Fixtures:
        playbook_app: Provides configured test application instance with MockApp
        tcex: Provides TcEx instance for testing input configuration
    """

    @staticmethod
    def test_config_kwarg() -> None:
        """Test config data input method using kwargs for TcEx initialization.

        Validates that external configuration data can be passed directly as kwargs to TcEx
        constructor and that custom configuration items are properly accessible through the
        inputs model. Tests registry reset functionality and external config item access.

        Playbook Data Type: Config kwargs with external configuration
        Validation: External config item accessibility, registry reset functionality

        Fixtures:
            None: This test uses direct TcEx instantiation with config kwargs
        """
        registry._reset()
        # external App config file data
        config_data = {
            'api_default_org': 'TCI',
            'tc_api_access_id': os.getenv('TC_API_ACCESS_ID'),
            'tc_api_path': os.getenv('TC_API_PATH'),
            'tc_api_secret_key': os.getenv('TC_API_SECRET_KEY'),
            'tc_log_path': Path.cwd(),
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
    def test_config_file_kwarg(playbook_app: Callable[..., MockApp]) -> None:
        """Test config file input method using file-based configuration for TcEx.

        Validates that external configuration data can be loaded from a JSON config file
        and properly parsed by TcEx. Tests file creation, TcEx initialization with config_file
        parameter, and cleanup of temporary configuration files.

        Playbook Data Type: Config file with JSON configuration data
        Validation: File-based config loading, external config item access, file cleanup

        Args:
            playbook_app: Mock app fixture for creating install.json file

        Fixtures:
            playbook_app: Provides configured test application instance with MockApp
        """
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
            'tc_log_path': Path.cwd(),
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
    def test_input_token(tcex: TcEx) -> None:
        """Test default token values and API configuration are properly set.

        Validates that default values including tokens, token expiration, and API organization
        are correctly initialized and accessible through the TcEx inputs model. Tests token
        validation and default API organization configuration.

        Playbook Data Type: Token and API configuration validation
        Validation: Token presence, token expiration, default API organization

        Args:
            tcex: TcEx instance fixture for testing token configuration

        Fixtures:
            tcex: Provides TcEx instance for testing input configuration
        """
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
#         tcex.args
#         tcex.rargs
#
#         assert tcex.args.my_bool is True
#         assert tcex.rargs.my_bool is True
#         assert tcex.args.my_multi == ['one', 'two']
#         assert tcex.rargs.my_multi == ['one', 'two']
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
