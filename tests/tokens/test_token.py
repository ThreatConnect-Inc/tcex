# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
# standard library
import threading
import time


class TestToken:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @property
    def thread_name(self):
        """Return the current thread name."""
        return threading.current_thread().name

    def test_expired_token(self, service_app):
        """Test registering an expired token???

        Args:
            service_app (MockApp, fixture): An instantiated instance of MockApp.
        """
        # get clean instance of tcex
        tcex = service_app().tcex

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
    def test_invalid_register_token(service_app):
        """Test invalid token register.

        Args:
            service_app (MockApp, fixture): An instantiated instance of MockApp.
        """
        # coverage: test register_token() [if token is None or expires is None:]
        try:
            service_app().tcex.token.register_token('dummy-key', None, None)
            assert True
        except RuntimeError:
            assert False

    @staticmethod
    def test_invalid_unregister_token(service_app):
        """Test invalid token register.

        Args:
            service_app (MockApp, fixture): An instantiated instance of MockApp.
        """
        # coverage: hit except on unregister_token()
        service_app().tcex.token.unregister_token('zzzzzz')

    def test_register_token_fail(self, service_app):
        """Test failing a token registation.

        Args:
            service_app (MockApp, fixture): An instantiated instance of MockApp.
        """
        # get clean instance of tcex
        tcex = service_app().tcex

        # get token from fixture
        tc_token = service_app().service_token
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

    def test_register_token_thread_as_key(self, service_app):
        """Test register of token in a thread as a key.

        Args:
            service_app (MockApp, fixture): An instantiated instance of MockApp.
        """
        # get clean instance of tcex
        tcex = service_app().tcex

        # get token from fixture
        tc_token = service_app().service_token
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
        tcex.token.shutdown = True  # coverage

    @staticmethod
    def test_token_setter(service_app):
        """Test register of token in a thread as a key.

        Args:
            service_app (MockApp, fixture): An instantiated instance of MockApp.
        """
        # get clean instance of tcex
        tcex = service_app().tcex

        # set token values
        tcex.token.token = service_app().api_token
        tcex.token.token_expires = '1700000000'

        try:
            r = tcex.session.get('/v2/owners')
            assert tcex.token.token_expires == 1700000000  # coverage
            assert r.status_code == 200, f'Failed API call ({r.text})'
        except RuntimeError:
            assert False

    def test_token_thread_with_renewal(self, service_app):
        """Test thread with token renewal.

        Args:
            service_app (MockApp, fixture): An instantiated instance of MockApp.
        """
        # get clean instance of tcex
        tcex = service_app().tcex

        # get token from fixture
        tc_token = service_app().service_token
        tc_token_expires = int(time.time()) - 999  # expire token immediately

        token_key = '1234'
        tcex.token.register_token(key=token_key, token=tc_token, expires=tc_token_expires)

        # create a thread to test register_thread
        t = threading.Thread(
            name='pytest-token-pass',
            target=self.token_thread_pass,
            args=(tcex, token_key),
            kwargs=({'old_token': tc_token}),
        )
        t.start()
        t.join()

        tcex.token.unregister_token(token_key)

    def token_thread_fail(self, tcex, key):
        """Run thread test for expected fail test.

        Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            key (str): The thread key.
        """
        tcex.token.register_thread(key, self.thread_name)

        # sleep until token renewal
        time.sleep(tcex.token.sleep_interval + 1)

        r = tcex.session.get('/v2/owners')
        if r.ok:
            assert False, 'API request passed on a fail test.'

        tcex.token.unregister_thread(key, self.thread_name)

    def token_thread_pass(self, tcex, key, sleep=True, register_thread=True, old_token=None):
        """Run thread test for expected pass test.

        Args:  # coverage
            tcex (TcEx): An instantiated instance of TcEx object.
            key (str): The thread key.
            sleep (bool, optional): If true add sleep interval to wait for token renewal.
            register_thread (bool, optional): If true register the thread. Defaults to True.
            old_token (str, optional): The generated token before renewal. Defaults to None.
        """
        if register_thread:
            tcex.token.register_thread(key, self.thread_name)

        # sleep until renewal
        if sleep:
            time.sleep(tcex.token.sleep_interval + 1)

        r = tcex.session.get('/v2/owners')
        if not r.ok:
            assert False, f'API call failed {r.text}'

        if old_token:
            assert old_token != tcex.token.token

        if register_thread:
            tcex.token.unregister_thread(key, self.thread_name)
