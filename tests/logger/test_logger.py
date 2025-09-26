"""TestLogger for TcEx Logger Module Testing.

This module contains comprehensive test cases for the TcEx Logger Module, specifically testing
the main logging functionality including log levels, log rotation, file handling, and various
logging scenarios across different configurations and environments.

Classes:
    TestLogger: Test class for TcEx Logger Module functionality

TcEx Module Tested: logger.logger
"""


from collections.abc import Callable
from random import randint


import pytest


from tcex import TcEx
from tests.mock_app import MockApp


@pytest.mark.run(order=1)
class TestLogger:
    """TestLogger for TcEx Logger Module Testing.

    This class provides comprehensive testing for the TcEx Logger Module, covering various
    logging scenarios including log level management, log file rotation, file creation,
    and integration with different logging handlers and configurations.
    """

    @staticmethod
    def test_logger_level(tcex: TcEx, caplog: pytest.LogCaptureFixture) -> None:
        """Test Logger Level Management for TcEx Logger Module.

        This test case verifies that the logger correctly handles different log levels
        by generating log messages at various levels and ensuring they are properly
        captured and stored in the log file, validating the complete logging pipeline.

        Fixtures:
            tcex: TcEx instance with logger configured
            caplog: Pytest fixture for capturing log output
        """
        trace_logging_message = 'STD TRACE LOGGING'
        debug_logging_message = 'STD DEBUG LOGGING'
        info_logging_message = 'STD INFO LOGGING'
        warning_logging_message = 'STD WARNING LOGGING'
        error_logging_message = 'STD ERROR LOGGING'
        for _ in range(5):
            tcex.log.trace(trace_logging_message)
            tcex.log.debug(debug_logging_message)
            tcex.log.info(info_logging_message)
            tcex.log.warning(warning_logging_message)
            tcex.log.error(error_logging_message)

        # simple assert to ensure the log file was created
        log_file_path = tcex.inputs.model.tc_log_path / tcex.inputs.model.tc_log_file
        assert log_file_path.exists(), 'Log file was not created'
        assert trace_logging_message in caplog.text, 'Trace logging message not found in caplog'
        assert debug_logging_message in caplog.text, 'Debug logging message not found in caplog'
        assert info_logging_message in caplog.text, 'Info logging message not found in caplog'
        assert warning_logging_message in caplog.text, 'Warning logging message not found in caplog'
        assert error_logging_message in caplog.text, 'Error logging message not found in caplog'

    @staticmethod
    def test_logger_rotate(playbook_app: Callable[..., MockApp]) -> None:
        """Test Logger File Rotation for TcEx Logger Module.

        This test case verifies that the logger correctly handles log file rotation
        by generating enough log content to exceed the maximum file size, ensuring
        that rotation occurs and backup files are created with proper compression.

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        config_data = {'tc_log_file': 'rotate.log', 'tc_log_max_bytes': 100_048}
        tcex = playbook_app(config_data=config_data).tcex

        for _ in range(500):
            tcex.log.info(f'A long random string {tcex.util.random_string(randint(200, 250))}')

        # simple assert to ensure the log file was created
        main_log_path = tcex.inputs.model.tc_log_path / tcex.inputs.model.tc_log_file
        rotated_log_path = (
            tcex.inputs.model.tc_log_path / f'{tcex.inputs.model.tc_log_file}.1.gz'
        )
        assert main_log_path.exists(), 'Main log file was not created'
        assert rotated_log_path.exists(), 'Rotated log file was not created'
