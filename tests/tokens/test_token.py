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

    # def test_token_thread_with_renewal(self, token_data, monkeypatch):
    def test_token_thread_with_renewal(self):
        """Test thread file handler."""
        # get token from fixture
        # tc_token = token_data.get('tc_token')
        # tc_token_expires = token_data.get('tc_token_expires')
        tc_token = '4:146:-1:-1:1564807311:saCMu:NA:OKFubNwzJcKAmWGk1YYfRvTUByEcNBD6jAtheHF443g='
        tc_token_expires = int(time.time()) - 999  # expire token immediately

        token_key = '1234'
        tcex.token.register_token(key=token_key, token=tc_token, expires=tc_token_expires)

        # create a thread to test register_thread
        t = threading.Thread(
            name='pytest-token-pass', target=self.token_thread_pass, args=(token_key, 200)
        )
        t.start()
        t.join()

        tcex.token.unregister_token(token_key)

    def token_thread_fail(self, key):
        """Thread to test logging."""
        tcex.token.register_thread(key, self.thread_name)
        try:
            tcex.session.get('/v2/owners')
        except RuntimeError:
            assert True

        tcex.token.unregister_thread(key, self.thread_name)

    def token_thread_pass(self, key, status_code):
        """Thread to test logging."""
        tcex.token.register_thread(key, self.thread_name)
        try:
            r = tcex.session.get('/v2/owners')
            assert r.status_code == status_code
        except RuntimeError:
            assert False

        tcex.token.unregister_thread(key, self.thread_name)
