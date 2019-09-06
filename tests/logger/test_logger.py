# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
import os

# define thread logfile
logfile = os.path.join('pytest', 'pytest.log')


class TestLogs:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    def test_logger(self, tc_log_file, tcex):  # pylint: disable=no-self-use
        """Test any to datetime"""
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
        assert os.path.exists(os.path.join(tcex.default_args.tc_log_path, tc_log_file))
