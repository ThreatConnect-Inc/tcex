"""TcEx Framework Module"""

# standard library
import logging
from collections.abc import Callable

# third-party
import pytest

# first-party
from tests.mock_app import MockApp


@pytest.mark.run(order=1)
class TestApiHandler:
    """Test Module"""

    @staticmethod
    def test_api_handler(playbook_app: Callable[..., MockApp], caplog: pytest.LogCaptureFixture):
        """Test Case"""
        tcex = playbook_app(config_data={'tc_log_to_api': True}).tcex

        # TRACE level is 5 (custom level below DEBUG)
        with caplog.at_level(5):
            for _ in range(0, 20):
                tcex.log.trace('TRACE LOGGING')
                tcex.log.debug('DEBUG LOGGING')
                tcex.log.info('INFO LOGGING')
                tcex.log.warning('WARNING LOGGING')
                tcex.log.error('ERROR LOGGING')

        # validate log messages were captured
        assert 'TRACE LOGGING' in caplog.text
        assert 'DEBUG LOGGING' in caplog.text
        assert 'INFO LOGGING' in caplog.text
        assert 'WARNING LOGGING' in caplog.text
        assert 'ERROR LOGGING' in caplog.text

        # validate expected count (20 iterations * 5 log levels = 100 records)
        assert len(caplog.records) >= 100

        # validate log levels are present
        assert any(record.levelno == logging.DEBUG for record in caplog.records)
        assert any(record.levelno == logging.INFO for record in caplog.records)
        assert any(record.levelno == logging.WARNING for record in caplog.records)
        assert any(record.levelno == logging.ERROR for record in caplog.records)
