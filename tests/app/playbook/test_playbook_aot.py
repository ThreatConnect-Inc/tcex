"""TcEx Framework Module"""

# third-party
from pydantic import BaseModel

# first-party
from tcex.input.field_type import String

# from collections.abc import Callable
# from _pytest.monkeypatch import MonkeyPatch
# from redis import Redis


class InputModel(BaseModel):
    """."""

    my_bool: bool
    my_multi: list[String]


class TestPlaybookAot:
    """Test TcEx Playbook AOT Feature."""

    # @staticmethod
    # def test_aot_inputs(playbook_app: Callable[..., MockApp], redis_client: Redis):
    #     """Test AOT input method of TcEx

    #     ..important:: This method duplicates some of the same coverage in inputs module testing.
    #     """
    #     # add AOT setting to App
    #     config_data = {
    #         'tc_action_channel': f'pytest-action-channel-{randint(1000,9999)}',
    #         'tc_aot_enabled': True,
    #         'tc_exit_channel': f'pytest-exit-channel-{randint(1000,9999)}',
    #         'tc_terminate_seconds': 60,
    #     }
    #     app = playbook_app(config_data=config_data)

    #     # send redis rpush AOT message
    #     aot_config_data = {'my_bool': 'true', 'my_multi': 'one|two'}
    #     aot_config_data.update(app.config_data)
    #     aot_msg = {'type': 'execute', 'params': aot_config_data}
    #     redis_client.rpush(config_data.get('tc_action_channel'), json.dumps(aot_msg))

    #     # get a configured instance of tcex, missing AOT values
    #     # tcex will block, check for the AOT method, parse new config, and then run
    #     tcex = app.tcex
    #     tcex.inputs.add_model(TestInputModel)

    #     assert tcex.inputs.model.my_bool is True
    #     assert tcex.inputs.model.my_multi == ['one', 'two']

    #     tcex.exit_service._aot_rpush(0)

    # @staticmethod
    # def test_aot_terminate(playbook_app: Callable[..., MockApp], redis_client: Redis):
    #     """Test AOT handling terminate command"""
    #     # add AOT setting to App
    #     config_data = {
    #         'tc_action_channel': f'pytest-action-channel-{randint(1000,9999)}',
    #         'tc_aot_enabled': True,
    #         'tc_exit_channel': f'pytest-exit-channel-{randint(1000,9999)}',
    #         'tc_terminate_seconds': 60,
    #     }
    #     app = playbook_app(config_data=config_data)

    #     # send redis rpush AOT message
    #     aot_msg = {'type': 'terminate'}
    #     redis_client.rpush(config_data.get('tc_action_channel'), json.dumps(aot_msg))

    #     # get a configured instance of tcex, missing AOT values
    #     # tcex will block, check for the AOT method, parse new config, and then run
    #     try:
    #         app.tcex  # pylint: disable=pointless-statement
    #         # the app will immediately exit since terminate command was already sent
    #         assert False
    #     except SystemExit:
    #         assert True

    # @staticmethod
    # def test_aot_timeout(playbook_app: Callable[..., MockApp]):
    #     """Test AOT timeout waiting on push."""
    #     # add AOT setting to App
    #     config_data = {
    #         'tc_action_channel': f'pytest-action-channel-{randint(1000,9999)}',
    #         'tc_aot_enabled': True,
    #         'tc_exit_channel': f'pytest-exit-channel-{randint(1000,9999)}',
    #         'tc_terminate_seconds': 1,
    #     }
    #     app = playbook_app(config_data=config_data)

    #     try:
    #         app.tcex.inputs.model  # pylint: disable=pointless-statement
    #         # the app will timeout and exit
    #         assert False
    #     except SystemExit:
    #         assert True
