# -*- coding: utf-8 -*-
"""Base pytest configuration file."""
import os
import shutil

import pytest
import redis

from .mock_app import MockApp


#
# fixtures
#


@pytest.fixture()
def config_data():
    """Return tcex config data."""
    app = MockApp(runtime_level='Playbook')
    return app.config_data


@pytest.fixture()
def owner_id():
    """Return an owner id."""
    tcex_ = MockApp(runtime_level='Playbook').tcex

    def get_owner_id(name):
        """Return owner Id give the name."""
        id_ = None
        for o in tcex_.session.get('/v2/owners').json().get('data', []).get('owner', []):
            if o.get('name') == name:
                id_ = o.get('id')
                break
        return id_

    return get_owner_id


@pytest.fixture()
def playbook_app():
    """Mock a playbook App."""

    def app(**kwargs):
        if kwargs.get('runtime_level') is None:
            kwargs['runtime_level'] = 'Playbook'
        return MockApp(**kwargs)

    return app


@pytest.fixture()
def redis_client():
    """Return instance of redis_client."""
    host = os.getenv('tc_playbook_db_path', 'localhost')
    port = os.getenv('tc_playbook_db_port', '6379')
    return redis.Redis(host=host, port=port)


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
def tcex_proxy():
    """Return an instance of tcex.

    mitmproxy -p 4242 --ssl-insecure
    """
    # create log structure for feature/test (e.g., args/test_args.log)
    config_data_ = {
        'tc_proxy_tc': True,
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
        os.makedirs(f'log/DEBUG', exist_ok=True)
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

    # cleanup environment variables
    try:
        del os.environ['TC_APP_PARAM_FILE']
    except Exception:
        pass

    try:
        del os.environ['TC_APP_PARAM_KEY']
    except Exception:
        pass

    try:
        del os.environ['TC_APP_PARAM_LOCK']
    except Exception:
        pass
