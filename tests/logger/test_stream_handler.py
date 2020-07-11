# -*- coding: utf-8 -*-
"""Test the TcEx Logger Module."""


class TestStreamHandler:
    """Test the TcEx Stream Handler Module."""

    @staticmethod
    def test_stream_handler(tcex):
        """Test TcEx API Handler logger

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        handler_name = 'pytest-sh'
        tcex.logger.add_stream_handler(name=handler_name, level='trace')
        tcex.logger.remove_handler_by_name(handler_name)
