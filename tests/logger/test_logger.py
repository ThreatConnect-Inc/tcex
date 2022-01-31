"""Test Module"""
# standard library
import logging
import os
from random import randint
from typing import TYPE_CHECKING

# third-party
import pytest

if TYPE_CHECKING:
    # first-party
    from tcex import TcEx
    from tests.mock_app import MockApp


@pytest.mark.run(order=1)
@pytest.mark.xdist_group(name='logging-tests')
class TestLogs:
    """Test Module"""

    @staticmethod
    def test_logger_level(tcex: 'TcEx', caplog: 'pytest.LogCaptureFixture'):
        """Test Case"""
        trace_logging_message = 'TRACE LOGGING'
        debug_logging_message = 'DEBUG LOGGING'
        info_logging_message = 'INFO LOGGING'
        warning_logging_message = 'WARNING LOGGING'
        error_logging_message = 'ERROR LOGGING'
        for _ in range(0, 5):
            tcex.log.trace(trace_logging_message)
            tcex.log.debug(debug_logging_message)
            tcex.log.info(info_logging_message)
            tcex.log.warning(warning_logging_message)
            tcex.log.error(error_logging_message)

        # simple assert to ensure the log file was created
        assert os.path.exists(
            os.path.join(tcex.inputs.model.tc_log_path, tcex.inputs.model.tc_log_file)
        )
        assert trace_logging_message in caplog.text
        assert debug_logging_message in caplog.text
        assert info_logging_message in caplog.text
        assert warning_logging_message in caplog.text
        assert error_logging_message in caplog.text

        # update handler log level and ensure log event is not logged
        caplog.clear()
        tcex.log.level = logging.INFO
        log_msg = 'LOGGING TRACE AT INFO'
        tcex.log.trace(log_msg)
        assert log_msg not in caplog.text

        tcex.logger.update_handler_level('trace')

    @staticmethod
    def test_logger_rotate(playbook_app: 'MockApp'):
        """Test Case"""
        config_data = {'tc_log_file': 'rotate.log', 'tc_log_max_bytes': 100_048}
        tcex = playbook_app(config_data=config_data).tcex

        for _ in range(0, 500):
            tcex.log.info(f'A long random string {tcex.utils.random_string(randint(200, 250))}')

        # simple assert to ensure the log file was created
        assert os.path.exists(
            os.path.join(tcex.inputs.model.tc_log_path, tcex.inputs.model.tc_log_file)
        )
        assert os.path.exists(
            os.path.join(tcex.inputs.model.tc_log_path, f'{tcex.inputs.model.tc_log_file}.1.gz')
        )
