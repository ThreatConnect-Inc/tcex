"""TcEx Exit Module"""
# standard library
import logging
import os
import sys
from enum import Enum
from typing import Optional, Union

# first-party
from tcex.app_config import InstallJson
from tcex.pleb.registry import registry

# get tcex logger
logger = logging.getLogger('tcex')


class ExitCode(int, Enum):
    """Valid exit codes for a ThreatConnect app.

    Note not all exit codes are valid for all app types: partial failure is not valid for playbook
    apps.
    """

    SUCCESS = 0
    FAILURE = 1
    PARTIAL_FAILURE = 3
    HARD_FAILURE = 4

    def __str__(self):
        """@cblades"""
        clean_name = self.name.replace('_', ' ').title()
        return f'{self.value} ({clean_name})'


class ExitService:
    """Provides functionality around exiting an app."""

    def __init__(self, inputs):
        """."""
        self.ij = InstallJson()
        self.inputs = inputs

        self._exit_code = ExitCode.SUCCESS

    @property
    def exit_code(self) -> 'ExitCode':
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

    def exit(self, code: Optional[Union[ExitCode, int]] = None, msg: Optional[str] = None):
        """Application exit method with proper exit code

        The method will run the Python standard sys.exit() with the exit code
        previously defined via :py:meth:`~tcex.tcex.TcEx.exit_code` or provided
        during the call of this method.

        Args:
            code: The exit code value for the app.
            msg: A message to log and add to message tc output.
        """
        code = ExitCode(code) if code is not None else self.exit_code

        # playbook exit handler
        if self.ij.model.runtime_level.lower() == 'playbook':
            self.exit_playbook_handler(msg)

        # aot notify
        if 'tc_aot_enabled' in self.inputs.contents and self.inputs.contents.get('tc_aot_enabled'):
            # push exit message
            self._aot_rpush(code.value)

        # exit token renewal thread
        registry.token.shutdown = True

        # exit
        self._exit(code, msg)

    def _exit(self, code: int, msg: str):
        """Exit the App"""
        # handle exit msg logging
        self._exit_msg_handler(code, msg)

        logger.info(f'exit-code={code}')
        sys.exit(code.value)

    # TODO: [med] @cblades - is msg required?
    # pylint: disable=unused-argument
    def exit_aot_terminate(
        self, code: Optional[Union[ExitCode, int]] = None, msg: Optional[str] = None
    ):
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
        if 'tc_aot_enabled' in self.inputs.contents and self.inputs.contents.get('tc_aot_enabled'):
            # push exit message
            self._aot_rpush(code.value)

        logger.info(f'exit-code={code}')
        sys.exit(code)

    def exit_playbook_handler(self, msg: str):
        """Perform special action for PB Apps before exit."""
        # write outputs before exiting
        registry.playbook.output.process()  # pylint: disable=no-member

        # required only for tcex testing framework
        if (
            hasattr(self.inputs.model_unresolved, 'tcex_testing_context')
            and self.inputs.model_unresolved.tcex_testing_context is not None
        ):  # pragma: no cover
            registry.redis_client.hset(  # pylint: disable=no-member
                self.inputs.model_unresolved.tcex_testing_context, '_exit_message', msg
            )

    def _exit_msg_handler(self, code: ExitCode, msg: str):
        """Handle exit message. Write to both log and message_tc."""
        if msg is not None:
            log_msg = msg.replace('\n', ',')
            if code in [ExitCode.SUCCESS, ExitCode.PARTIAL_FAILURE]:
                logger.info(f'exit-message="{log_msg}"')
            else:
                logger.error(f'exit-message="{log_msg}"')
            self._message_tc(msg)

    def _aot_rpush(self, exit_code: int):
        """Push message to AOT action channel."""
        if self.inputs.contents.get('tc_playbook_db_type') == 'Redis':
            try:
                # pylint: disable=no-member
                registry.redis_client.rpush(self.inputs.contents.get('tc_exit_channel'), exit_code)
            except Exception as e:  # pragma: no cover
                self._exit(ExitCode.FAILURE, f'Exception during AOT exit push ({e}).')

    def _message_tc(self, message: str, max_length: Optional[int] = 255):
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

        if os.access(self.inputs.contents.get('tc_out_path'), os.W_OK):
            message_file = os.path.join(self.inputs.contents.get('tc_out_path'), 'message.tc')
        else:
            message_file = 'message.tc'

        if not message.endswith('\n'):
            message += '\n'
        with open(message_file, 'w') as mh:
            # write last <max_length> characters to file
            mh.write(message[-max_length:])
