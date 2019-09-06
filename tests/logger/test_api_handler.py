# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
from tcex import TcEx


class TestApiHandler:
    """Test the TcEx API Handler Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    def test_api_handler(self, config_data):  # pylint: disable=no-self-use
        """Test API logging handler"""
        config_data['tc_log_to_api'] = True
        tcex = TcEx(config=config_data)

        for _ in range(0, 20):
            tcex.log.trace('TRACE LOGGING')
            tcex.log.debug('DEBUG LOGGING')
            tcex.log.info('INFO LOGGING')
            tcex.log.warning('WARNING LOGGING')
            tcex.log.error('ERROR LOGGING')
