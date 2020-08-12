# -*- coding: utf-8 -*-
"""Test the TcEx Session Module."""


class TestUtils:
    """Test the TcEx Session Module."""

    @staticmethod
    def test_session_external(tcex):
        """Test tc.session_external property.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        r = tcex.session_external.get('https://www.google.com')
        assert tcex.session_external.proxies == {}
        assert r.status_code == 200

    @staticmethod
    def test_session_external_base_url(tcex):
        """Test tc.session_external property.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        session = tcex.session_external
        session.base_url = 'https://www.google.com'
        session.mask_headers = False
        r = session.get('/')
        assert tcex.session_external.proxies == {}
        assert r.status_code == 200

    @staticmethod
    def test_session_external_mask_headers(tcex):
        """Test tc.session_external property.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        session = tcex.session_external
        session.base_url = 'https://www.google.com'
        session.mask_headers = True
        session.mask_patterns = ['user']
        r = session.get('/')
        assert tcex.session_external.proxies == {}
        assert r.status_code == 200

    @staticmethod
    def test_session_external_proxy(tcex_proxy):
        """Test tc.session_external property with proxy.

        Args:
            tcex_proxy (TcEx, fixture): An instantiated instance of TcEx object.
        """
        r = tcex_proxy.session_external.get('https://www.google.com', verify=False)
        assert tcex_proxy.session_external.proxies is not None
        assert r.status_code == 200
