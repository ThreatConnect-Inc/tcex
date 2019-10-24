# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""


# pylint: disable=R0201,W0201
class TestUtils:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @staticmethod
    def test_session_external(tcex):
        """Test token renewal"""
        r = tcex.session_external.get('https://www.google.com')
        assert tcex.session_external.proxies == {}
        assert r.status_code == 200

    @staticmethod
    def test_session_external_proxy(tcex_proxy_external):
        """Test token renewal"""
        r = tcex_proxy_external.session_external.get('https://www.google.com', verify=False)
        assert tcex_proxy_external.session_external.proxies is not None
        assert r.status_code == 200
