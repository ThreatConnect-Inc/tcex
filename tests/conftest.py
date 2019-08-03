# -*- coding: utf-8 -*-
"""Base pytest configuration file."""
import json
import os
import shutil

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


# @pytest.fixture(scope='module')
# def token_data():
#     """Get a valid TC token."""
#     token_url = os.getenv('TOKEN_PROVIDER')
#     r = requests.get(token_url, verify=False)
#     return r.json()
