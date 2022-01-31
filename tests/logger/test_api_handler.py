"""Test Module"""
# standard library
from typing import TYPE_CHECKING

# third-party
import pytest

if TYPE_CHECKING:
    # first-party
    from tests.mock_app import MockApp


@pytest.mark.run(order=1)
@pytest.mark.xdist_group(name='logging-tests')
class TestApiHandler:
    """Test Module"""

    @staticmethod
    def test_api_handler(playbook_app: 'MockApp'):
        """Test Case"""
        tcex = playbook_app(config_data={'tc_log_to_api': True}).tcex

        for _ in range(0, 20):
            tcex.log.trace('TRACE LOGGING')
            tcex.log.debug('DEBUG LOGGING')
            tcex.log.info('INFO LOGGING')
            tcex.log.warning('WARNING LOGGING')
            tcex.log.error('ERROR LOGGING')
