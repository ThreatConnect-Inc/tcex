"""TestToken for TcEx App Token Module Testing.

This module contains comprehensive test cases for the TcEx App Token Module, specifically
testing the token management functionality including token registration, renewal, expiration
handling, race conditions, and thread safety across various token lifecycle scenarios.

Classes:
    TestToken: Test class for TcEx App Token Module functionality

TcEx Module Tested: app.token.token
"""


import logging
import threading
import time
from collections.abc import Callable


import pytest

from _pytest.monkeypatch import MonkeyPatch


from tcex.app.token.token import Token
from tcex.input.field_type import Sensitive
from tcex.pleb.cached_property import cached_property
from tcex.pleb.scoped_property import scoped_property
from tests.mock_app import MockApp

# Test constants
TEST_TOKEN_EXPIRES_TIMESTAMP = 1700000000


def await_token_barrier_enabled(token_service: Token, timeout: int = 120) -> None:
    """Await for token barrier to be enabled.

    This utility function waits for the token barrier to be enabled, which indicates
    that the token renewal monitor has started a renewal cycle and is blocking
    access to tokens.

    Args:
        token_service: The Token service instance to monitor
        timeout: Maximum time to wait in seconds before raising an error
    """
    while token_service._barrier.is_set():  # noqa: SLF001
        time.sleep(1)
        timeout -= 1
        if timeout <= 0:
            error_msg = 'Timeout expired while waiting for token barrier to be enabled'
            raise RuntimeError(error_msg)


def await_token_barrier_disabled(token_service: Token, timeout: int = 60) -> None:
    """Await token service to be disabled.

    This utility function waits for the token barrier to be disabled, which indicates
    that the token renewal monitor has completed a renewal cycle and tokens are
    accessible again.

    Args:
        token_service: The Token service instance to monitor
        timeout: Maximum time to wait in seconds before raising an error
    """
    result = token_service._barrier.wait(timeout=timeout)  # noqa: SLF001

    if not result:
        ex_msg = 'Timeout Expired while waiting for token barrier to be disabled'
        raise RuntimeError(ex_msg)


def await_token_renewal_cycle(token_service: Token, timeout: int = 60) -> None:
    """Await for a token renewal cycle to take place and finish.

    This utility function waits for a complete token renewal cycle to complete,
    including both the barrier being enabled and then disabled, ensuring that
    the renewal process has fully finished.

    Args:
        token_service: The Token service instance to monitor
        timeout: Maximum time to wait in seconds before raising an error
    """
    # wait until renewal monitor has enabled the barrier (is_set == False), which
    # means that renewal monitor has started renewal process
    await_token_barrier_enabled(token_service, timeout)

    # wait until renewal monitor has disabled the barrier, meaning that renewal is done
    await_token_barrier_disabled(token_service, timeout)


