"""Test Module"""
# standard library
from collections.abc import Callable

# third-party
import pytest

# first-party
from tests.mock_app import MockApp


@pytest.mark.run(order=1)
class TestApiHandler:
    """Test Module"""

    @staticmethod
    def test_api_handler(playbook_app: Callable[..., MockApp]):
        """Test Case"""
        tcex = playbook_app(config_data={'tc_log_to_api': True}).tcex

        for _ in range(0, 20):
            tcex.log.trace('TRACE LOGGING')
            tcex.log.debug('DEBUG LOGGING')
            tcex.log.info('INFO LOGGING')
            tcex.log.warning('WARNING LOGGING')
            tcex.log.error('ERROR LOGGING')
