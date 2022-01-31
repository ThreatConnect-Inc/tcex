"""Test Module"""
# standard library
import os
import threading
import time
from typing import TYPE_CHECKING

# third-party
import pytest

if TYPE_CHECKING:
    # first-party
    from tcex import TcEx


@pytest.mark.run(order=1)
@pytest.mark.xdist_group(name='logging-tests')
class TestThreadFileHandler:
    """Test Module"""

    @staticmethod
    def logging_thread(logfile: str, tcex: 'TcEx'):
        """Test Case"""
        tcex.logger.add_thread_file_handler(
            name='pytest',
            filename=logfile,
            level='trace',
            path=tcex.inputs.model.tc_log_path,
            thread_key='tester',
        )

        for _ in range(0, 20):
            tcex.log.trace('THREAD TRACE LOGGING')
            tcex.log.debug('THREAD DEBUG LOGGING')
            tcex.log.info('THREAD INFO LOGGING')
            tcex.log.warning('THREAD WARNING LOGGING')
            tcex.log.error('THREAD ERROR LOGGING')

        tcex.logger.remove_handler_by_name(handler_name='pytest')

    def test_thread_file_handler(self, tcex: 'TcEx'):
        """Test Case"""
        logfile = tcex.inputs.model.tc_log_file.replace('.log', '-thread.log')
        t = threading.Thread(name='pytest', target=self.logging_thread, args=(logfile, tcex))

        time.sleep(2)
        t.start()
        t.join()

        # simple assert to ensure the log file was created
        assert os.path.exists(os.path.join(tcex.inputs.model.tc_log_path, logfile))
