"""Test the TcEx Batch Module."""
# standard library
import os
import threading


class TestApiHandler:
    """Test the TcEx API Handler Module."""

    @staticmethod
    def logging_thread(logfile, tcex):
        """Test thread logging

        Args:
            logfile (str): The logfile name.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
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

    def test_thread_file_handler(self, tcex):
        """Test thread logging

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        logfile = tcex.default_args.tc_log_file.replace('.log', '-thread.log')
        t = threading.Thread(name='pytest', target=self.logging_thread, args=(logfile, tcex))
        # standard library
        import time

        time.sleep(5)
        t.start()
        t.join()

        # simple assert to ensure the log file was created
        assert os.path.exists(os.path.join(tcex.default_args.tc_log_path, logfile))
