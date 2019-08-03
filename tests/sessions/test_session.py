# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
from tcex import TcEx
from ..tcex_init import tcex, config_data


# pylint: disable=R0201,W0201
class TestUtils:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    def test_token_auth(self):
        """Test token renewal"""
        r = tcex.session.get('/v2/owners')

        assert r.status_code == 200

    def test_no_valid_credentials(self):
        """Testing initializing tcex with no credentials."""
        hmac_config_data = dict(config_data)
        del hmac_config_data['tc_token']
        del hmac_config_data['tc_token_expires']
        hmac_tcex = TcEx()
        hmac_tcex.tcex_args.config(hmac_config_data)
        hmac_tcex.args  # pylint: disable=pointless-statement
        r = hmac_tcex.session.get('/v2/owners')

        assert r.status_code == 200
