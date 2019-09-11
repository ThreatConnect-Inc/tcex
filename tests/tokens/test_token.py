# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
import threading
import time


class TestLogs:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @property
    def thread_name(self):
        """Return the current thread name."""
        return threading.current_thread().name

    def test_expired_token(self, tcex):
        """Test thread file handler."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        token_key = '666'
        tcex.token.register_token(
            key=token_key,
            token=(
                'JOB:3:ksKNpI:1567352558827:220:null:YPSaVFIGVbIkt1cfi4DzoG2bjWwsLBfwv9fJbeEx68A='
            ),
            expires=int(time.time()) - 999,  # expire token immediately
        )

        # create a thread to test register_thread
        t = threading.Thread(
            name='pytest-token-fail', target=self.token_thread_fail, args=(tcex, token_key)
        )
        t.start()
        t.join()

        tcex.token.unregister_token(token_key)
        tcex.token.unregister_token('dummy-key')  # hit except on unregister_token()

    @staticmethod
    def test_invalid_register_token(tcex):
        """Test invalid token data."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        # test register_token() [if token is None or expires is None:]
        try:
            tcex.token.register_token('dummy-key', None, None)
        except RuntimeError:
            assert True

    @staticmethod
    def test_invalid_unregister_token(tcex):
        """Test invalid token data."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        tcex.token.unregister_token('zzzzzz')  # hit except on unregister_token()

    def test_register_token_fail(self, tcex, tc_service_token):
        """Test thread file handler."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        # get token from fixture
        tc_token = tc_service_token
        tc_token_expires = int(time.time()) - 999

        token_key = 'thread-as-key'
        tcex.token.register_token(key=token_key, token=tc_token, expires=tc_token_expires)

        # create a thread to test register_thread
        t = threading.Thread(
            name=token_key, target=self.token_thread_pass, args=(tcex, token_key, False, False)
        )
        t.start()
        t.join()

        tcex.token.unregister_token(token_key)

    def test_register_token_thread_as_key(self, tcex, tc_service_token):
        """Test thread file handler."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        # get token from fixture
        tc_token = tc_service_token
        tc_token_expires = int(time.time()) + 999

        token_key = 'thread-as-key'
        tcex.token.register_token(key=token_key, token=tc_token, expires=tc_token_expires)

        # create a thread to test register_thread
        t = threading.Thread(
            name=token_key, target=self.token_thread_pass, args=(tcex, token_key, False, False)
        )
        t.start()
        t.join()

        tcex.token.unregister_token(token_key)

    @staticmethod
    def test_token_setter(tcex, tc_api_token):
        """Testing token setters."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        tcex.token.token = tc_api_token
        tcex.token.token_expires = '1700000000'

        try:
            r = tcex.session.get('/v2/owners')
            assert r.status_code == 200, 'Failed API call ({})'.format(r.text)
        except RuntimeError:
            assert False

    def test_token_thread_with_renewal(self, tcex, tc_service_token):
        """Test thread file handler."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        # get token from fixture
        tc_token = tc_service_token
        tc_token_expires = int(time.time()) - 999  # expire token immediately

        token_key = '1234'
        tcex.token.register_token(key=token_key, token=tc_token, expires=tc_token_expires)

        # create a thread to test register_thread
        t = threading.Thread(
            name='pytest-token-pass', target=self.token_thread_pass, args=(tcex, token_key)
        )
        t.start()
        t.join()

        tcex.token.unregister_token(token_key)

    def token_thread_fail(self, tcex, key):
        """Test token failure."""
        tcex.token.register_thread(key, self.thread_name)

        # sleep until token renewal
        time.sleep(tcex.token.sleep_interval + 1)

        try:
            tcex.session.get('/v2/owners')
        except RuntimeError:
            pass

        tcex.token.unregister_thread(key, self.thread_name)

    def token_thread_pass(self, tcex, key, sleep=True, register_thread=True):
        """Test token is pass."""
        if register_thread:
            tcex.token.register_thread(key, self.thread_name)

        # sleep until renewal
        if sleep:
            time.sleep(tcex.token.sleep_interval + 1)

        r = tcex.session.get('/v2/owners')
        if not r.ok:
            raise RuntimeError('API call failed {}'.format(r.text))

        if register_thread:
            tcex.token.unregister_thread(key, self.thread_name)
