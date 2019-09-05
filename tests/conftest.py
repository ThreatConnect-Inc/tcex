# -*- coding: utf-8 -*-
"""Base pytest configuration file."""
import json
import os
import shutil
import sys

import pytest
from tcex import TcEx
from .tc_token import TcToken


# instance of tc token to retrieve testing token from API
tc_token = TcToken()


# install.json data for testing
pytest_install_json = {
    'allowOnDemand': True,
    'commitHash': 'abc123',
    'displayName': 'Pytest',
    'features': ['aotExecutionEnabled', 'appBuilderCompliant', 'layoutEnabledApp', 'secureParams'],
    'languageVersion': '3.6',
    'listDelimiter': '|',
    'note': '',
    'params': [
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
    ],
    'playbook': {'outputVariables': [], 'type': 'Utility'},
    'programLanguage': 'PYTHON',
    'programMain': 'run',
    'programVersion': '1.0.0',
    'runtimeLevel': 'Playbook',
}


#
# Standard config for tcex instance
#

_config_data = {
    # connection
    'api_default_org': os.getenv('API_DEFAULT_ORG'),
    # 'tc_token': tc_token.service_token,
    'tc_token': tc_token.api_token,
    'tc_token_expires': '1700000000',
    'tc_owner': os.getenv('TC_OWNER', 'TCI'),
    # hmac auth (for session tests)
    'api_access_id': os.getenv('API_ACCESS_ID'),
    'api_secret_key': os.getenv('API_SECRET_KEY'),
    # logging
    'tc_log_level': os.getenv('TC_LOG_LEVEL', 'trace'),
    'tc_log_to_api': str(os.getenv('TC_LOG_TO_API', 'false')).lower() in ['true'],
    # paths
    'tc_api_path': os.getenv('TC_API_PATH'),
    'tc_in_path': os.getenv('TC_IN_PATH', 'log'),
    'tc_log_path': os.getenv('TC_LOG_PATH', 'log'),
    'tc_out_path': os.getenv('TC_OUT_API', 'log'),
    'tc_temp_path': os.getenv('TC_TEMP_PATH', 'log'),
    # playbooks
    'tc_playbook_db_type': os.getenv('TC_PLAYBOOK_DB_TYPE', 'Redis'),
    'tc_playbook_db_context': os.getenv(
        'TC_PLAYBOOK_DB_CONTEXT', '0d5a675a-1d60-4679-bd01-3948d6a0a8bd'
    ),
    'tc_playbook_db_path': os.getenv('TC_PLAYBOOK_DB_PATH', 'localhost'),
    'tc_playbook_db_port': os.getenv('TC_PLAYBOOK_DB_PORT', '6379'),
    # proxy
    'tc_proxy_tc': str(os.getenv('TC_PROXY_TC', 'false')).lower() in ['true'],
    'tc_proxy_external': str(os.getenv('TC_PROXY_EXTERNAL', 'false')).lower() in ['true'],
}

# proxy
if os.getenv('TC_PROXY_HOST'):
    _config_data['tc_proxy_host'] = os.getenv('TC_PROXY_HOST')
if os.getenv('TC_PROXY_PORT'):
    _config_data['tc_proxy_port'] = os.getenv('TC_PROXY_PORT')
if os.getenv('TC_PROXY_USERNAME'):
    _config_data['tc_proxy_username'] = os.getenv('TC_PROXY_USERNAME')
if os.getenv('TC_PROXY_PASSWORD'):
    _config_data['tc_proxy_password'] = os.getenv('TC_PROXY_PASSWORD')


def pytest_configure(config):  # pylint: disable=unused-argument
    """Execute configure logic.

    Allows plugins and conftest files to perform initial configuration. This hook is called for
    every plugin and initial conftest file after command line options have been parsed.
    """

    # remove log directory
    try:
        shutil.rmtree('log')
    except OSError:
        pass

    # create testing install.json
    with open('install.json', 'w') as fh:
        json.dump(pytest_install_json, fh, indent=2)


def pytest_sessionstart(session):  # pylint: disable=unused-argument
    """Execute session start logic.

    Runs after the Session object has been created and before performing collection and entering
    the run test loop.
    """


def pytest_sessionfinish(session, exitstatus):  # pylint: disable=unused-argument
    """Execute session finish logic.

    Runs after whole test run completes, before returning the exit status.
    """


def pytest_unconfigure(config):  # pylint: disable=unused-argument
    """Execute uncofigure logic before test process is exited."""
    try:
        # remove temp install.json directory
        os.remove('install.json')
    except OSError:
        pass


#
# fixtures
#


# @pytest.fixture(scope='module')
@pytest.fixture()
def config_data():
    """Return tcex config data."""
    return _config_data


@pytest.fixture()
def tc_api_token():
    """Return a valid TC api token."""
    return tc_token.api_token


@pytest.fixture()
def tc_log_file():
    """Return tcex config data."""
    return _tc_log_file()


@pytest.fixture()
def tc_service_token():
    """Return a valid TC service token."""
    return tc_token.service_token


@pytest.fixture()
def tcex():
    """Return an instance of tcex."""
    # create log structure for feature/test (e.g., args/test_args.log)
    config_data_ = dict(_config_data)
    config_data_['tc_log_file'] = _tc_log_file()

    # clear sys.argv to avoid invalid arguments
    sys.argv = sys.argv[:1]
    return TcEx(config=config_data_)


#
# misc functions
#


def _tc_log_file():
    """Return config file name for current test case."""
    test_data = os.getenv('PYTEST_CURRENT_TEST').split(' ')[0].split('::')
    test_feature = test_data[0].split('/')[1].replace('/', '-')
    test_name = test_data[-1].replace('/', '-').replace('[', '-')
    return os.path.join(test_feature, '{}.log'.format(test_name))
