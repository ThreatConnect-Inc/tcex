# -*- coding: utf-8 -*-
"""TcEx testing profile Class."""
# standard library
import json
import re
import sys

# third-party
import colorama as c
import jmespath

# autoreset colorama
c.init(autoreset=True, strip=False)


class Populate:
    """Populate profile env vars and other items."""

    def __init__(self, profile):
        """Initialize Class properties."""
        self.profile = profile

    def replace_env_variables(self, profile_data):
        """Replace any env vars.

        Environment variables replaced follow the pattern ${type:name[=default]}
        e.g. ${env:FOO} or ${env:FOO=bla} to have a default value of "bla" if FOO
        is unset.

        A warning is raised when a substitution is called for, but the source
        does not contain a matching key.  A default value of '' will be used
        when this happens.

        An error is raised if the substitution would result in a new key
        pattern being formed, i.e. if the substitution text contains '${',
        which may or may not be expanded, or break profile expansion.

        Args:
            profile_data (dict): The profile data dict.

        Returns:
            dict: The updated dict.
        """
        profile = json.dumps(profile_data)

        for m in re.finditer(r'\${(env|envs|local|remote):(.*?)}', profile):
            try:
                full_match = m.group(0)
                env_type = m.group(1)  # currently env, envs, local, or remote
                env_key = m.group(2)
                if '=' in env_key:
                    env_key, default_value = env_key.split('=', 1)
                else:
                    default_value = None

                env_value = self.profile.env_store.getenv(env_key, env_type, default_value)
                if env_value is not None:
                    if '${' in env_value:
                        self.profile.log.error(
                            f'Profile replacement value for {full_match} includes '
                            f'recursive expansion {env_value}'
                        )
                    profile = profile.replace(full_match, env_value)
            except IndexError:
                print(f'{c.Fore.YELLOW}Could not replace variable {full_match}).')
        return json.loads(profile)

    def replace_tc_variables(self, profile_data):
        """Replace all of the TC output variables in the profile with their correct value.

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
            data_value = data.get('data')

            for m in re.finditer(r'\${tcenv:' + str(key) + r':(.*?)}', profile):
                try:
                    full_match = m.group(0)
                    jmespath_expression = m.group(1)

                    if jmespath_expression:
                        value = jmespath.search(jmespath_expression, data_value)
                        profile = profile.replace(full_match, str(value))
                except IndexError:
                    print(f'{c.Fore.YELLOW}Invalid variable found {full_match}.')
        return json.loads(profile)
