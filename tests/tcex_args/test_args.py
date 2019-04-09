# -*- coding: utf-8 -*-
"""Test the TcEx Args Config Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestArgsConfig:
    """Test TcEx Args Config."""

    @staticmethod
    def test_address_get():
        """Test args."""
        assert tcex.args.tc_token
        assert tcex.args.tc_token_expires
        assert tcex.args.api_default_org == 'TCI'
