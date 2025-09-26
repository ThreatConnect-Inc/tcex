"""TestStreamHandler for TcEx Logger Stream Handler Module Testing.

This module contains comprehensive test cases for the TcEx Logger Stream Handler Module,
specifically testing the stream handler functionality that manages console and stream-based
logging including handler addition, removal, and level configuration.

Classes:
    TestStreamHandler: Test class for TcEx Logger Stream Handler Module functionality

TcEx Module Tested: logger.logger
"""


import pytest


from tcex import TcEx


@pytest.mark.run(order=1)
class TestStreamHandler:
    """TestStreamHandler for TcEx Logger Stream Handler Module Testing.

    This class provides comprehensive testing for the TcEx Logger Stream Handler Module, covering
    various stream handler scenarios including handler creation, configuration, and cleanup
    operations for console and stream-based logging.
    """

    @staticmethod
    def test_stream_handler(tcex: TcEx) -> None:
        """Test Stream Handler Management for TcEx Logger Stream Handler Module.

        This test case verifies that the stream handler can be properly added and removed
        from the logger system by creating a named handler, configuring its log level,
        and then cleaning it up, ensuring proper handler lifecycle management.

        Fixtures:
            tcex: TcEx instance with logger configured
        """
        handler_name = 'pytest-sh'
        tcex.logger.add_stream_handler(name=handler_name, level='trace')
        tcex.logger.remove_handler_by_name(handler_name)
