# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
import os
import threading

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

    def logging_thread(self, tcex):  # pylint: disable=no-self-use
        """Thread to test logging."""
        tcex.logger.add_thread_file_handler(
            name='pytest', filename=logfile, level='trace', path=tcex.default_args.tc_log_path
        )

        tcex.log.trace('THREAD TRACE LOGGING')
        tcex.log.debug('THREAD DEBUG LOGGING')
        tcex.log.info('THREAD INFO LOGGING')
        tcex.log.warning('THREAD WARNING LOGGING')
        tcex.log.error('THREAD ERROR LOGGING')

        tcex.logger.remove_handler_by_name(handler_name='pytest')

    def test_thread_file_handler(self, tc_log_file, tcex):
        """Test thread file handler."""
        t = threading.Thread(name='pytest', target=self.logging_thread)
        t.start()
        t.join()

        # simple assert to ensure the log file was created
        assert os.path.exists(os.path.join(tcex.default_args.tc_log_path, tc_log_file))
