# -*- coding: utf-8 -*-
"""Test the TcEx Logging Module."""


class TestApiHandler:
    """Test the TcEx API Handler Module."""

    @staticmethod
    def test_api_handler(playbook_app):
        """Test TcEx API Handler logger

        Args:
            playbook_app (callable, fixture): The playbook_app fixture for access to MockApp.
        """
        tcex = playbook_app(config_data={'tc_log_to_api': True}).tcex

        for _ in range(0, 20):
            tcex.log.trace('TRACE LOGGING')
            tcex.log.debug('DEBUG LOGGING')
            tcex.log.info('INFO LOGGING')
            tcex.log.warning('WARNING LOGGING')
            tcex.log.error('ERROR LOGGING')
