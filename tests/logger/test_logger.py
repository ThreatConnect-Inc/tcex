# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""

from ..tcex_init import tcex


# pylint: disable=R0201,W0201
class TestLogs:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""
        # self.tcex = test()

    def test_any_to_datetime(self):
        """Test any to datetime"""
        tcex.log.trace('TRACE LOGGING')
        tcex.log.debug('DEBUG LOGGING')
        tcex.log.info('INFO LOGGING')
        tcex.log.warning('WARNING LOGGING')
        tcex.log.error('ERROR LOGGING')
