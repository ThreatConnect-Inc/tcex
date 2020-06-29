# -*- coding: utf-8 -*-
"""TcEx testing profile Class."""
import json

# import os
import re
import sys

import colorama as c

# from ..__metadata__ import __version__ as tcex_version

# autoreset colorama
c.init(autoreset=True, strip=False)


class Migrate:
    """Class for profile Migration methods management."""

    def __init__(self, profile):
        """Initialize Class properties."""
        self.profile = profile

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
        # Short circuit migrations if the profile is newer than this code
        # Ideally, we'd put a migration stamp in the profile instead
        # migration_mtime = os.stat(__file__).st_mtime
        # migration_target = f'{tcex_version}.{migration_mtime}'

        profile_data = self.profile.contents

        # profile_version = profile_data.get('version', None)
        # if not profile_version or profile_version < migration_target:
        #     profile_data['version'] = migration_target
        # else:
        #     return profile_data  # profile is already migrated

        # migrate comment to comments and make an array
        self.comment_to_comments(profile_data)

        # update all env variables to match latest pattern
        self.permutation_output_variables(profile_data)

        # update config section of profile for service Apps
        self.service_config_inputs(profile_data)

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
    def stage_redis_name(profile_data):
        """Update staged redis to kvstore

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
