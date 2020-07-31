# -*- coding: utf-8 -*-
"""Test the TcEx Utils Module."""
# standard library
import json
import os
from random import randint
from uuid import uuid4

# first-party
from tcex.profile import Profile


# pylint: disable=no-self-use
class TestProfileAdd:
    """Test the TcEx Utils Module."""

    profile_dir = os.path.join(os.getcwd(), 'tests', 'PyTest', 'profiles.d')

    @property
    def default_args(self):
        """Return default args dict."""
        return {}

    def load_profile(self, filename):
        """Load profile from disk

        Args:
            filename (str): The filename to load.
        """
        profile_filename = os.path.join(self.profile_dir, filename)
        with open(profile_filename, 'r') as fh:
            return json.load(fh)

    @property
    def profile_data(self):
        """Return example profile data."""
        return {
            'exit_codes': [0],
            'exit_message': {'expected_output': 'Successfully read keys.\n', 'op': 'eq'},
            'inputs': {
                'optional': {'boolean': None, 'tc_proxy_host': 'localhost', 'vault_mount': 'ninja'},
                'required': {
                    'hidden': 'test',
                    'path': 'int/pytest/app/read_1',
                    'read_keys': '#App:1234:read_keys!KeyValueArray',
                    'tc_action': 'Read Keys',
                    'vault_token': '$env.PYTEST_PWD',
                    'vault_url': 'https://vault-01.tci.ninja:8200',
                },
            },
            'options': {'session': {'blur': [], 'enabled': False}},
            'outputs': {
                '#App:9876:one!String': {'expected_output': '1', 'op': 'eq'},
                '#App:9876:three!String': {'expected_output': None, 'op': 'eq'},
                '#App:9876:two!String': {'expected_output': '2', 'op': 'eq'},
            },
            'stage': {
                'redis': {
                    '#App:1234:read_keys!KeyValueArray': [
                        {'key': 'one', 'value': 'one'},
                        {'key': 'two', 'value': 'two'},
                        {'key': 'three', 'value': 'three'},
                    ]
                }
            },
        }

    def test_profile_add(self, tcex):  # pylint: disable=unused-argument
        """Test adding a profile.

        {
          "exit_codes": [
            0
          ],
          "exit_message": null,
          "inputs": {
            "optional": {
              "my_multi": [
                "one",
                "two"
              ]
            },
            "required": {
              "my_bool": false
            }
          },
          "options": {
            "autostage": {
              "enabled": false,
              "only_inputs": null
            },
            "session": {
              "blur": [],
              "enabled": false
            }
          },
          "outputs": null,
          "stage": {
            "kvstore": {}
          }
        }

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        default_args = {}
        feature = 'PyTest'
        name = f'pytest-{randint(1000, 9999)}'

        # initialize profile
        profile = Profile(default_args=default_args, feature=feature, name=name)

        # add profile
        profile.add()  # required tcex fixture for install.json to be created

        # load profile from disk
        profile_data = self.load_profile(f'{name}.json')

        # assert JSON file matches expected values
        assert profile_data.get('exit_codes') == [0]
        assert profile_data.get('exit_message') is None
        # inputs must match those defined in mock_app.py
        for k, _ in profile_data.get('inputs', {}).get('optional', {}).items():
            if k == 'my_multi':
                break
        else:
            assert False, 'Key my_multi not found in inputs, did someone change inputs in mock App?'
        for k, _ in profile_data.get('inputs', {}).get('required', {}).items():
            if k == 'my_bool':
                break
        else:
            assert False, 'Key my_bool not found in inputs, did someone change inputs in mock App?'
        assert profile_data.get('outputs') is None

        # cleanup
        os.remove(profile.filename)

    def test_profile_context(self, tcex):
        """Test profile contexts

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        default_args = {}
        feature = 'PyTest'
        name = f'pytest-{randint(1000, 9999)}'

        # initialize profile
        profile = Profile(
            default_args=default_args, feature=feature, name=name, redis_client=tcex.redis_client
        )

        # add profile
        profile.add()

        # test context
        context = str(uuid4())
        profile.add_context(context)

        # assert context
        assert profile.context_tracker == [context]

        # clear context
        profile.clear_context(context)
        profile._context_tracker = []

        # assert context
        assert profile.context_tracker == []

        # cleanup
        os.remove(profile.filename)

    def test_migrate_profile(self, tcex):
        """Test migrating profile."""
        os.environ['PYTEST_PWD'] = f'PYTEST_PWD_{randint(1000, 9999)}'
        profile_name = f'pytest-{randint(1000, 9999)}'

        # write temp test profile
        profile_filename = os.path.join(self.profile_dir, f'{profile_name}.json')
        with open(profile_filename, 'w') as fh:
            json.dump(self.profile_data, fh, indent=2)

        context = str(uuid4())
        profile = Profile(
            default_args=self.default_args.copy(),
            feature='PyTest',
            name=profile_name,
            redis_client=tcex.redis_client,
            tcex_testing_context=context,
        )

        # migrate profile to latest schema
        profile.migrate()

        # load profile
        profile_data = self.load_profile(f'{profile_name}.json')

        # validate redis was renamed to kvstore
        assert profile_data.get('stage', {}).get('redis') is None
        assert profile_data.get('stage', {}).get('kvstore') is not None
        # validate default input moved to default
        assert (
            profile_data.get('inputs', {}).get('defaults', {}).get('tc_proxy_host') == 'localhost'
        )
        # validate variable schema has been migrated
        assert (
            profile_data.get('inputs', {}).get('required', {}).get('vault_token')
            == '${env:PYTEST_PWD}'
        )

    # def test_populate_profile(self, tcex):
    #     """Test migrating profile."""

    #     # populate profile (env vars, etc)
    #     profile.populate()

    #     # validate required fields
    #     valid, message = profile.validate_required_inputs()

    #     # replace all variable references
    #     profile_data = profile.replace_env_variables(self._profile.data)

    #     # stage ThreatConnect data based on current profile, also used in teardown method
    #     self._staged_tc_data = self.stager.threatconnect.entities(
    #         self._profile.stage_threatconnect, self._profile.owner
    #     )

    #     # insert staged data for replacement
    #     self._profile.tc_staged_data = self._staged_tc_data

    #     # Replace staged_data
    #     profile_data = self._profile.replace_tc_variables(profile_data)
    #     self._profile.data = profile_data

    #     # replace all references and all staged variable
    #     self._profile.init()

    #     # stage kvstore data based on current profile
    #     self.stager.redis.from_dict(self._profile.stage_kvstore)
