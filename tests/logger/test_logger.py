"""TcEx Framework Module"""

# standard library
import os
from collections.abc import Callable
from random import randint

# third-party
import pytest

# first-party
from tcex import TcEx
from tests.mock_app import MockApp


@pytest.mark.run(order=1)
class TestLogs:
    """Test Module"""

    @staticmethod
    def test_logger_level(tcex: TcEx, caplog: pytest.LogCaptureFixture):
        """Test Case"""
        trace_logging_message = 'STD TRACE LOGGING'
        debug_logging_message = 'STD DEBUG LOGGING'
        info_logging_message = 'STD INFO LOGGING'
        warning_logging_message = 'STD WARNING LOGGING'
        error_logging_message = 'STD ERROR LOGGING'
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

    @staticmethod
    def test_logger_rotate(playbook_app: Callable[..., MockApp]):
        """Test Case"""
        config_data = {'tc_log_file': 'rotate.log', 'tc_log_max_bytes': 100_048}
        tcex = playbook_app(config_data=config_data).tcex

        for _ in range(0, 500):
            tcex.log.info(f'A long random string {tcex.util.random_string(randint(200, 250))}')

        # simple assert to ensure the log file was created
        assert os.path.exists(
            os.path.join(tcex.inputs.model.tc_log_path, tcex.inputs.model.tc_log_file)
        )
        assert os.path.exists(
            os.path.join(tcex.inputs.model.tc_log_path, f'{tcex.inputs.model.tc_log_file}.1.gz')
        )
