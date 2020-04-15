# -*- coding: utf-8 -*-
"""TcEx Framework Env Store Module"""
import os
import sys

try:
    import hvac
except ImportError:
    # hvac on required for local dev/testing
    pass


class EnvStore:
    """TcEx Key Value API Module.

    Args:
        session (request.Session): A configured requests session for TC API (tcex.session).
    """

    def __init__(self):
        """Initialize the Class properties."""

        # properties
        self._vault_client = None
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
            env_variable (str): The env variable name or Vault path.
            env_type (str, optional): The type of environment variable to look up. Defaults
                to 'env'.
            default (str): The default value if no value is found.

        Returns:
            str|None: The value from OS env or Vault.
        """
        env_var_updated = self._convert_env(env_variable)
        value = default

        if env_type in ['env', 'envs', 'os'] and os.getenv(env_var_updated):
            # return value from OS environ
            value = os.getenv(env_var_updated, default)
        elif env_type in ['env', 'envs', 'vault'] and 'hvac' in sys.modules:
            # return value from Vault
            value = self.read_from_vault(env_variable, default)

        return value

    def read_from_vault(self, path, default=None):
        """Read data from Vault for the provided path.

        Args:
            path (string): The path to the vault data including the key
                (e.g. myData/mySecret/myKey).
            default (str): The default value if no value is found.

        Returns:
            str|None: The vault association with the provided path and key.
        """
        paths = path.lstrip('/').split('/')

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
            # TODO: log a warning
            pass
        except hvac.exceptions.VaultError:
            pass

        return data.get('data', {}).get('data', {}).get(key) or default

    @property
    def vault_client(self):
        """Return configured vault client."""
        if self._vault_client is None and 'hvac' in sys.modules:
            if self.vault_url is not None and self.vault_token is not None:
                self._vault_client = hvac.Client(url=self.vault_url, token=self.vault_token)
        return self._vault_client
