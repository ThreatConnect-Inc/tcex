"""Test the TcEx Inputs Config Module."""
# standard library
import json
from random import randint


class TestPlaybookAot:
    """Test TcEx Playbook AOT Feature."""

    @staticmethod
    def test_aot_inputs(playbook_app, redis_client):
        """Test AOT input method of TcEx

        ..important:: This method duplicates some of the same coverage in inputs module testing.

        Args:
            playbook_app (callable, fixture): The tcex fixture defined in conftest.py.
            redis_client (Redis.client, fixture): The redis_client fixture defined in conftest.py.
        """
        # add AOT setting to App
        config_data = {
            'tc_action_channel': f'pytest-action-channel-{randint(1000,9999)}',
            'tc_aot_enabled': True,
            'tc_exit_channel': f'pytest-exit-channel-{randint(1000,9999)}',
            'tc_terminate_seconds': 60,
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

        tcex.aot_rpush(0)

    @staticmethod
    def test_aot_terminate(playbook_app, redis_client):
        """Test AOT handling terminate command

        Args:
            playbook_app (callable, fixture): The tcex fixture defined in conftest.py.
            redis_client (Redis.client, fixture): The redis_client fixture defined in conftest.py.
        """
        # add AOT setting to App
        config_data = {
            'tc_action_channel': f'pytest-action-channel-{randint(1000,9999)}',
            'tc_aot_enabled': True,
            'tc_exit_channel': f'pytest-exit-channel-{randint(1000,9999)}',
            'tc_terminate_seconds': 60,
        }
        app = playbook_app(config_data=config_data)

        # send redis rpush AOT message
        aot_msg = {'type': 'terminate'}
        redis_client.rpush(config_data.get('tc_action_channel'), json.dumps(aot_msg))

        # get a configured instance of tcex, missing AOT values
        # tcex will block, check for the AOT method, parse new config, and then run
        try:
            app.tcex  # pylint: disable=pointless-statement
            # the app will immediately exit since terminate command was already sent
            assert False
        except SystemExit:
            assert True

    @staticmethod
    def test_aot_timeout(playbook_app):
        """Test AOT timeout waiting on push.

        Args:
            playbook_app (callable, fixture): The tcex fixture defined in conftest.py.
        """
        # add AOT setting to App
        config_data = {
            'tc_action_channel': f'pytest-action-channel-{randint(1000,9999)}',
            'tc_aot_enabled': True,
            'tc_exit_channel': f'pytest-exit-channel-{randint(1000,9999)}',
            'tc_terminate_seconds': 1,
        }
        app = playbook_app(config_data=config_data)

        try:
            app.tcex  # pylint: disable=pointless-statement
            # the app will timeout and exit
            assert False
        except SystemExit:
            assert True
