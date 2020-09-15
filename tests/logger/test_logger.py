"""Test the TcEx Logger Module."""
# standard library
import os
from random import randint


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

    @staticmethod
    def test_logger_rotate(playbook_app):
        """Test TcEx logger

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        config_data = {'tc_log_file': 'rotate.log', 'tc_log_max_bytes': 1_048_576}
        tcex = playbook_app(config_data=config_data).tcex

        for _ in range(0, 5_000):
            tcex.log.info(f'A long random string {tcex.utils.random_string(randint(200, 250))}')

        # simple assert to ensure the log file was created
        assert os.path.exists(
            os.path.join(tcex.default_args.tc_log_path, tcex.default_args.tc_log_file)
        )
        assert os.path.exists(
            os.path.join(tcex.default_args.tc_log_path, f'{tcex.default_args.tc_log_file}.1.gz')
        )
