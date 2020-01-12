# -*- coding: utf-8 -*-
"""Test the TcEx Session Module."""


class TestUtils:
    """Test the TcEx Session Module."""

    @staticmethod
    def test_token_auth(tcex):
        """Test tc.session property

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        r = tcex.session.get('/v2/owners')

        assert r.status_code == 200

    @staticmethod
    def test_no_valid_credentials(tcex_hmac):
        """Test tc.session property

        Args:
            tcex_hmac (TcEx, fixture): An instantiated instance of TcEx object with no token.
        """
        r = tcex_hmac.session.get('/v2/owners')

        assert r.status_code == 200
