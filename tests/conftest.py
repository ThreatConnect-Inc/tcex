"""Base pytest configuration file."""
# standard library
import os
import shutil
from typing import TYPE_CHECKING

# third-party
import fakeredis
import pytest
import redis

# first-party
from tcex.backports import cached_property
from tcex.key_value_store import RedisClient
from tcex.pleb.registry import registry
from tcex.pleb.scoped_property import scoped_property
from tests.mock_app import MockApp

if TYPE_CHECKING:
    # first-party
    from tcex import TcEx
    from tcex.playbook.playbook import Playbook

#
# fixtures
#


# TODO: [med] this is not longer support, where is it needed?
# @pytest.fixture()
# def config_data():
#     """Return tcex config data."""
#     app = MockApp(runtime_level='Playbook')
#     return app.config_data


def _reset_modules():
    """Reset modules that cached_property, scoped_property and registry"""
    registry._reset()
    cached_property._reset()
    scoped_property._reset()


@pytest.fixture()
def owner_id():
    """Return an owner id."""
    _reset_modules()
    _tcex = MockApp(runtime_level='Playbook').tcex

    def get_owner_id(name):
        """Return owner Id give the name."""
        id_ = None
        for o in (
            _tcex.session_tc.get('/v2/owners')  # pylint: disable=no-member
            .json()
            .get('data', [])
            .get('owner', [])
        ):
            if o.get('name') == name:
                id_ = o.get('id')
                break
        return id_

    yield get_owner_id

    _tcex.token.shutdown = True


@pytest.fixture()
def playbook() -> 'Playbook':
    """Return an instance of tcex.playbook."""
    _reset_modules()
    app = MockApp(runtime_level='Playbook')
    yield app.tcex.playbook
    app.tcex.token.shutdown = True


@pytest.fixture()
def playbook_app() -> 'MockApp':
    """Mock a playbook App."""
    _reset_modules()
    app_refs = []

    def app(**kwargs):
        nonlocal app_refs
        if kwargs.get('runtime_level') is None:
            kwargs['runtime_level'] = 'Playbook'
        _app = MockApp(**kwargs)
        app_refs.append(_app)
        return _app

    yield app

    for _app in app_refs:
        _app.tcex.token.shutdown = True


@pytest.fixture()
def redis_client() -> redis.Redis:
    """Return instance of redis_client."""
    return fakeredis.FakeRedis()


@pytest.fixture()
def service_app() -> 'MockApp':
    """Mock a service App."""
    _reset_modules()
    app_refs = []

    def app(**kwargs):
        nonlocal app_refs
        if kwargs.get('runtime_level') is None:
            kwargs['runtime_level'] = 'TriggerService'
        _app = MockApp(**kwargs)
        app_refs.append(_app)
        return _app

    yield app

    for _app in app_refs:
        _app.tcex.token.shutdown = True


@pytest.fixture()
def tc_log_file() -> str:
    """Return tcex config data."""
    _reset_modules()
    app = MockApp(runtime_level='Playbook')
    yield app.tcex_log_file
    app.tcex.token.shutdown = True


@pytest.fixture()
def tcex() -> 'TcEx':
    """Return an instance of tcex."""
    _reset_modules()
    _tcex = MockApp(runtime_level='Playbook').tcex
    yield _tcex
    _tcex.token.shutdown = True


@pytest.fixture()
def tcex_hmac() -> 'TcEx':
    """Return an instance of tcex with hmac auth."""
    _reset_modules()
    config_data_ = {
        'tc_token': None,
        'tc_token_expires': None,
    }
    app = MockApp(runtime_level='Playbook', config_data=config_data_)
    yield app.tcex
    app.tcex.token.shutdown = True


# @pytest.fixture(scope='module')
@pytest.fixture()
def tcex_proxy() -> 'TcEx':
    """Return an instance of tcex with proxy configured.

    mitmproxy -p 4242 --ssl-insecure
    """
    _reset_modules()
    config_data_ = {
        'tc_proxy_tc': True,
        'tc_proxy_external': True,
    }
    app = MockApp(runtime_level='Playbook', config_data=config_data_)
    yield app.tcex
    app.tcex.token.shutdown = True


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
        os.makedirs('log/DEBUG', exist_ok=True)
    except OSError:
        pass

    # Replace Redis with FakeRedis for testing
    client_prop = cached_property(lambda *args: fakeredis.FakeRedis())
    client_prop.__set_name__(RedisClient, 'client')
    RedisClient.client = client_prop


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
    """Execute unconfigure logic before test process is exited."""
    try:
        # remove temp app_config.json file
        os.remove('app_config.json')
    except OSError:
        pass

    try:
        # remove temp install.json file
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
