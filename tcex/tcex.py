"""TcEx Framework Module"""

# standard library
import inspect
import os
import platform
import signal
import threading
from dataclasses import dataclass

# first-party
from tcex.api.api import API
from tcex.app.app import App
from tcex.exit.exit import Exit, ExitCode
from tcex.input.input import Input
from tcex.logger.logger import Logger
from tcex.logger.trace_logger import TraceLogger
from tcex.pleb.cached_property import cached_property
from tcex.pleb.proxies import proxies
from tcex.pleb.scoped_property import scoped_property
from tcex.registry import registry
from tcex.requests_external import ExternalSession, RequestsExternal
from tcex.requests_tc import RequestsTc, TcSession
from tcex.util import Util


@dataclass
class _Session:
    """Session dataclass."""

    external: ExternalSession
    tc: TcSession


class TcEx:
    """Provides functionality for all types of TxEx Apps.

    Args:
        config (dict, kwargs): A dictionary containing configuration items typically used by
            external Apps.
        config_file (str, kwargs): A filename containing JSON configuration items typically used
            by external Apps.
    """

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        # catch interrupt signals specifically based on thread name
        signal.signal(signal.SIGINT, self._signal_handler)
        if platform.system() != 'Windows':
            signal.signal(signal.SIGHUP, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # properties
        self._log: TraceLogger  # allow logger to be overridden

        # initialize TcEx/App inputs
        self.inputs = Input(kwargs.get('config') or {}, kwargs.get('config_file'))

        # add methods to registry
        registry.register(self)
        registry.add_service(Input, self.inputs)
        registry.add_service(App, self.app)
        registry.add_service(Logger, self.logger)
        registry.add_service(RequestsTc, self.requests_tc)

        # log standard App info early so it shows at the top of the logfile
        self.logger.log_info(self.inputs.model_tc)

    def _signal_handler(self, signal_interrupt: int, _):
        """Handle signal interrupt."""
        call_file = os.path.basename(inspect.stack()[1][0].f_code.co_filename)
        call_module = inspect.stack()[1][0].f_globals['__name__'].lstrip('Functions.')
        call_line = inspect.stack()[1][0].f_lineno
        self.log.error(
            f'App interrupted - file: {call_file}, method: {call_module}, line: {call_line}.'
        )
        exit_code = ExitCode.SUCCESS
        if threading.current_thread().name == 'MainThread' and signal_interrupt in (2, 15):
            exit_code = ExitCode.FAILURE

        # pylint: disable=no-member
        self.exit.exit(exit_code, 'The App received an interrupt signal and will now exit.')

    @cached_property
    def api(self) -> API:
        """Return instance of API."""
        # pylint: disable=no-member
        return API(self.inputs, self.session.tc)

    @cached_property
    def app(self) -> App:
        """Return instance of App."""
        return App(self.inputs.module_app_model, self.proxies)

    @registry.factory(Exit)
    @scoped_property
    def exit(self) -> Exit:
        """Return an instance of Exit."""
        return Exit(self.inputs)

    @property
    def log(self) -> TraceLogger:
        """Return a valid logger."""
        if self._log is None:
            self._log = self.logger.log
        return self._log

    @log.setter
    def log(self, log: TraceLogger):
        """Return a valid logger."""
        if isinstance(log, TraceLogger):
            self._log = log

    @cached_property
    def logger(self) -> Logger:
        """Return logger."""
        _logger = Logger(logger_name='tcex')

        # set logger to prevent recursion issue on get_session
        self._log = _logger.log

        # add api handler
        if self.inputs.contents.get('tc_token') is not None and self.inputs.contents.get(
            'tc_log_to_api'
        ) in (True, 'true'):
            _logger.add_api_handler(
                session_tc=self.requests_tc.get_session(),
                level=self.inputs.model_tc.tc_log_level,
            )

        # add rotating log handler
        _logger.add_rotating_file_handler(
            name='rfh',
            filename=self.inputs.model_tc.tc_log_file,
            path=self.inputs.model_tc.tc_log_path,
            backup_count=self.inputs.model_tc.tc_log_backup_count,
            max_bytes=self.inputs.model_tc.tc_log_max_bytes,
            level=self.inputs.model_tc.tc_log_level,
        )

        # set logging level
        _logger.update_handler_level(level=self.inputs.model_tc.tc_log_level)
        _logger.log.setLevel(_logger.log_level(self.inputs.model_tc.tc_log_level))

        # replay cached log events
        _logger.replay_cached_events(handler_name='cache')

        return _logger

    @cached_property
    def proxies(self) -> dict:
        """Format the proxy configuration for Python Requests module.

        Generates a dictionary for use with the Python Requests module format
        when proxy is required for remote connections.

        **Example Response**
        ::

            {"http": "http://user:pass@10.10.1.10:3128/"}
        """
        return proxies(
            proxy_host=self.inputs.model_tc.tc_proxy_host,
            proxy_port=self.inputs.model_tc.tc_proxy_port,
            proxy_user=self.inputs.model_tc.tc_proxy_username,
            proxy_pass=self.inputs.model_tc.tc_proxy_password,
        )

    @cached_property
    def requests_external(self) -> RequestsExternal:
        """Return instance of RequestsSession."""
        return RequestsExternal(self.inputs.module_requests_session_model, self.proxies)

    @cached_property
    def requests_tc(self) -> RequestsTc:
        """Return instance of RequestsSession."""
        return RequestsTc(self.inputs.module_requests_session_model)

    @cached_property
    def session(self) -> _Session:
        """Return Session object.

        Add interface to access Sessions:

        * self.tcex.session.external
        * self.tcex.session.tc
        """
        return _Session(external=self.requests_external.session, tc=self.requests_tc.session)

    @cached_property
    def util(self) -> Util:
        """Return instance of Util."""
        return Util()
