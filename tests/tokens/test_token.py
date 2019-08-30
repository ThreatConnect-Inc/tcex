# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
import os
import threading
import time

from ..tcex_init import tcex

# define thread logfile
logfile = os.path.join('pytest', 'pytest.log')


class TestLogs:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @property
    def thread_name(self):
        """Return the current thread name."""
        return threading.current_thread().name

    @staticmethod
    def test_invalid_register_token():
        """Test invalid token data."""
        # test register_token() [if token is None or expires is None:]
        try:
            tcex.token.register_token('dummy-key', None, None)
        except RuntimeError:
            assert True

    @staticmethod
    def test_invalid_unregister_token():
        """Test invalid token data."""
        tcex.token.unregister_token('zzzzzz')  # hit except on unregister_token()

    def test_expired_token(self):
        """Test thread file handler."""
        token_key = '666'
        tcex.token.register_token(
            key=token_key,
            token='4:146:-1:-1:1564808228:otlhb:NA:Zb3jqAAgLcKJi1JJglpwJaPY4D8hVSv/aZ1rdwtZMnU=',
            expires=int(time.time()) - 999,  # expire token immediately
        )

        # create a thread to test register_thread
        t = threading.Thread(
            name='pytest-token-fail', target=self.token_thread_fail, args=(token_key,)
        )
        t.start()
        t.join()

        tcex.token.unregister_token(token_key)
        tcex.token.unregister_token('dummy-key')  # hit except on unregister_token()

    def test_token_thread_with_renewal(self, tc_service_token):
        """Test thread file handler."""
        # get token from fixture
        tc_token = tc_service_token
        tc_token_expires = int(time.time()) - 999  # expire token immediately

        token_key = '1234'
        tcex.token.register_token(key=token_key, token=tc_token, expires=tc_token_expires)

        # create a thread to test register_thread
        t = threading.Thread(
            name='pytest-token-pass', target=self.token_thread_pass, args=(token_key,)
        )
        t.start()
        t.join()

        tcex.token.unregister_token(token_key)

    def test_register_token_thread_as_key(self, tc_service_token):
        """Test thread file handler."""
        # get token from fixture
        tc_token = tc_service_token
        tc_token_expires = int(time.time()) + 999

        token_key = 'thread-as-key'
        tcex.token.register_token(key=token_key, token=tc_token, expires=tc_token_expires)

        # create a thread to test register_thread
        t = threading.Thread(
            name=token_key, target=self.token_thread_pass, args=(token_key, False, False)
        )
        t.start()
        t.join()

        tcex.token.unregister_token(token_key)

    def test_register_token_fail(self, tc_service_token):
        """Test thread file handler."""
        # get token from fixture
        tc_token = tc_service_token
        tc_token_expires = int(time.time()) - 999

        token_key = 'thread-as-key'
        tcex.token.register_token(key=token_key, token=tc_token, expires=tc_token_expires)

        # create a thread to test register_thread
        t = threading.Thread(
            name=token_key, target=self.token_thread_pass, args=(token_key, False, False)
        )
        t.start()
        t.join()

        tcex.token.unregister_token(token_key)

    def token_thread_fail(self, key):
        """Method to test token failure."""
        tcex.token.register_thread(key, self.thread_name)

        # sleep until token renewal
        time.sleep(tcex.token.sleep_interval + 1)

        try:
            tcex.session.get('/v2/owners')
        except RuntimeError:
            assert True

        tcex.token.unregister_thread(key, self.thread_name)

    def token_thread_pass(self, key, sleep=True, register_thread=True):
        """Method to ensure token is valid."""
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

    @staticmethod
    def test_token_setter():
        """Testing token setters."""
        tcex.token.token = os.getenv('TC_TOKEN')
        tcex.token.token_expires = os.getenv('TC_TOKEN_EXPIRES')

        try:
            r = tcex.session.get('/v2/owners')
            assert r.status_code == 200
        except RuntimeError:
            assert False
