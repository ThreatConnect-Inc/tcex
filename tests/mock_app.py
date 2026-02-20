"""TcEx Framework Module"""

# standard library
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any

# third-party
from requests import Session

# first-party
from tcex.app.config.install_json import InstallJson
from tcex.input.field_type.sensitive import Sensitive
from tcex.registry import registry
from tcex.requests_tc.auth.hmac_auth import HmacAuth
from tcex.tcex import TcEx
from tcex.util.util import Util


class MockApp:
    """MockApp Class for testing TcEx Framework.

    Typical usage when using conftest.py fixture:

    # basic option
    tcex = service_app().tcex

    # with runtime level option
    tcex = service_app(runtime_level='WebhookTriggerService').tcex
    """

    def __init__(self, runtime_level: str, **kwargs):
        """Initialize instance properties."""
        self.runtime_level = runtime_level
        self.cd: dict = kwargs.get('config_data', {})  # configuration data for tcex instance
        self.ijd: dict = kwargs.get('ij_data', {})  # install.json data

        # properties
        self.tc_api_path = os.getenv('TC_API_PATH')
        self.tc_token_url = os.getenv('TC_TOKEN_URL')
        self.tc_token_svc_id = os.getenv('TC_TOKEN_SVC_ID')
        self.util = Util()
        self._tcex = None

        # External Apps don't require an install.json file
        if self.runtime_level.lower() != 'external':
            # create install.json file
            self.mock_install_json()
        InstallJson._instances = {}  # type: ignore
        self.ij = InstallJson()

    @property
    def _config_api(self) -> dict[str, bool | str | None]:
        return {
            'tc_token': self.api_token,
            'tc_token_expires': '1700000000',
            # hmac auth (for session tests)
            'tc_api_access_id': self.getenv('tc_api_access_id'),
            'tc_api_secret_key': self.getenv('tc_api_secret_key'),
        }

    @property
    def _config_common(self) -> dict[str, bool | str | None]:
        """Return config data for mocked App."""
        return {
            # default
            'api_default_org': self.getenv('api_default_org'),
            'tc_owner': self.getenv('tc_owner', 'TCI'),
            # logging
            'tc_log_level': self.getenv('tc_log_level', 'trace'),
            'tc_log_to_api': self.getenv('tc_log_to_api', 'false', True),
            # paths
            'tc_api_path': self.getenv('tc_api_path'),
            'tc_in_path': self.getenv('tc_in_path', ''),
            'tc_log_path': self.getenv('tc_log_path', ''),
            'tc_out_path': self.getenv('tc_out_api', ''),
            'tc_temp_path': self.getenv('tc_temp_path', str(Path(__file__).parent)),
            # proxy
            'tc_proxy_tc': self.getenv('tc_proxy_tc', 'false', True),
            'tc_proxy_external': self.getenv('tc_proxy_external', 'false', True),
        }

    @property
    def _config_playbook(self) -> dict[str, bool | int | str]:
        """Return config data for mocked App."""
        return {
            'tc_exit_channel': 'exit-channel',
            'tc_terminate_seconds': 30,
        }

    @property
    def _config_playbook_common(self) -> dict[str, Any]:
        """Return config data for mocked App."""
        return {
            'tc_playbook_kvstore_context': self.getenv(
                'tc_playbook_kvstore_context', str(uuid.uuid4())
            ),
            'tc_kvstore_host': self.getenv('tc_kvstore_host', 'localhost'),
            'tc_kvstore_port': int(self.getenv('tc_kvstore_port') or '6379'),
            'tc_kvstore_type': self.getenv('tc_kvstore_type', 'Redis'),
            'tc_playbook_kvstore_id': int(self.getenv('tc_playbook_kvstore_id') or '0'),
        }

    @property
    def _config_proxy(self) -> dict[str, str]:
        """Return config data for mocked App."""
        config = {}
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
    def _config_service(self) -> dict[str, bool | str]:
        """Return config data for mocked App."""
        return {
            'tc_svc_client_topic': self.getenv('tc_svc_client_topic')
            or 'svc-client-cc66d36344787779ccaa8dbb5e09a7ab'
        }

    @property
    def _ij_common(self) -> dict[str, Any]:
        """Return install.json data for mocked App."""
        return {
            'allowOnDemand': True,
            'commitHash': 'abc-123',
            'displayName': self.ijd.get('display_name') or 'Pytest',
            'features': self.ijd.get('features', [])
            or [
                'appBuilderCompliant',
                'layoutEnabledApp',
                'fileParams',
                'secureParams',
            ],
            'languageVersion': '3.11',
            'listDelimiter': '|',
            'note': 'TcEx Testing',
            'programLanguage': 'PYTHON',
            'programMain': 'run',
            'programVersion': '1.0.0',
            'runtimeLevel': self.runtime_level,
        }

    @property
    def _ij_playbook_common(self) -> dict[str, Any]:
        """Return install.json data for mocked App."""
        return {
            'params': self.ijd.get('params')
            or [
                {
                    'label': 'My Bool',
                    'name': 'my_bool',
                    'note': '',
                    'required': True,
                    'sequence': 1,
                    'type': 'Boolean',
                },
                {
                    'label': 'My Choice',
                    'name': 'my_choice',
                    'note': '',
                    'required': True,
                    'sequence': 2,
                    'type': 'Choice',
                    'validValues': [
                        '-- Select --',
                        'choice_1',
                        'choice_2',
                        'choice_3',
                        '${ATTRIBUTES}',
                        '${ARTIFACT_TYPES}',
                        '${GROUP_TYPES}',
                        '${INDICATOR_TYPES}',
                        '${OWNERS}',
                        '${USERS}',
                        '${USER_GROUPS}',
                    ],
                },
                {
                    'label': 'My Choice',
                    'name': 'my_choice_optional',
                    'note': '',
                    'required': False,
                    'sequence': 2,
                    'type': 'Choice',
                    'validValues': ['-- Select --', 'choice_1', 'choice_2', 'choice_3'],
                },
                {
                    'label': 'My Multi',
                    'name': 'my_multi',
                    'note': '',
                    'required': False,
                    'sequence': 3,
                    'type': 'MultiChoice',
                    'validValues': ['one', 'two'],
                },
                {
                    'label': 'Colors',
                    'name': 'colors',
                    'note': '',
                    'required': False,
                    'sequence': 4,
                    'type': 'String',
                },
                {
                    'label': 'Color',
                    'name': 'color',
                    'note': '',
                    'required': False,
                    'sequence': 5,
                    'type': 'String',
                },
                {
                    'label': 'Fruit',
                    'name': 'fruit',
                    'note': '',
                    'required': False,
                    'sequence': 6,
                    'type': 'String',
                },
            ],
            'playbook': self.ijd.get('playbook')
            or {
                'outputPrefix': 'pytest',
                'outputVariables': [],
                'type': 'TcEx Test',
            },
        }

    def _write_file_params_encrypted_file(self, config: dict):
        """Write the App encrypted fileParams file."""
        config_data = json.dumps(config).encode()
        config_key = self.util.random_string(16)
        config_file = 'app_params.aes'

        # encrypt the serialized config data
        encrypted_contents = self.util.encrypt_aes_cbc(config_key, config_data)

        # write the config data to disk
        with open(config_file, 'wb') as fh:
            fh.write(encrypted_contents)

        # set the environment variables for tcex input module.
        os.environ['TC_APP_PARAM_FILE'] = config_file
        os.environ['TC_APP_PARAM_KEY'] = config_key

    @staticmethod
    def _write_install_json(data: dict):
        """Write the App install.json file."""
        with open('install.json', 'w') as fh:
            json.dump(data, fh, indent=2, sort_keys=True)

    @property
    def api_token(self) -> str:
        """Return a valid API token."""
        r = self.session.post(f'{self.tc_api_path}{self.tc_token_url}api', verify=False)
        if r.status_code != 200:
            raise RuntimeError(
                f'This feature requires ThreatConnect 6.0 or higher. response={r.text}, '
                f'url={r.request.url}, status_code={r.status_code}'
            )
        # cannot return Sensitive here because it is used in a dict
        return r.json()['data']

    @property
    def config_data(self) -> dict:
        """Return the complete input config for Mock App."""
        # add common config items
        _config = self._config_common

        # add proxy config
        _config.update(self._config_proxy)

        # create log structure for feature/test (e.g., args/test_args.log)
        _config['tc_log_file'] = 'test.log'

        # add api inputs
        _config.update(self._config_api)

        if self.runtime_level.lower() == 'playbook':
            _config.update(self._config_playbook)  # type: ignore

        # add playbook and service configs
        if self.runtime_level.lower() in [
            'apiservice',
            'playbook',
            'triggerservice',
            'webhooktriggerservice',
        ]:
            _config.update(self._config_playbook_common)  # type: ignore

        # add service configs
        if self.runtime_level.lower() in [
            'apiservice',
            'triggerservice',
            'webhooktriggerservice',
        ]:
            _config.update(self._config_service)

        # anything remaining in self.cd would be an arg to add.
        for k, v in self.cd.items():
            _config[k] = v

        # only support one auth mechanism
        if _config.get('tc_token'):
            del _config['tc_api_access_id']
            del _config['tc_api_secret_key']

        return _config

    def getenv(
        self, key: str, default: str | None = None, boolean: bool = False
    ) -> bool | str | None:
        """Get the appropriate **config value**.

        Use config_data value provided to Class,
        else use environment variable data,
        else use default value
        """
        cv = os.getenv(key.upper(), default)
        if hasattr(self.cd, key):
            # check if it exist so None can be set
            cv = self.cd.pop(key)

        if boolean:
            # convert string response to boolean
            cv = str(cv).lower() in ['true']
        return cv

    def mock_file_params(self):
        """Return the configuration data for that App or write to app_param."""
        # create encrypted file (fileParam feature)
        self._write_file_params_encrypted_file(self.config_data)

    def mock_install_json(self):
        """Return install.json data for mocked App."""
        _install_json = self._ij_common

        # add playbook and service configs
        if self.runtime_level.lower() in [
            'apiservice',
            'playbook',
            'triggerservice',
            'webhooktriggerservice',
        ]:
            _install_json.update(self._ij_playbook_common)

        # create install.json file
        self._write_install_json(_install_json)

    @property
    def service_token(self) -> str:
        """Get a valid TC service token.

        TC_TOKEN_SVC_ID is the ID field from the app catalog item table for a service App.
        TC_TOKEN_URL is the API endpoint to get a TOKEN.
        """
        data = {'serviceId': os.getenv('TC_TOKEN_SVC_ID')}
        r = self.session.post(f'{self.tc_api_path}{self.tc_token_url}svc', json=data, verify=False)
        if r.status_code != 200:
            raise RuntimeError(f'This feature requires ThreatConnect 6.0 or higher ({r.text})')
        # cannot return Sensitive here because it is used in a dict
        return r.json()['data']

    @property
    def session(self) -> Session:
        """Return Session configured for TC API."""
        _session = Session()
        tc_api_access_id = os.getenv('TC_API_ACCESS_ID')
        tc_api_secret_key = os.getenv('TC_API_SECRET_KEY')
        if tc_api_access_id is None or tc_api_secret_key is None:
            print('Environment Variable TC_API_ACCESS_ID and TC_API_SECRET_KEY must be set.')
            sys.exit(1)

        _session.auth = HmacAuth(tc_api_access_id, Sensitive(tc_api_secret_key))
        return _session

    @property
    def tcex(self) -> TcEx:
        """Return an instance of tcex."""
        # write file params and initialize new tcex instance
        if self._tcex is not None:
            return self._tcex

        self.mock_file_params()
        registry._reset()
        self._tcex = TcEx()

        # cleanup environment variables
        if os.getenv('TC_APP_PARAM_FILE', None):
            del os.environ['TC_APP_PARAM_FILE']
        if os.getenv('TC_APP_PARAM_KEY', None):
            del os.environ['TC_APP_PARAM_KEY']

        return self._tcex
