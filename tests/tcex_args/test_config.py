# -*- coding: utf-8 -*-
"""Test the TcEx Args Config Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestArgsConfig:
    """Test TcEx Args Config."""

    @staticmethod
    def test_address_get():
        """Test address creation"""
        assert tcex.args.api_access_id
        assert tcex.args.api_secret_key
        assert tcex.args.api_default_org == 'TCI'
