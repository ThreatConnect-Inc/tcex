"""TcEx Framework Module"""

# standard library
import logging
import os
import sys
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Literal, NoReturn

# first-party
from tcex.app.config import InstallJson
from tcex.logger.trace_logger import TraceLogger
from tcex.registry import registry

if TYPE_CHECKING:
    # first-party
    from tcex.input.input import Input  # CIRCULAR-IMPORT


# get tcex logger
_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


EXIT_CODES = Literal[0, 1, 3, 4]


class ExitCode(int, Enum):
    """Valid exit codes for a ThreatConnect app.

    Note not all exit codes are valid for all app types:
    partial failure is not valid for playbook apps.
    """

    SUCCESS = 0
    FAILURE = 1
    PARTIAL_FAILURE = 3
    HARD_FAILURE = 4

    def __str__(self):
        """@cblades"""
        clean_name = self.name.replace('_', ' ').title()
        return f'{self.value} ({clean_name})'


class Exit:
    """Provides functionality around exiting an app."""

    def __init__(self, inputs: 'Input'):
        """Initialize instance properties."""
        self.ij = InstallJson()
        self.inputs = inputs

        # properties
        self._exit_code = ExitCode.SUCCESS
        self._message = None
        self.log = _logger

    def _exit(self, code: ExitCode | int, msg: str) -> NoReturn:
        """Exit the App"""
        code = ExitCode(code) if code is not None else self.code

        # handle exit msg logging
        self._exit_msg_handler(code, msg)

        self.log.info(f'exit-code={code}')
        sys.exit(code.value)

    def _message_tc(self, message: str, max_length: int = 255):
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

        if os.access(self.inputs.model_tc.tc_out_path, os.W_OK):
            message_file = self.inputs.model_tc.tc_out_path / 'message.tc'
        else:
            message_file = Path('message.tc')

        if not message.endswith('\n'):
            message += '\n'
        with message_file.open('w') as mh:
            # write last <max_length> characters to file
            mh.write(message[-max_length:])

    @property
    def code(self) -> ExitCode:
        """Get exit code."""
        return self._exit_code

    @code.setter
    def code(self, exit_code: ExitCode | int):
        """Set exit code.

        Will automatically change partial failure to success if app is a playbook app.

        Args:
            exit_code: the new exit code.
        """
        exit_code = ExitCode(exit_code)
        if exit_code == ExitCode.PARTIAL_FAILURE and self.ij.model.is_playbook_app:
            self.log.info(
                f'Changing exit code from {ExitCode.PARTIAL_FAILURE} '
                f'to {ExitCode.SUCCESS} for Playbook App.'
            )
            exit_code = ExitCode.SUCCESS
        self._exit_code = exit_code

    def exit(self, code: ExitCode | int | None = None, msg: str | None = None) -> NoReturn:
        """Application exit method with proper exit code

        The method will run the Python standard sys.exit() with the exit code
        previously defined via :py:meth:`~tcex.tcex.TcEx.exit_code` or provided
        during the call of this method.

        Args:
            code: The exit code value for the app.
            msg: A message to log and add to message tc output.
        """
        code = ExitCode(code) if code is not None else self.code
        msg = msg if msg is not None else ''

        # playbook exit handler
        if self.ij.model.is_playbook_app:
            self.exit_playbook_handler(msg)

        # exit token renewal thread
        if not self.ij.is_external_app:
            registry.token.shutdown = True

        # exit
        self._exit(code, msg)

    def _exit_msg_handler(self, code: ExitCode, msg: str):
        """Handle exit message. Write to both log and message_tc."""
        if msg is not None:
            log_msg = msg.replace('\n', ',')
            if code in [ExitCode.SUCCESS, ExitCode.PARTIAL_FAILURE]:
                self.log.info(f'exit-message="{log_msg}"')
            else:
                self.log.error(f'exit-message="{log_msg}"')
            self._message_tc(msg)

    def exit_playbook_handler(self, msg: str):
        """Perform special action for PB Apps before exit."""
        # write outputs before exiting
        registry.playbook.output.process()  # pylint: disable=no-member

        # required only for tcex testing framework
        if (
            hasattr(self.inputs.model_tc, 'tcex_testing_context')
            and self.inputs.model_tc.tcex_testing_context is not None
        ):  # pragma: no cover
            registry.redis_client.hset(  # pylint: disable=no-member
                self.inputs.model_tc.tcex_testing_context, '_exit_message', msg
            )

    @property
    def message(self) -> str:
        """Get exit code."""
        return self._message or ''

    @message.setter
    def message(self, message: str):
        """Set exit message."""
        self._message = message
