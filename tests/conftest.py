"""TcEx Framework Module"""

# standard library
import hashlib
import logging
import os
import re
import shutil
import socket
from collections.abc import Callable, Iterator
from threading import Thread

# third-party
import fakeredis
import pytest
import redis
from _pytest.monkeypatch import MonkeyPatch
from fakeredis import TcpFakeServer

# first-party
from tcex import TcEx
from tcex.app.key_value_store import RedisClient
from tcex.app.playbook.playbook import Playbook
from tcex.logger.trace_logger import TraceLogger
from tcex.pleb.cached_property import cached_property
from tcex.pleb.scoped_property import scoped_property
from tcex.registry import registry
from tests.mock_app import MockApp

_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore

#
# fixtures
#


def _reset_modules():
    """Reset modules that cached_property, scoped_property and registry"""
    registry._reset()
    cached_property._reset()
    scoped_property._reset()


@pytest.fixture(autouse=True)
def change_test_dir(request, monkeypatch: MonkeyPatch):
    """Change the test working directory to prevent conflicts with other tests."""
    test_name = request.node.name

    start_index = re.search(r'\W+', test_name)
    if start_index is not None:
        test_name_prefix = test_name[: start_index.start()]
        test_name_hash = hashlib.sha256(test_name[start_index.start() :].encode()).hexdigest()
        test_name = f'{test_name_prefix}_{test_name_hash}'

    temp_test_path = os.path.join(
        request.fspath.dirname.replace(os.getcwd(), f'{os.getcwd()}/log'), test_name
    )
    _logger.debug(f'Working directory: test-name={request.node.name}, test-path={temp_test_path}')
    os.makedirs(temp_test_path, exist_ok=True)
    os.makedirs(os.path.join(temp_test_path, 'DEBUG'), exist_ok=True)
    monkeypatch.chdir(temp_test_path)


@pytest.fixture()
def owner_id() -> Iterator[Callable]:
    """Return an owner id."""
    _reset_modules()
    _tcex = MockApp(runtime_level='Playbook').tcex

    def get_owner_id(name) -> int | None:
        """Return owner Id give the name."""
        id_ = None
        for o in (
            _tcex.session.tc.get('/v2/owners')
            .json()
            .get('data', [])
            .get('owner', [])
        ):
            if o.get('name') == name:
                id_ = o.get('id')
                break
        return id_

    yield get_owner_id

    _tcex.app.token.shutdown = True


@pytest.fixture()
def playbook() -> Iterator[Playbook]:
    """Return an instance of tcex.app.playbook."""
    _reset_modules()
    app = MockApp(runtime_level='Playbook')
    yield app.tcex.app.playbook
    app.tcex.app.token.shutdown = True


@pytest.fixture()
def playbook_app() -> Iterator[Callable[..., MockApp]]:
    """Mock a playbook App."""
    _reset_modules()
    app_refs: list[MockApp] = []

    def app(**kwargs) -> MockApp:
        nonlocal app_refs
        if kwargs.get('runtime_level') is None:
            kwargs['runtime_level'] = 'Playbook'
        _app = MockApp(**kwargs)
        app_refs.append(_app)
        return _app

    yield app

    for _app in app_refs:
        _app.tcex.app.token.shutdown = True


@pytest.fixture()
def redis_client() -> redis.Redis:
    """Return instance of redis_client."""
    return fakeredis.FakeRedis()


@pytest.fixture()
def service_app() -> Iterator[Callable]:
    """Mock a service App."""
    _reset_modules()
    app_refs: list[MockApp] = []

    def app(**kwargs) -> MockApp:
        nonlocal app_refs
        if kwargs.get('runtime_level') is None:
            kwargs['runtime_level'] = 'TriggerService'
        _app = MockApp(**kwargs)
        app_refs.append(_app)
        return _app

    yield app

    for _app in app_refs:
        _app.tcex.app.token.shutdown = True


@pytest.fixture()
def tcex() -> Iterator[TcEx]:
    """Return an instance of tcex."""
    _reset_modules()
    _tcex = MockApp(runtime_level='Playbook').tcex
    yield _tcex
    _tcex.app.token.shutdown = True


@pytest.fixture()
def tcex_hmac() -> Iterator[TcEx]:
    """Return an instance of tcex with hmac auth."""
    _reset_modules()
    config_data_ = {
        'tc_token': None,
        'tc_token_expires': None,
    }
    app = MockApp(runtime_level='Playbook', config_data=config_data_)
    yield app.tcex
    app.tcex.app.token.shutdown = True


# @pytest.fixture(scope='module')
@pytest.fixture()
def tcex_proxy() -> Iterator[TcEx]:
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
    app.tcex.app.token.shutdown = True


#
# pytest startup/shutdown configuration
#


def pytest_configure(config):
    """Execute configure logic.

    Allows plugins and conftest files to perform initial configuration. This hook is called for
    every plugin and initial conftest file after command line options have been parsed.
    """

    os.environ['TCEX_TEST_DIR'] = os.path.join(os.getcwd(), 'tests')

    # remove log directory
    try:
        shutil.rmtree('log')
    except OSError:
        pass

    config.tcp_fake_server = None  # type: ignore
    server_address = 'localhost'
    server_port = 6379

    def is_port_in_use() -> bool:
        """Check if a port is in use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((server_address, server_port)) == 0

    if not is_port_in_use():
        tcp_fake_server = TcpFakeServer((server_address, server_port), server_type='redis')
        tcp_fake_server.daemon_threads = True
        t = Thread(target=tcp_fake_server.serve_forever, daemon=True)
        t.start()
        config.tcp_fake_server = tcp_fake_server  # type: ignore

        print('Starting fake Redis server.')  # noqa: T201


def pytest_sessionstart(session):
    """Execute session start logic.

    Runs after the Session object has been created and before performing collection and entering
    the run test loop.
    """


def pytest_sessionfinish(session, exitstatus):
    """Execute session finish logic.

    Runs after whole test run completes, before returning the exit status.
    """


def pytest_unconfigure(config):
    """Execute unconfigure logic before test process is exited."""
    if config.tcp_fake_server:  # type: ignore
        config.tcp_fake_server.server_close()  # type: ignore
        config.tcp_fake_server.shutdown()  # type: ignore

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
