# -*- coding: utf-8 -*-
"""TcEx Framework Env Store Module"""
# standard library
import logging
import os
import sys

try:
    # third-party
    import hvac
except ImportError:
    # hvac on required for local dev/testing
    pass


class EnvStore:
    """TcEx Key Value API Module.

    Args:
        logger (logging.Logger, optional): A instance of Logger. Defaults to None.
    """

    def __init__(self, logger=None):
        """Initialize the Class properties."""
        self.log = logger or logging.getLogger('layout_json')

        # properties
        self._vault_client = None
        self.cache = {}
        self.vault_token = os.getenv('VAULT_TOKEN')
        self.vault_url = os.getenv('VAULT_URL')

    @staticmethod
    def _convert_env(env_variable):
        """Convert an a vault path to env variable, removing first 2 parts of path

        Vault path need to be updated to be looked up as env variables.

        /ninja/int/cisco/umbrella/token -> CISCO_UMBRELLA_TOKEN

        """
        if '/' in env_variable:
            paths = env_variable.lstrip('/').split('/')
            # remove first to parts of path for env variable and leading '/'
            env_variable = '/'.join(paths[2:])
        return env_variable.replace('/', '_').replace(' ', '_').upper()

    def getenv(self, env_variable, env_type='env', default=None):
        """Return the value for the provide environment variable.

        Args:
            env_variable (str): The env variable name or env store path.
            env_type (str, optional): The type of environment variable to look up. Defaults
                to 'env'.
            default (str): The default value if no value is found.

        Returns:
            str|None: The value from OS env or env store.
        """
        cache_key = f'{env_type}-{env_variable}'
        cache_value = self.cache.get(cache_key)
        if cache_value is not None:
            return cache_value

        env_var_updated = self._convert_env(env_variable)
        value = default

        if env_type in ['env', 'envs', 'local'] and os.getenv(env_var_updated):
            # return value from OS environ
            value = os.getenv(env_var_updated, default)
        elif env_type in ['env', 'envs', 'remote'] and 'hvac' in sys.modules:
            # return value from Vault
            value = self.read_from_vault(env_variable, default)

        # provide an error so dev/qa engineer knows that
        # an env var they provide could not be found
        if value is None:
            raise RuntimeError(
                f'Could not resolve env variable {env_variable} ({env_var_updated}).'
            )

        self.cache[cache_key] = value
        return value

    def read_from_vault(self, full_path, default=None):
        """Read data from Vault for the provided path.

        Args:
            full_path (string): The path to the vault data including the key
                (e.g. myData/mySecret/myKey).
            default (str): The default value if no value is found.

        Returns:
            str|None: The vault association with the provided path and key.
        """
        paths = full_path.lstrip('/').split('/')

        # the key stored in data object at the provided path
        # (e.g., "/myData/myResource/token" -> "token")
        key = paths[-1].strip('/')

        # the path with the key and mount point removed
        # (e.g., "/myData/myResource/token/" -> "myResource")
        path = '/'.join(paths[1:-1])

        # the mount point from the path
        # (e.g., "/myData/myResource/token/" -> "myData")
        mount_point = paths[0]

        data = {}
        try:
            data = self.vault_client.secrets.kv.read_secret_version(
                path=path, mount_point=mount_point
            )
        except hvac.exceptions.InvalidPath:
            if hasattr(self.log, 'data'):
                self.log.data('setup', 'env store', f'Path not found: {path}')
        except hvac.exceptions.VaultError as e:
            if hasattr(self.log, 'data'):
                self.log.data('setup', 'env store', f'Error reading path: "{path}" ({e})', 'error')
        except Exception:
            self.log.data(
                'setup',
                'env store',
                'Generic failure. Please ensure Environment Store '
                'connectivity and env are configured properly.',
                'error',
            )

        if hasattr(self.log, 'data'):
            self.log.data('setup', 'vault read', full_path, 'trace')

        return data.get('data', {}).get('data', {}).get(key) or default

    @property
    def vault_client(self):
        """Return configured vault client."""
        if self._vault_client is None and 'hvac' in sys.modules:
            if self.vault_url is not None and self.vault_token is not None:
                self._vault_client = hvac.Client(url=self.vault_url, token=self.vault_token)
        return self._vault_client
