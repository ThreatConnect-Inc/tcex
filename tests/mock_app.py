# -*- coding: utf-8 -*-
"""Pytest MockApp class for testing TcEx Framework."""
import json
import os
import sys
from requests import Session

from tcex import TcEx
from tcex.sessions.tc_session import HmacAuth


class MockApp:
    """MockApp Class for testing TcEx Framework.

    Typical usage when using conftest.py fixture:

    # basic option
    tcex = service_app().tcex

    # with runlevel option
    tcex = service_app(runtime_level='WebhookTriggerService').tcex

    Args:
        runtime_level (str): The runtime level of the Mock App.
    """

    def __init__(self, runtime_level, config_data=None, ij_data=None):
        """Initialize Class properties."""
        self.cd = config_data or {}  # configuration data for tcex instance
        self.ijd = ij_data or {}  # install.json data
        self.runtime_level = runtime_level

        # properties
        api_access_id = os.getenv('API_ACCESS_ID')
        api_secret_key = os.getenv('API_SECRET_KEY')
        self.tc_api_path = os.getenv('TC_API_PATH')
        self.tc_token_url = os.getenv('TC_TOKEN_URL')
        self.tc_token_svc_id = os.getenv('TC_TOKEN_SVC_ID')

        # get a requests session and set hmac auth to use in retrieving tokens.
        self.session = Session()
        self.session.auth = HmacAuth(api_access_id, api_secret_key)

        # create install.json file
        self._create_install_json()

    def _create_install_json(self):
        """Create a mock install.json file."""
        with open('install.json', 'w') as fh:
            json.dump(self._mock_install_json, fh, indent=2)

    @property
    def _mock_install_json(self):
        """Return install.json data for mocked App."""
        display_name = self.ijd.get('display_name', 'Pytest')
        features = self.ijd.get('features') or [
            'aotExecutionEnabled',
            'appBuilderCompliant',
            'layoutEnabledApp',
            'secureParams',
        ]
        params = self.ijd.get('params') or [
            {
                'label': 'My Book',
                'name': 'my_bool',
                'note': '',
                'required': True,
                'sequence': 1,
                'type': 'Boolean',
            },
            {
                'label': 'My Multi',
                'name': 'my_multi',
                'note': '',
                'required': False,
                'sequence': 8,
                'type': 'MultiChoice',
                'validValues': ['one', 'two'],
            },
        ]
        playbook = self.ijd.get('playbook') or {'outputVariables': [], 'type': 'Utility'}

        ij = {
            'allowOnDemand': True,
            'commitHash': 'abc-123',
            'displayName': display_name,
            'features': features,
            'languageVersion': '3.6',
            'listDelimiter': '|',
            'note': '',
            'params': params,
            'programLanguage': 'PYTHON',
            'programMain': 'run',
            'programVersion': '1.0.0',
            'runtimeLevel': self.runtime_level,
        }
        if self.runtime_level.lower() != 'job':
            ij['playbook'] = playbook

        return ij

    @property
    def api_token(self):
        """Return a valid API token."""
        r = self.session.post(f'{self.tc_api_path}{self.tc_token_url}api', verify=False)
        if r.status_code != 200:
            raise RuntimeError(f'This feature requires ThreatConnect 6.0 or higher ({r.text})')
        return r.json().get('data')

    def getenv(self, key, default=None, boolean=False):
        """Get the appropriate **config value**.

        Use config_data value provided to Class,
        else use environment variable data,
        else use default value

        Args:
            key (str): The key value.
            default (str, optional): The default value to return if not found. Defaults to None.
            boolean (bool, optional): If true return the result as a bool. Defaults to False.

        Returns:
            bool|str: The value found in config date, env var, or default.
        """
        cv = self.cd.get(key) or os.getenv(key.upper(), default)
        if boolean:
            cv = str(cv.lower) in ['true']
        return cv

    @property
    def mock_config_data(self):
        """Return config data for mocked App."""
        config = {
            # default
            'api_default_org': self.getenv('api_default_org'),
            'tc_owner': self.getenv('tc_owner', 'TCI'),
            # logging
            'tc_log_level': self.getenv('tc_log_level', 'trace'),
            'tc_log_to_api': self.getenv('tc_log_to_api', 'false', True),
            # paths
            'tc_api_path': self.getenv('tc_api_path'),
            'tc_in_path': self.getenv('tc_in_path', 'log'),
            'tc_log_path': self.getenv('tc_log_path', 'log'),
            'tc_out_path': self.getenv('tc_out_api', 'log'),
            'tc_temp_path': self.getenv('tc_temp_path', 'log'),
            # proxy
            'tc_proxy_tc': self.getenv('tc_proxy_tc', 'false', True),
            'tc_proxy_external': self.getenv('tc_proxy_external', 'false', True),
        }

        # add specific config shared between job and playbook Apps
        if self.runtime_level.lower() in ['job', 'playbook']:
            # 'tc_token': self.service_token,
            config['tc_token'] = self.api_token
            config['tc_token_expires'] = '1700000000'
            # hmac auth (for session tests)
            config['api_access_id'] = self.getenv('api_access_id')
            config['api_secret_key'] = self.getenv('api_secret_key')

        # add specific config options for playbook and service Apps
        if self.runtime_level.lower() == [
            'apiservice',
            'playbook',
            'triggerservice',
            'webhooktriggerservice',
        ]:
            config['tc_playbook_db_type'] = self.getenv('tc_playbook_db_type', 'Redis')
            config['tc_playbook_db_context'] = self.getenv(
                'tc_playbook_db_context', '0d5a675a-1d60-4679-bd01-3948d6a0a8bd'
            )
            config['tc_playbook_db_path'] = self.getenv('tc_playbook_db_path', 'localhost')
            config['tc_playbook_db_port'] = self.getenv('tc_playbook_db_port', '6379')

        # add proxy config options if appropriate
        if self.getenv('tc_proxy_host'):
            config['tc_proxy_host'] = self.getenv('tc_proxy_host')
        if self.getenv('tc_proxy_port'):
            config['tc_proxy_port'] = self.getenv('tc_proxy_port')
        if self.getenv('tc_proxy_username'):
            config['tc_proxy_username'] = self.getenv('tc_proxy_username')
        if self.getenv('tc_proxy_password'):
            config['tc_proxy_password'] = self.getenv('tc_proxy_password')

        return config

    @property
    def service_token(self):
        """Get a valid TC service token.

        TC_TOKEN_SVC_ID is the ID field from the appcatalogitem table for a service App.
        TC_TOKEN_URL is the API endpoint to get a TOKEN.
        """
        data = {'serviceId': os.getenv('TC_TOKEN_SVC_ID')}
        r = self.session.post(f'{self.tc_api_path}{self.tc_token_url}svc', json=data, verify=False)
        if r.status_code != 200:
            raise RuntimeError(f'This feature requires ThreatConnect 6.0 or higher ({r.text})')
        return r.json().get('data')

    @property
    def tcex(self):
        """Return an instance of tcex."""

        # create log structure for feature/test (e.g., args/test_args.log)
        config_data = dict(self.mock_config_data)
        config_data['tc_log_file'] = self.tcex_log_file

        # clear sys.argv to avoid invalid arguments
        sys.argv = sys.argv[:1]
        return TcEx(config=config_data)

    @property
    def tcex_log_file(self):
        """Return log file name for current test case."""
        test_data = os.getenv('PYTEST_CURRENT_TEST').split(' ')[0].split('::')
        test_feature = test_data[0].split('/')[1].replace('/', '-')
        test_name = test_data[-1].replace('/', '-').replace('[', '-')
        return os.path.join(test_feature, f'{test_name}.log')
