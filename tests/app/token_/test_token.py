"""TcEx Framework Module"""

# standard library
import threading
import time
from collections.abc import Callable

# third-party
import pytest
from _pytest.monkeypatch import MonkeyPatch

# first-party
from tcex.app.token.token import Token
from tcex.input.field_type import Sensitive
from tcex.pleb.cached_property import cached_property
from tcex.pleb.scoped_property import scoped_property
from tests.mock_app import MockApp


def await_token_barrier_enabled(token_service: Token, timeout: int = 120):
    """Await for token barrier to be enabled"""
    while token_service._barrier.is_set():
        time.sleep(1)
        timeout -= 1
        if timeout <= 0:
            raise RuntimeError('Timeout expired while waiting for token barrier to be enabled')


def await_token_barrier_disabled(token_service: Token, timeout: int = 60):
    """Await token service to be disabled"""
    result = token_service._barrier.wait(timeout=timeout)

    if not result:
        raise RuntimeError('Timeout Expired while waiting for token barrier to be disabled')


def await_token_renewal_cycle(token_service: Token, timeout: int = 60):
    """Await for a token renewal cycle to take place and finish"""
    # wait until renewal monitor has enabled the barrier (is_set == False), which
    # means that renewal monitor has started renewal process
    await_token_barrier_enabled(token_service, timeout)

    # wait until renewal monitor has disabled the barrier, meaning that renewal is done
    await_token_barrier_disabled(token_service, timeout)



@pytest.mark.run(order=3)
class TestToken:
    """Test Suite"""

    def setup_method(self):
        """Setup method for all tests."""
        scoped_property._reset()
        cached_property._reset()

    @property
    def thread_name(self):
        """Return the current thread name."""
        return threading.current_thread().name

    def test_token_registration_process(
        self, service_app: Callable[..., MockApp], monkeypatch: pytest.MonkeyPatch
    ):
        """Test Case

        Usage of token is out of scope of this test. This simply tests that register_token
        sets up token correctly.
        """
        monkeypatch.setenv('TC_TOKEN_SLEEP_INTERVAL', '1')
        app = service_app()

        # get token from fixture
        tc_token = app.service_token
        tc_token_expires = int(time.time()) + 999

        app.tcex.app.token.register_token(
            key=self.thread_name, token=tc_token, expires=tc_token_expires
        )
        assert isinstance(
            app.tcex.app.token.token, Sensitive
        ), 'Token was not wrapped with Sensitive'
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
    def test_token_setters(service_app: Callable[..., MockApp], monkeypatch: MonkeyPatch):
        """Test Case

        Test using token and token_expires setters.
        """
        monkeypatch.setenv('TC_TOKEN_SLEEP_INTERVAL', '1')

        app = service_app()

        # pass token setter a str type
        token = app.api_token
        app.tcex.app.token.token = token
        app.tcex.app.token.token_expires = '1700000000'

        # test passing a string
        assert isinstance(app.tcex.app.token.token, Sensitive), 'Token should be type Sensitive'
        token_ = app.tcex.app.token.token
        assert token_ is not None, 'Token should not be None'
        assert token_.value == token
        assert app.tcex.app.token.token_expires == 1700000000

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
    ):
        """Test Case"""
        monkeypatch.setenv('TC_TOKEN_SLEEP_INTERVAL', '1')
        # coverage: hit except on unregister_token()
        service_app().tcex.app.token.unregister_token('zzzzzz')

    def test_request_with_expired_token(
        self, service_app: Callable[..., MockApp], monkeypatch: pytest.MonkeyPatch
    ):
        """Test Case"""
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
    ):
        """Test Case"""
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
    ):
        """Test Case"""
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
    ):
        """Test Case"""
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
    ):
        """Test Case

        A race condition exists where the app gets a TC token from the tokens.py module
        but does not use it before the tokens.py renewal monitor renews the token.

        If an app does not use a token before it is renewed by the renewal monitor,
        then the token becomes invalid, and a 401 response is returned. Logic has been put in
        place so that tc_session detects the 401 response and reattempts the request. When the
        request is reattempted, tc_session should request a new token from tokens.py, and tokens.py
        should only return the new token after the renewal process is complete. This test exercises
        this scenario.
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
        original_token_header_method = getattr(app.tcex.session.tc.auth, '_token_header')

        first_generation_of_header = True

        def mock_token_header(*args, **kwargs):
            # standard library
            import logging

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
                assert (
                    tc_token.value != app.tcex.app.token.token.value
                ), 'Original token not renewed'

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
            assert False, f'API call failed {r.text}'

        app.tcex.app.token.unregister_token(threading.current_thread().name)
