"""TcEx Exit Module"""
# standard library
import logging
import os
import sys
from enum import Enum
from typing import TYPE_CHECKING, Optional, Union

# first-party
from tcex.app_config import InstallJson
from tcex.pleb.registry import registry

if TYPE_CHECKING:
    # third-party
    from redis import Redis

    # first-party
    from tcex.playbook.playbook import Playbook
    from tcex.tokens import Tokens

# get tcex logger
logger = logging.getLogger('tcex')


class ExitCode(Enum):
    """Valid exit codes for a ThreatConnect app.

    Note not all exit codes are valid for all app types: partial failure is not valid for playbook
    apps.
    """

    SUCCESS = 0
    FAILURE = 1
    PARTIAL_FAILURE = 3

    def __str__(self):
        """@cblades"""
        clean_name = self.name.replace('_', ' ').title()
        return f'{self.value} ({clean_name})'


class ExitService:
    """Provides functionality around exiting an app."""

    def __init__(
        self,
        pre_run_inputs
    ):
        """."""
        self.ij = InstallJson()
        self.pre_run_inputs = pre_run_inputs


        self._exit_code = ExitCode.SUCCESS

    @property
    def exit_code(self) -> ExitCode:
        """Get exit code."""
        return self._exit_code

    @exit_code.setter
    def exit_code(self, exit_code: Union[ExitCode, int]):
        """Set exit code.

        Will automatically change partial failure to success if app is a playbook app.

        Args:
            exit_code: the new exit code.
        """
        exit_code = ExitCode(exit_code)
        if (
            exit_code == ExitCode.PARTIAL_FAILURE
            and self.ij.model.runtime_level.lower() == 'playbook'
        ):
            logger.info(
                f'Changing exit code from {ExitCode.PARTIAL_FAILURE} '
                f'to {ExitCode.SUCCESS} for Playbook App.'
            )
            exit_code = ExitCode.SUCCESS
        self._exit_code = exit_code

    def exit(self, code: Optional[Union[ExitCode, int]] = None, msg: Optional[str] = None) -> None:
        """Application exit method with proper exit code

        The method will run the Python standard sys.exit() with the exit code
        previously defined via :py:meth:`~tcex.tcex.TcEx.exit_code` or provided
        during the call of this method.

        Args:
            code: The exit code value for the app.
            msg: A message to log and add to message tc output.
        """
        code = ExitCode(code) if code is not None else self.exit_code
        # handle exit msg logging
        self._exit_msg_handler(code, msg)

        # aot notify
        if ('tc_aot_enabled' in self.pre_run_inputs
                and self.pre_run_inputs.get('tc_aot_enabled')):
            # push exit message
            self._aot_rpush(code.value)

        # exit token renewal thread
        registry.token.shutdown = True

        logger.info(f'Exit Code: {code}')
        sys.exit(code.value)

    def exit_aot_terminate(self, code: Optional[Union[ExitCode, int]] = None,
                 msg: Optional[str] = None) -> None:
        """Application exit method with proper exit code only for AOT.

        The method will run the Python standard sys.exit() with the exit code
        previously defined via :py:meth:`~tcex.tcex.TcEx.exit_code` or provided
        during the call of this method.

        Args:
            code: The exit code value for the app.
            msg: A message to log and add to message tc output.
        """
        code = ExitCode(code) if code is not None else self.exit_code

        # aot notify
        if ('tc_aot_enabled' in self.pre_run_inputs
                and self.pre_run_inputs.get('tc_aot_enabled')):
            # push exit message
            self._aot_rpush(code.value)

        logger.info(f'Exit Code: {code}')
        sys.exit(code.value)

    def _exit_msg_handler(self, code: ExitCode, msg: str) -> None:
        """Handle exit message. Write to both log and message_tc."""
        if msg is not None:
            if code in [ExitCode.SUCCESS, ExitCode.PARTIAL_FAILURE]:
                logger.info(msg)
            else:
                logger.error(msg)
            self._message_tc(msg)

    def _aot_rpush(self, exit_code: int) -> None:
        """Push message to AOT action channel."""
        if self.pre_run_inputs.get('tc_playbook_db_type') == 'Redis':
            try:
                # pylint: disable=no-member
                registry.redis.rpush(self.pre_run_inputs.get('tc_exit_channel'), exit_code)
            except Exception as e:  # pragma: no cover
                self.exit(ExitCode.FAILURE, f'Exception during AOT exit push ({e}).')

    def _message_tc(self, message: str, max_length: Optional[int] = 255) -> None:
        """Write data to message_tc file in TcEX specified directory.

        This method is used to set and exit message in the ThreatConnect Platform.
        ThreatConnect only supports files of max_message_length.  Any data exceeding
        this limit will be truncated. The last <max_length> characters will be preserved.

        Args:
            message: The message to add to message_tc file
            max_length: The maximum length of an exit message. Defaults to 255.
        """
        if not isinstance(message, str):
            message = str(message)

        if os.access(self.pre_run_inputs.get('tc_out_path'), os.W_OK):
            message_file = os.path.join(self.pre_run_inputs.get('tc_out_path'), 'message.tc')
        else:
            message_file = 'message.tc'

        if os.path.isfile(message_file):
            with open(message_file) as mh:
                message = mh.read() + message

        if not message.endswith('\n'):
            message += '\n'
        with open(message_file, 'w') as mh:
            # write last <max_length> characters to file
            mh.write(message[-max_length:])
