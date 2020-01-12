# -*- coding: utf-8 -*-
"""Base pytest configuration file."""
import os
import shutil
import pytest
from .mock_app import MockApp


#
# fixtures
#


@pytest.fixture()
def config_data():
    """Return tcex config data."""
    app = MockApp(runtime_level='Playbook')
    return app.mock_config_data


@pytest.fixture()
def service_app():
    """Mock a service App."""

    def app(**kwargs):
        if kwargs.get('runtime_level') is None:
            kwargs['runtime_level'] = 'TriggerService'
        return MockApp(**kwargs)

    return app


@pytest.fixture()
def tc_log_file():
    """Return tcex config data."""
    app = MockApp(runtime_level='Playbook')
    return app.tcex_log_file


@pytest.fixture()
def tcex():
    """Return an instance of tcex."""
    app = MockApp(runtime_level='Playbook')
    return app.tcex


@pytest.fixture()
def tcex_hmac():
    """Return an instance of tcex."""
    # create log structure for feature/test (e.g., args/test_args.log)
    config_data_ = {
        'tc_token': None,
        'tc_token_expires': None,
    }
    app = MockApp(runtime_level='Playbook', config_data=config_data_)
    return app.tcex


# @pytest.fixture(scope='module')
@pytest.fixture()
def tcex_proxy_external():
    """Return an instance of tcex.

    mitmproxy -p 4242 --ssl-insecure
    """
    # create log structure for feature/test (e.g., args/test_args.log)
    config_data_ = {
        'tc_proxy_external': True,
    }
    app = MockApp(runtime_level='Playbook', config_data=config_data_)
    return app.tcex


#
# pytest startup/shutdown configuration
#


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
