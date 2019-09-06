# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
from tcex import TcEx


class TestApiHandler:
    """Test the TcEx API Handler Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @staticmethod
    def test_stream_handler(config_data):  # pylint: disable=no-self-use
        """Test API logging handler"""
        tcex = TcEx(config=config_data)
        handler_name = 'pytest-sh'
        tcex.logger.add_stream_handler(name=handler_name, level='trace')
        tcex.logger.remove_handler_by_name(handler_name)
