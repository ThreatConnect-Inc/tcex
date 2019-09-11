# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
from tcex import TcEx


# pylint: disable=R0201,W0201
class TestUtils:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @staticmethod
    def test_token_auth(tcex):
        """Test token renewal"""
        r = tcex.session.get('/v2/owners')

        assert r.status_code == 200

    def test_no_valid_credentials(self, config_data):
        """Testing initializing tcex with no credentials."""
        hmac_config_data = dict(config_data)
        del hmac_config_data['tc_token']
        del hmac_config_data['tc_token_expires']

        hmac_tcex = TcEx(config=hmac_config_data)
        hmac_tcex.args  # pylint: disable=pointless-statement
        r = hmac_tcex.session.get('/v2/owners')

        assert r.status_code == 200
