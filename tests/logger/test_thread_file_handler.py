# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
import os
import threading


class TestApiHandler:
    """Test the TcEx API Handler Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    def logging_thread(self, logfile, tcex):  # pylint: disable=no-self-use
        """Thread to test logging."""
        logfile = logfile.replace('.log', '-thread.log')
        tcex.logger.add_thread_file_handler(
            name='pytest', filename=logfile, level='trace', path=tcex.default_args.tc_log_path
        )

        for _ in range(0, 20):
            tcex.log.trace('THREAD TRACE LOGGING')
            tcex.log.debug('THREAD DEBUG LOGGING')
            tcex.log.info('THREAD INFO LOGGING')
            tcex.log.warning('THREAD WARNING LOGGING')
            tcex.log.error('THREAD ERROR LOGGING')

        tcex.logger.remove_handler_by_name(handler_name='pytest')

    def test_thread_file_handler(self, tc_log_file, tcex):
        """Test thread file handler."""
        t = threading.Thread(name='pytest', target=self.logging_thread, args=(tc_log_file, tcex))
        t.start()
        t.join()

        # simple assert to ensure the log file was created
        assert os.path.exists(os.path.join(tcex.default_args.tc_log_path, tc_log_file))
