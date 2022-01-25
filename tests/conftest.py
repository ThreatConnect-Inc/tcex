"""Base pytest configuration file."""
# standard library
import os
import shutil
from typing import TYPE_CHECKING

# third-party
import pytest
import redis

# first-party
from tcex.backports import cached_property
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


@pytest.fixture()
def owner_id():
    """Return an owner id."""
    tcex_ = MockApp(runtime_level='Playbook').tcex

    def get_owner_id(name):
        """Return owner Id give the name."""
        id_ = None
        for o in (
            tcex_.session_tc.get('/v2/owners')  # pylint: disable=no-member
            .json()
            .get('data', [])
            .get('owner', [])
        ):
            if o.get('name') == name:
                id_ = o.get('id')
                break
        return id_

    yield get_owner_id

    tcex_.token.shutdown = True


@pytest.fixture()
def playbook() -> 'Playbook':
    """Return an instance of tcex.playbook."""
    app = MockApp(runtime_level='Playbook')
    yield app.tcex.playbook
    app.tcex.token.shutdown = True


@pytest.fixture()
def playbook_app() -> 'MockApp':
    """Mock a playbook App."""
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
    host = os.getenv('tc_playbook_db_path', 'localhost')
    port = os.getenv('tc_playbook_db_port', '6379')
    return redis.Redis(host=host, port=port)


@pytest.fixture()
def service_app() -> 'MockApp':
    """Mock a service App."""
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
    app = MockApp(runtime_level='Playbook')
    yield app.tcex_log_file
    app.tcex.token.shutdown = True


@pytest.fixture()
def tcex() -> 'TcEx':
    """Return an instance of tcex."""
    registry._reset()
    cached_property._reset()
    scoped_property._reset()
    _tcex = MockApp(runtime_level='Playbook').tcex
    yield _tcex
    _tcex.token.shutdown = True


@pytest.fixture()
def tcex_hmac() -> 'TcEx':
    """Return an instance of tcex with hmac auth."""
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