@pytest.mark.run(order=3)
class TestToken:
    """TestToken for TcEx App Token Module Testing.

    This class provides comprehensive testing for the TcEx App Token Module, covering
    various token management scenarios including registration, renewal, expiration
    handling, race conditions, thread safety, and error handling across different
    token lifecycle states.
    """

    def setup_method(self) -> None:
        """Setup method for all tests.

        This method is called before each test method to reset scoped and cached
        properties, ensuring a clean testing environment for each test case.
        """
        scoped_property._reset()  # noqa: SLF001
        cached_property._reset()  # noqa: SLF001

    @property
    def thread_name(self) -> str:
        """Return the current thread name.

        This property provides the current thread name for use in token registration
        and testing scenarios that require thread-specific token management.
        """
        return threading.current_thread().name

    def test_token_registration_process(
        self, service_app: Callable[..., MockApp], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test Token Registration Process for TcEx App Token Module.

        This test case verifies that the token registration process works correctly
        by testing both string and Sensitive token registration, ensuring proper
        token wrapping, expiration handling, and cleanup operations.

        Fixtures:
            service_app: Callable function that returns a configured MockApp instance
            monkeypatch: Pytest fixture for modifying environment variables and attributes
        """
        monkeypatch.setenv('TC_TOKEN_SLEEP_INTERVAL', '1')
        app = service_app()

        # get token from fixture
        tc_token = app.service_token
        tc_token_expires = int(time.time()) + 999

        app.tcex.app.token.register_token(
            key=self.thread_name, token=tc_token, expires=tc_token_expires
        )
        assert isinstance(app.tcex.app.token.token, Sensitive), (
            'Token was not wrapped with Sensitive'
        )
        assert tc_token == app.tcex.app.token.token.value
        assert tc_token_expires == app.tcex.app.token.token_expires

        # test registering with Sensitive
        app.tcex.app.token.register_token(
            key=self.thread_name, token=Sensitive(tc_token), expires=tc_token_expires
        )
        assert isinstance(app.tcex.app.token.token, Sensitive), 'Token should be a Sensitive object'
        assert tc_token == app.tcex.app.token.token.value
        assert tc_token_expires == app.tcex.app.token.token_expires

        app.tcex.app.token.unregister_token(self.thread_name)
        app.tcex.app.token.shutdown = True  # coverage

    @staticmethod
    def test_token_setters(service_app: Callable[..., MockApp], monkeypatch: MonkeyPatch) -> None:
        """Test Token Setters for TcEx App Token Module.

        This test case verifies that the token and token_expires setters work correctly
        by testing both string and Sensitive token types, ensuring proper type
        conversion and value assignment.

        Fixtures:
            service_app: Callable function that returns a configured MockApp instance
            monkeypatch: Pytest fixture for modifying environment variables and attributes
        """
        monkeypatch.setenv('TC_TOKEN_SLEEP_INTERVAL', '1')

        app = service_app()

        # pass token setter a str type
        token = app.api_token
        app.tcex.app.token.token = token
        app.tcex.app.token.token_expires = str(TEST_TOKEN_EXPIRES_TIMESTAMP)

        # test passing a string
        assert isinstance(app.tcex.app.token.token, Sensitive), 'Token should be type Sensitive'
        token_ = app.tcex.app.token.token
        assert token_ is not None, 'Token should not be None'
        assert token_.value == token
        assert app.tcex.app.token.token_expires == TEST_TOKEN_EXPIRES_TIMESTAMP

        # pass token setter a Sensitive type
        token = app.api_token
        app.tcex.app.token.token = Sensitive(token)

        assert isinstance(app.tcex.app.token.token, Sensitive), 'Token should be type Sensitive'
        token_ = app.tcex.app.token.token
        assert token_ is not None, 'Token should not be None'
        assert token_.value == token

    @staticmethod
    def test_invalid_unregister_token(
        service_app: Callable[..., MockApp], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test Invalid Unregister Token for TcEx App Token Module.

        This test case verifies that the token unregistration process handles
        invalid keys gracefully by attempting to unregister a non-existent token
        key, ensuring proper error handling and coverage.

        Fixtures:
            service_app: Callable function that returns a configured MockApp instance
            monkeypatch: Pytest fixture for modifying environment variables and attributes
        """
        monkeypatch.setenv('TC_TOKEN_SLEEP_INTERVAL', '1')
        # coverage: hit except on unregister_token()
        service_app().tcex.app.token.unregister_token('zzzzzz')

    def test_request_with_expired_token(
        self, service_app: Callable[..., MockApp], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test Request with Expired Token for TcEx App Token Module.

        This test case verifies that requests with expired tokens are handled
        correctly by registering an expired token and ensuring that API calls
        fail as expected, validating the token expiration mechanism.

        Fixtures:
            service_app: Callable function that returns a configured MockApp instance
            monkeypatch: Pytest fixture for modifying environment variables and attributes
        """
        # to give us a chance to use expired token in a request
        monkeypatch.setenv('TC_TOKEN_SLEEP_INTERVAL', '10')

        # get clean instance of tcex
        tcex = service_app().tcex
        # Initialize Token module, which starts token renewal monitor and immediately kicks off
        # first renewal cycle. Wait until initial cycle is finished before staging test token

        await_token_renewal_cycle(tcex.app.token)

        token = 'JOB:3:ksKNpI:1567352558827:220:null:YPSaVFIGVbIkt1cfi4DzoG2bjWwsLBfwv9fJbeEx68A='

        # register expired token
        tcex.app.token.register_token(
            key=self.thread_name,
            token=token,
            # expire token immediately. Note this by itself does not expire the token. This merely
            # tells the renewal monitor that the token is expired. The token used in this test is
            # a very old token which is expired.
            expires=int(time.time()) - 999,
        )

        # ensure token was registered
        assert tcex.app.token.token is not None, 'Token should not be None'
        assert tcex.app.token.token.value == token
        # ensure request that uses token fails
        assert not tcex.session.tc.get('/v2/owners').ok, 'API call did not fail as expected'
        # ensure token did not change
        assert tcex.app.token.token.value == token

    def test_expired_token_could_not_be_renewed(
        self, service_app: Callable[..., MockApp], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test Expired Token Could Not Be Renewed for TcEx App Token Module.

        This test case verifies that tokens that cannot be renewed are properly
        removed from the token service by registering an expired token and waiting
        for a renewal cycle to fail, ensuring proper cleanup of invalid tokens.

        Fixtures:
            service_app: Callable function that returns a configured MockApp instance
            monkeypatch: Pytest fixture for modifying environment variables and attributes
        """
        # reduce the amount of time between token renewal cycles, but make it long enough
        # to give us a chance to stage an expired token and validate it before a renewal is done
        monkeypatch.setenv('TC_TOKEN_SLEEP_INTERVAL', '10')

        # get clean instance of tcex
        tcex = service_app().tcex

        # Initialize Token module, which starts token renewal monitor and immediately kicks off
        # first renewal cycle. Wait until initial cycle is finished before staging test token
        await_token_renewal_cycle(tcex.app.token)

        token = 'JOB:3:ksKNpI:1567352558827:220:null:YPSaVFIGVbIkt1cfi4DzoG2bjWwsLBfwv9fJbeEx68A='
        # register expired token
        tcex.app.token.register_token(
            key=self.thread_name,
            token=token,
            # expire token immediately. Note this by itself does not expire the token. This merely
            # tells the renewal monitor that the token is expired. The token used in this test is
            # a very old token which is expired.
            expires=int(time.time()) - 999,
        )

        # ensure token was registered
        assert tcex.app.token.token is not None, 'Token should not be None'
        assert tcex.app.token.token.value == token

        # await a renewal attempt. Should fail, as token is very old and cannot be renewed
        await_token_renewal_cycle(tcex.app.token)

        # renewal failed, token removed from tokens module
        assert tcex.app.token.token is None

    def test_expired_token_is_renewed(
        self, service_app: Callable[..., MockApp], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test Expired Token is Renewed for TcEx App Token Module.

        This test case verifies that valid tokens with expired timestamps are
        properly renewed by the token renewal monitor, ensuring that the renewal
        process works correctly and API calls succeed after renewal.

        Fixtures:
            service_app: Callable function that returns a configured MockApp instance
            monkeypatch: Pytest fixture for modifying environment variables and attributes
        """
        # reduce the amount of time between token renewal cycles, but make it long enough
        # to give us a chance to setup an expired token and validate it before the
        # renewal monitor renews it.
        monkeypatch.setenv('TC_TOKEN_SLEEP_INTERVAL', '10')

        app = service_app()

        # Initialize Token module, which starts token renewal monitor and immediately kicks off
        # first renewal cycle. Wait until initial cycle is finished before staging test token
        await_token_renewal_cycle(app.tcex.app.token)

        # get token from fixture
        tc_token = app.service_token
        # Token itself is valid, but we tell tokens.py that it is now expired
        tc_token_expires = int(time.time()) - 999  # expire token immediately

        app.tcex.app.token.register_token(
            key=self.thread_name, token=tc_token, expires=tc_token_expires
        )

        # "expired" token registered successfully.
        assert app.tcex.app.token.token is not None, 'Token should not be None'
        assert app.tcex.app.token.token.value == tc_token

        await_token_renewal_cycle(app.tcex.app.token)

        assert app.tcex.app.token.token.value != tc_token, 'Token not was not renewed'
        assert app.tcex.session.tc.get('/v2/owners').ok, 'API call failed after token renewal'

        app.tcex.app.token.unregister_token(self.thread_name)

    def test_token_renewal_monitor_thread_exits_unexpectedly(
        self, service_app: Callable[..., MockApp], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test Token Renewal Monitor Thread Exits Unexpectedly for TcEx App Token Module.

        This test case verifies that the token renewal monitor handles unexpected
        thread exits gracefully by intentionally corrupting the monitor state and
        ensuring that proper error handling occurs when the barrier times out.

        Fixtures:
            service_app: Callable function that returns a configured MockApp instance
            monkeypatch: Pytest fixture for modifying environment variables and attributes
        """
        monkeypatch.setenv('TC_TOKEN_SLEEP_INTERVAL', '5')

        app = service_app()
        # Initialize Token module, which starts token renewal monitor and immediately kicks off
        # first renewal cycle. Wait until initial cycle is finished before intentionally
        # corrupting monitor thread state. Otherwise, test executes too fast and the
        # corrupted state is never used, as everything happens within the initial renewal cycle
        await_token_renewal_cycle(app.tcex.app.token)
        tc_token = app.service_token
        tc_token_expires = int(time.time()) - 999
        # stage token to give renewal monitor some work
        app.tcex.app.token.register_token(
            key=self.thread_name, token=tc_token, expires=tc_token_expires
        )

        # set token_window to a value that is not an integer to cause an exception
        # within the renewal monitor on purpose
        app.tcex.app.token.token_window = 'not an integer'  # type: ignore

        # wait until renewal monitor enters a renewal cycle. Monitor should enable the barrier
        # but the exception will cause it to exit before it disables the barrier.
        await_token_barrier_enabled(app.tcex.app.token)

        # attempt to retrieve token. Barrier await timeout should expire. RuntimeError expected
        with pytest.raises(RuntimeError):
            _ = app.tcex.app.token.token

    def test_token_race_condition(
        self, service_app: Callable[..., MockApp], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test Token Race Condition for TcEx App Token Module.

        This test case verifies that the token race condition handling works correctly
        by simulating a scenario where a token becomes stale between retrieval and use,
        ensuring that the automatic retry mechanism with renewed tokens functions properly.

        Fixtures:
            service_app: Callable function that returns a configured MockApp instance
            monkeypatch: Pytest fixture for modifying environment variables and attributes
        """
        # reduce the amount of time between token renewal cycles, but make it long enough
        # to keep test logic consistent
        monkeypatch.setenv('TC_TOKEN_SLEEP_INTERVAL', '10')

        # begin code that patches TokenAuth so that it grabs original API token, but waits
        # until the renewal monitor has renewed the token in order to use it.

        app = service_app()

        # Initialize Token module, which starts token renewal monitor and immediately kicks off
        # first renewal cycle. Wait until initial cycle is finished before staging test token
        await_token_renewal_cycle(app.tcex.app.token)

        # get new API token
        tc_token = Sensitive(app.service_token)

        # register new token with expiration time in the past, so that renewal monitor
        # renews this token upon next execution of token renewal logic
        tc_token_expires = int(time.time()) - 999

        # The goal is to prepare a token header but wait until it is no longer valid before it is
        # used. The token header is no longer valid because the renewal monitor would have
        # renewed the token being used in the header, which causes the old token to not be valid
        # anymore.
        original_token_header_method = app.tcex.session.tc.auth._token_header  # noqa: SLF001 # type: ignore

        first_generation_of_header = True

        def mock_token_header(*args, **kwargs):
            log = logging.getLogger('tcex')
            nonlocal first_generation_of_header
            # retrieve token header, which should have a valid token at this point.
            header = original_token_header_method(*args, **kwargs)

            # If this is the first time generating a token header, wait until token in header is
            # stale (renewal monitor has renewed token, making previous token invalid) before
            # returning it. We expect the application to use the stale header, receive a 401
            # response, then retry the request again. This means that a token header will be
            # requested a second time (executing this function again). This if statement will not
            # execute on the second run of this function. On second execution, the header will
            # simply be returned, and such header should now have a new token in it.
            if first_generation_of_header:
                first_generation_of_header = False

                # token that was originally staged should be in header. If not, then the renewal
                # monitor has already renewed the staged token, which corrupts test state
                assert tc_token.value in header, 'Original token has been unexpectedly renewed.'

                # await for renewal cycle, which should renew the token
                await_token_renewal_cycle(app.tcex.app.token)

                # ensure token has been renewed
                assert app.tcex.app.token.token is not None, 'Token was not renewed'
                assert tc_token.value != app.tcex.app.token.token.value, (
                    'Original token not renewed'
                )

                # the token in the header is now stale, return stale header
                log.info('returning stale header')
                return header
            # return header as normal
            log.info('returning good header')
            # token should have been renewed upon second call to this function, so the header
            # should not include the old token.
            assert tc_token.value not in header
            return header

        monkeypatch.setattr(app.tcex.session.tc.auth, '_token_header', mock_token_header)

        # register "expired" token for the current thread. Note: Token is actually good,
        # but we are setting a bad expiration time on the token service so that the
        # renewal monitor knows to renew it.
        app.tcex.app.token.register_token(
            key=threading.current_thread().name, token=tc_token, expires=tc_token_expires
        )

        # make request which should first use a stale token then should automatically retry
        # with renewed token
        r = app.tcex.session.tc.get('/v2/owners')
        if not r.ok:
            pytest.fail(f'API call failed {r.text}')

        app.tcex.app.token.unregister_token(threading.current_thread().name)
