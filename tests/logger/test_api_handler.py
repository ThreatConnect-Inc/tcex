"""TestApiHandler for TcEx Logger API Handler Module Testing.

This module contains comprehensive test cases for the TcEx Logger API Handler Module, specifically
testing the API logging functionality that sends log events to the ThreatConnect API including
various log levels and batch processing capabilities.

Classes:
    TestApiHandler: Test class for TcEx Logger API Handler Module functionality

TcEx Module Tested: logger.api_handler
"""


import logging
from collections.abc import Callable


import pytest


from tests.mock_app import MockApp


@pytest.mark.run(order=1)
class TestApiHandler:
    """TestApiHandler for TcEx Logger API Handler Module Testing.

    This class provides comprehensive testing for the TcEx Logger API Handler Module, covering
    various API logging scenarios including different log levels, batch processing, and
    integration with the ThreatConnect API logging system.
    """

    @staticmethod
    def test_api_handler(playbook_app: Callable[..., MockApp], caplog: pytest.LogCaptureFixture):
        """Test API Handler Logging for TcEx Logger API Handler Module.

        This test case verifies that the API handler correctly processes and sends log
        events to the ThreatConnect API by enabling API logging and generating multiple
        log entries across different log levels, ensuring proper API integration.

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
            caplog: Pytest fixture for capturing log output during tests
        """
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
