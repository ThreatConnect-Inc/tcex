# -*- coding: utf-8 -*-
"""Test the TcEx Logger Module."""
import os


class TestLogs:
    """Test the TcEx Logger Module."""

    @staticmethod
    def test_logger(tcex_proxy):
        """Test TcEx logger

        Args:
            tcex_proxy (TcEx, fixture): An instantiated instance of TcEx object.
        """
        tcex = tcex_proxy
        for _ in range(0, 20):
            tcex.log.trace('TRACE LOGGING')
            tcex.log.debug('DEBUG LOGGING')
            tcex.log.info('INFO LOGGING')
            tcex.log.warning('WARNING LOGGING')
            tcex.log.error('ERROR LOGGING')

        # update handler log level
        tcex.logger.update_handler_level(None)
        tcex.logger.update_handler_level('trace')

        # simple assert to ensure the log file was created
        assert os.path.exists(
            os.path.join(tcex.default_args.tc_log_path, tcex.default_args.tc_log_file)
        )
