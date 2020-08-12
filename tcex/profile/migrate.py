# -*- coding: utf-8 -*-
"""TcEx testing profile Class."""
# standard library
import json
import re
import sys

# third-party
import colorama as c

# autoreset colorama
c.init(autoreset=True, strip=False)


class Migrate:
    """Class for profile Migration methods management."""

    def __init__(self, profile):
        """Initialize Class properties."""
        self.profile = profile

    @property
    def _reserved_args(self):
        """Return a list of *all* ThreatConnect reserved arg values."""
        return [
            'api_access_id',
            'api_default_org',
            'api_secret_key',
            'batch_action',
            'batch_chunk',
            'batch_halt_on_error',
            'batch_interval_max',
            'batch_poll_interval',
            'batch_write_type',
            'logging',
            'tc_api_path',
            'tc_in_path',
            'tc_log_file',
            'tc_log_level',
            'tc_log_path',
            'tc_log_to_api',
            'tc_out_path',
            'tc_playbook_db_context',
            'tc_playbook_db_path',
            'tc_playbook_db_port',
            'tc_playbook_db_type',
            'tc_playbook_out_variables',
            'tc_proxy_host',
            'tc_proxy_port',
            'tc_proxy_username',
            'tc_proxy_password',
            'tc_proxy_external',
            'tc_proxy_tc',
            'tc_secure_params',
            'tc_temp_path',
            'tc_token',
            'tc_token_expires',
            'tc_user_id',
        ]

    def add_staging_data(self, profile_data, name, type_, value):
        """Create staging data and return variable value.

        Args:
            profile_data (dict): The profile to update with new staging data.
            name (str): The name of the input.
            type_ (str): The type of input (Binary, StringArray, etc.)
            value (str): The value to write in the staging data.

        Returns:
            [type]: [description]
        """
        variable = self.profile.ij.create_variable(name, type_)
        profile_data['stage']['kvstore'][variable] = value
        return variable

    @staticmethod
    def comment_to_comments(profile_data):
        """Migrate comment key to comments key.

        Args:
            profile_data (dict): The profile data dict.
        """
        # APP-80 - migrate comment/comments field
        comment = profile_data.pop('comment', None)
        if isinstance(comment, str):
            profile_data['_comments_'] = [comment]
        elif isinstance(comment, list):
            profile_data['_comments_'] = comment

        comments = profile_data.pop('comments', None)
        if isinstance(comments, str):
            profile_data['_comments_'] = [comments]
        elif isinstance(comments, list):
            profile_data['_comments_'] = comments

    @property
    def data(self):
        """Migrate profile to latest schema and rewrite data.

        Called from test_case.py init_profile so that profile is update before
        the test case runs.
        """
        profile_data = self.profile.contents

        # migrate comment to comments and make an array
        self.comment_to_comments(profile_data)

        # remove any deprecated fields
        self.deprecated_fields(profile_data)

        # move default inputs
        self.move_default_inputs(profile_data)

        # update all env variables to match latest pattern
        self.permutation_output_variables(profile_data)

        # update config section of profile for service Apps
        self.service_config_inputs(profile_data)

        # create staged section if not already present
        self.create_staged_section(profile_data)

        # stage String inputs if they are not already staged
        self.stage_inputs(profile_data)

        # change for threatconnect staged data
        self.stage_redis_name(profile_data)

        # change for threatconnect staged data
        self.stage_threatconnect_data(profile_data)

        # update all version 1 env variables to match latest pattern
        profile_data = self.variable_pattern_env_v1(profile_data)

        # update all version 2 env variables to match latest pattern
        profile_data = self.variable_pattern_env_v2(profile_data)

        # update all tcenv variables to match latest pattern
        profile_data = self.variable_pattern_tcenv(profile_data)

        self.profile.write(profile_data)

    @staticmethod
    def deprecated_fields(profile_data):
        """Remove deprecated fields."""
        deprecated_fields = ['version']
        for d in deprecated_fields:
            try:
                del profile_data[d]
            except KeyError:
                pass

        # remove autostage
        deprecated_option_fields = ['autostage']
        for d in deprecated_option_fields:
            try:
                del profile_data['options'][d]
            except KeyError:
                pass

    def move_default_inputs(self, profile_data):
        """Move any default args from optional or required inputs to defaults section."""
        updated_params = []  # collect all PB configs for service Apps
        for profile_inputs in self.profile.profile_inputs:
            # ADI-1376 - handle tcex default args
            for input_type, inputs in dict(profile_inputs).items():
                for name in dict(inputs):
                    if name in self._reserved_args:
                        # preserve overwritten default arg
                        profile_inputs.setdefault('defaults', {})
                        profile_inputs['defaults'][name] = profile_inputs[input_type].pop(name)

            # updated params are for service Apps
            updated_params.append(profile_inputs)

        # use updated params from the validation section above to merge inputs
        if self.profile.ij.runtime_level.lower() in ['triggerservice', 'webhooktriggerservice']:
            for index, config_item in enumerate(profile_data.get('configs', [])):
                config_item['config'] = updated_params[index]
        else:
            # non-service App (PB Apps) will only have one set of inputs
            profile_data['inputs'] = updated_params[0]

    @staticmethod
    def permutation_output_variables(profile_data):
        """Remove permutation_output_variables field.

        Args:
            profile_data (dict): The profile data dict.
        """
        try:
            del profile_data['permutation_output_variables']
        except KeyError:
            pass

    def service_config_inputs(self, profile_data):
        """Change flat config inputs to include required/options.

        Args:
            profile_data (dict): The profile data dict.
        """
        for configs in profile_data.get('configs', []):
            config = configs.get('config', {})

            # handle updated configs
            if config.get('optional') or config.get('required'):
                continue

            # new config schema
            config_inputs = {'optional': {}, 'required': {}}

            # iterate over defined inputs
            for k, v in config.items():
                input_data = self.profile.ij.params_dict.get(k)
                if input_data is not None:
                    input_type = 'optional'
                    if input_data.get('required') is True:
                        input_type = 'required'

                # add value back with appropriate input type
                config_inputs[input_type][k] = v

            # overwrite flattened config
            configs['config'] = config_inputs

    @staticmethod
    def create_staged_section(profile_data):
        """Create the Stage and kvstore section in the profile if not currently present"""
        if 'stage' not in profile_data.keys():
            profile_data['stage'] = {'kvstore': {}}
        if 'kvstore' not in profile_data.get('stage').keys():
            profile_data['stage']['kvstore'] = []

    def stage_inputs(self, profile_data):
        """Stage any non-staged profile data."""
        if self.profile.ij.runtime_level.lower() != 'playbook':
            # staging is only required for PB Apps
            return

        for input_type in ['optional', 'required']:
            for k, v in dict(profile_data.get('inputs', {}).get(input_type, {})).items():
                # check that value requires staging
                if v is None:
                    continue

                # get ij data for k
                ij_data = self.profile.ij.params_dict.get(k)

                # input is not define in install.json, possibly default arg
                if ij_data is None:
                    continue

                # check input type to see if it support staging data
                if ij_data.get('type').lower() in [
                    'boolean',
                    'choice',
                    'multichoice',
                ]:
                    continue

                # check value to see if there are any variables in the data
                if re.search(self.profile.utils.variable_parse, v):
                    continue

                # get PB data type, APP-607
                data_types = ij_data.get('playbookDataType', [])

                # only stage String values
                if 'String' not in data_types and not isinstance(v, str):
                    continue

                # convert input value to staged data
                v = self.add_staging_data(profile_data, k, 'String', v)

                # update input with new variable
                profile_data['inputs'][input_type][k] = v

    @staticmethod
    def stage_redis_name(profile_data):
        """Update stage.redis to stage.kvstore

        This change updates the previous value of redis with a
        more generic value of kvstore for staged data.

        Args:
            profile_data (dict): The current profile data dict.

        Returns:
            dict: The update profile dict.
        """
        if profile_data.get('stage') is None:
            return profile_data

        kvstore_data = profile_data['stage'].get('redis', None)
        if kvstore_data is not None:
            del profile_data['stage']['redis']
            profile_data['stage']['kvstore'] = kvstore_data

        return None

    @staticmethod
    def stage_threatconnect_data(profile_data):
        """Update for staged threatconnect data section of profile

        This change updates the previous list to a dict with a key that
        can be reference as a variable in other sections of the profile.

        Args:
            profile_data (dict): The current profile data dict.

        Returns:
            dict: The update profile dict.
        """
        if 'stage' not in profile_data:
            return profile_data

        stage_tc = profile_data.get('stage').get('threatconnect')

        # check if profile is using old list type
        if isinstance(stage_tc, list):
            profile_data['stage']['threatconnect'] = {}

            counter = 0
            for item in stage_tc:
                profile_data['stage']['threatconnect'][f'item_{counter}'] = item
                counter += 1

        return None

    @staticmethod
    def variable_pattern_env_v1(profile_data):
        """Update the profile variable to latest pattern

        Args:
            profile_data (dict): The profile data dict.

        Returns:
            dict: The updated dict.
        """
        profile = json.dumps(profile_data)

        for m in re.finditer(r'\"\$(env|envs)\.(\w+)\"', profile):
            try:
                full_match = m.group(0)
                env_type = m.group(1)
                env_key = m.group(2)

                new_variable = f'"${{{env_type}:{env_key}}}"'
                profile = profile.replace(full_match, new_variable)
            except IndexError:
                print(f'{c.Fore.YELLOW}Invalid variable found {full_match}.')
        return json.loads(profile)

    @staticmethod
    def variable_pattern_env_v2(profile_data):
        """Update the profile variable to latest pattern

        Args:
            profile_data (dict): The profile data dict.

        Returns:
            dict: The updated dict.
        """
        profile = json.dumps(profile_data)

        for m in re.finditer(r'\${(env|envs|local|remote)\.(.*?)}', profile):
            try:
                full_match = m.group(0)
                env_type = m.group(1)  # currently env, envs, local, remote
                env_key = m.group(2)

                new_variable = f'${{{env_type}:{env_key}}}'
                profile = profile.replace(full_match, new_variable)
            except IndexError:
                print(f'{c.Fore.YELLOW}Invalid variable found {full_match}.')
        return json.loads(profile)

    def variable_pattern_tcenv(self, profile_data):
        """Update the profile variable to latest pattern

        Args:
            profile_data (dict): The profile data dict.

        Returns:
            dict: The updated dict.
        """
        if 'jmespath' not in sys.modules:
            print(
                f'{c.Fore.RED}Missing jmespath module. Try '
                f'installing "pip install tcex[development]"'
            )
            sys.exit(1)

        profile = json.dumps(profile_data)

        for data in self.profile.tc_staged_data:
            key = data.get('key')
            for m in re.finditer(r'\${tcenv\.' + str(key) + r'\.(.*?)}', profile):
                try:
                    full_match = m.group(0)
                    jmespath_expression = m.group(1)

                    new_variable = f'${{tcenv:{key}:{jmespath_expression}}}'
                    profile = profile.replace(full_match, new_variable)
                except IndexError:
                    print(f'{c.Fore.YELLOW}Invalid variable found {full_match}.')
        return json.loads(profile)
