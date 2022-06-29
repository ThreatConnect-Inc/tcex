"""TcEx Framework"""

# standard library
import inspect
import logging
import os
import platform
import signal
import threading
from typing import TYPE_CHECKING, Dict, Optional, Union

# third-party
from requests import Session

# first-party
from tcex.api.tc.utils.threat_intel_utils import ThreatIntelUtils
from tcex.api.tc.v2.v2 import V2
from tcex.api.tc.v3.v3 import V3
from tcex.app_config.install_json import InstallJson
from tcex.app_feature import AdvancedRequest
from tcex.backports import cached_property
from tcex.exit.exit import ExitCode, ExitService
from tcex.input.input import Input
from tcex.key_value_store import KeyValueApi, KeyValueRedis, RedisClient
from tcex.logger.logger import Logger  # pylint: disable=no-name-in-module
from tcex.playbook import Playbook
from tcex.pleb.proxies import proxies
from tcex.pleb.registry import registry
from tcex.pleb.scoped_property import scoped_property
from tcex.sessions.auth.tc_auth import TcAuth
from tcex.sessions.external_session import ExternalSession
from tcex.sessions.tc_session import TcSession
from tcex.tokens import Tokens
from tcex.utils import Utils
from tcex.utils.file_operations import FileOperations

if TYPE_CHECKING:
    # first-party
    from tcex.logger.trace_logger import TraceLogger  # pylint: disable=no-name-in-module
    from tcex.services.api_service import ApiService
    from tcex.services.common_service_trigger import CommonServiceTrigger
    from tcex.services.webhook_trigger_service import WebhookTriggerService
    from tcex.sessions.auth.hmac_auth import HmacAuth
    from tcex.sessions.auth.token_auth import TokenAuth


class TcEx:
    """Provides basic functionality for all types of TxEx Apps.

    Args:
        config (dict, kwargs): A dictionary containing configuration items typically used by
            external Apps.
        config_file (str, kwargs): A filename containing JSON configuration items typically used
            by external Apps.
    """

    def __init__(self, **kwargs):
        """Initialize Class Properties."""
        # catch interrupt signals specifically based on thread name
        signal.signal(signal.SIGINT, self._signal_handler)
        if platform.system() != 'Windows':
            signal.signal(signal.SIGHUP, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Property defaults
        self._config: dict = kwargs.get('config') or {}
        self._log = None
        self._jobs = None
        self._redis_client = None
        self._service = None
        self.ij = InstallJson()
        self.main_os_pid = os.getpid()

        # init inputs
        self.inputs = Input(self._config, kwargs.get('config_file'))

        # add methods to registry
        registry.add_method(self.inputs.resolve_variable)

        # add methods to registry
        registry.register(self)
        registry.add_service(Input, self.inputs)

        # log standard App info early so it shows at the top of the logfile
        self.logger.log_info(self.inputs.model_unresolved)

    def _signal_handler(self, signal_interrupt: int, _):
        """Handle signal interrupt."""
        call_file: str = os.path.basename(inspect.stack()[1][0].f_code.co_filename)
        call_module: str = inspect.stack()[1][0].f_globals['__name__'].lstrip('Functions.')
        call_line: int = inspect.stack()[1][0].f_lineno
        self.log.error(
            f'App interrupted - file: {call_file}, method: {call_module}, line: {call_line}.'
        )
        exit_code = ExitCode.SUCCESS
        if threading.current_thread().name == 'MainThread' and signal_interrupt in (2, 15):
            exit_code = ExitCode.FAILURE

        self.exit(exit_code, 'The App received an interrupt signal and will now exit.')

    @property
    def _user_agent(self):
        """Return a User-Agent string."""
        return {
            'User-Agent': (
                f'TcEx/{__import__(__name__).__version__}, '
                f'{self.ij.model.display_name}/{self.ij.model.program_version}'
            )
        }

    def advanced_request(
        self,
        session: Session,
        output_prefix: str,
        timeout: Optional[int] = 600,
    ) -> 'AdvancedRequest':
        """Return instance of AdvancedRequest.

        Args:
            session: An instance of requests.Session.
            output_prefix: A value to prepend to outputs.
            timeout: The number of second before timing out the request.
        """
        return AdvancedRequest(self.inputs, self.playbook, session, output_prefix, timeout)

    def exit(self, code: Optional[ExitCode] = None, msg: Optional[str] = None):
        """Application exit method with proper exit code

        The method will run the Python standard sys.exit() with the exit code
        previously defined via :py:meth:`~tcex.tcex.TcEx.exit_code` or provided
        during the call of this method.

        Args:
            code: The exit code value for the app.
            msg: A message to log and add to message tc output.
        """
        # get correct code
        self.exit_service.exit(code, msg)  # pylint: disable=no-member

    @property
    def exit_code(self) -> 'ExitCode':
        """Return the current exit code."""
        return self.exit_service.exit_code  # pylint: disable=no-member

    @exit_code.setter
    def exit_code(self, code: 'ExitCode'):
        """Set the App exit code.

        For TC Exchange Apps there are 3 supported exit codes.
        * 0 indicates a normal exit
        * 1 indicates a failure during execution
        * 3 indicates a partial failure

        Args:
            code (int): The exit code value for the app.
        """
        self.exit_service.exit_code = code

    @registry.factory(ExitService)
    @scoped_property
    def exit_service(self) -> 'ExitService':
        """Return an ExitService object."""
        # TODO: [high] @cblades - inputs being required for exit prevents AOT from exiting
        return self.get_exit_service(self.inputs)

    @cached_property
    def file_operations(self) -> 'FileOperations':  # pylint: disable=no-self-use
        """Include the Utils module."""
        return FileOperations(temp_path=self.inputs.model_unresolved.tc_temp_path)

    @staticmethod
    def get_exit_service(inputs) -> 'ExitService':
        """Create an ExitService object."""
        return ExitService(inputs)

    def get_playbook(
        self, context: Optional[str] = None, output_variables: Optional[list] = None
    ) -> 'Playbook':
        """Return a new instance of playbook module.

        Args:
            context: The KV Store context/session_id. For PB Apps the context is provided on
                startup, but for service Apps each request gets a different context.
            output_variables: The requested output variables. For PB Apps outputs are provided on
                startup, but for service Apps each request gets different outputs.
        """
        return Playbook(self.key_value_store, context, output_variables)

    @staticmethod
    def get_redis_client(
        host: str, port: int, db: int = 0, blocking_pool: bool = False, **kwargs
    ) -> 'RedisClient':
        """Return a *new* instance of Redis client.

        For a full list of kwargs see https://redis-py.readthedocs.io/en/latest/#redis.Connection.

        Args:
            host: The REDIS host. Defaults to localhost.
            port: The REDIS port. Defaults to 6379.
            db: The REDIS db. Defaults to 0.
            blocking_pool: Use BlockingConnectionPool instead of ConnectionPool.
            errors (str, kwargs): The REDIS errors policy (e.g. strict).
            max_connections (int, kwargs): The maximum number of connections to REDIS.
            password (str, kwargs): The REDIS password.
            socket_timeout (int, kwargs): The REDIS socket timeout.
            timeout (int, kwargs): The REDIS Blocking Connection Pool timeout value.

        Returns:
            Redis.client: An instance of redis client.
        """
        return RedisClient(
            host=host, port=port, db=db, blocking_pool=blocking_pool, **kwargs
        ).client

    def get_session_tc(
        self,
        auth: Optional[Union['HmacAuth', 'TokenAuth', 'TcAuth']] = None,
        base_url: Optional[str] = None,
        log_curl: Optional[bool] = None,
        proxies: Optional[Dict[str, str]] = None,  # pylint: disable=redefined-outer-name
        proxies_enabled: Optional[bool] = None,
        verify: Optional[Union[bool, str]] = None,
    ) -> 'TcSession':
        """Return an instance of Requests Session configured for the ThreatConnect API.

        No args are required to get a working instance of TC Session instance.

        This method allows for getting a new instance of TC Session instance. This can be
        very useful when connecting between multiple TC instances (e.g., migrating data).
        """
        if log_curl is None:
            log_curl = self.inputs.model_unresolved.tc_log_curl

        if proxies_enabled is None:
            proxies_enabled = self.inputs.model_unresolved.tc_proxy_tc

        if verify is None:
            verify = self.inputs.model_unresolved.tc_verify

        auth = auth or TcAuth(
            tc_api_access_id=self.inputs.model_unresolved.tc_api_access_id,
            tc_api_secret_key=self.inputs.model_unresolved.tc_api_secret_key,
            tc_token=self.token,
        )

        return TcSession(
            auth=auth,
            base_url=base_url or self.inputs.model_unresolved.tc_api_path,
            log_curl=log_curl,
            proxies=proxies or self.proxies,
            proxies_enabled=proxies_enabled,
            user_agent=self._user_agent,
            verify=verify,
        )

    def get_session_external(self) -> 'ExternalSession':
        """Return an instance of Requests Session configured for the ThreatConnect API."""
        _session_external = ExternalSession()

        # add User-Agent to headers
        _session_external.headers.update(self._user_agent)

        # add proxy support if requested
        if self.inputs.model_unresolved.tc_proxy_external:
            _session_external.proxies = self.proxies
            self.log.info(
                f'Using proxy host {self.inputs.model_unresolved.tc_proxy_host}:'
                f'{self.inputs.model_unresolved.tc_proxy_port} for external session.'
            )

        if self.inputs.model_unresolved.tc_log_curl:
            _session_external.log_curl = True

        return _session_external

    # def get_ti(self) -> 'ThreatIntelligence':
    #     """Include the Threat Intel Module."""
    #     return ThreatIntelligence(session=self.get_session_tc())

    @registry.factory('KeyValueStore')
    @scoped_property
    def key_value_store(self) -> Union['KeyValueApi', 'KeyValueRedis']:
        """Return the correct KV store for this execution.

        The TCKeyValueAPI KV store is limited to two operations (create and read),
        while the Redis kvstore wraps a few other Redis methods.
        """
        if self.inputs.model_unresolved.tc_kvstore_type == 'Redis':
            return KeyValueRedis(self.redis_client)

        if self.inputs.model_unresolved.tc_kvstore_type == 'TCKeyValueAPI':
            return KeyValueApi(self.session_tc)

        raise RuntimeError(
            f'Invalid KV Store Type: ({self.inputs.model_unresolved.tc_kvstore_type})'
        )

    @property
    def log(self) -> 'TraceLogger':
        """Return a valid logger."""
        if self._log is None:
            self._log = self.logger.log
        return self._log

    @log.setter
    def log(self, log: object):
        """Return a valid logger."""
        if isinstance(log, logging.Logger):
            self._log = log

    @cached_property
    def logger(self) -> 'Logger':
        """Return logger."""
        _logger = Logger(logger_name='tcex')

        # set logger to prevent recursion issue on get_session_tc
        self._log = _logger.log

        # add api handler
        if (
            self.inputs.contents.get('tc_token') is not None
            and self.inputs.contents.get('tc_log_to_api') is True
        ):
            _logger.add_api_handler(
                session_tc=self.get_session_tc(), level=self.inputs.model_unresolved.tc_log_level
            )

        # add rotating log handler
        _logger.add_rotating_file_handler(
            name='rfh',
            filename=self.inputs.model_unresolved.tc_log_file,
            path=self.inputs.model_unresolved.tc_log_path,
            backup_count=self.inputs.model_unresolved.tc_log_backup_count,
            max_bytes=self.inputs.model_unresolved.tc_log_max_bytes,
            level=self.inputs.model_unresolved.tc_log_level,
        )

        # set logging level
        _logger.update_handler_level(level=self.inputs.model_unresolved.tc_log_level)
        _logger.log.setLevel(_logger.log_level(self.inputs.model_unresolved.tc_log_level))

        # replay cached log events
        _logger.replay_cached_events(handler_name='cache')

        return _logger

    @registry.factory(Playbook)
    @scoped_property
    def playbook(self) -> 'Playbook':
        """Return an instance of Playbooks module.

        This property defaults context and outputvariables to arg values.

        Returns:
            tcex.playbook.Playbooks: An instance of Playbooks
        """
        return self.get_playbook(
            context=self.inputs.model_unresolved.tc_playbook_kvstore_context,
            output_variables=self.inputs.model_unresolved.tc_playbook_out_variables,
        )

    @cached_property
    def proxies(self) -> dict:
        """Format the proxy configuration for Python Requests module.

        Generates a dictionary for use with the Python Requests module format
        when proxy is required for remote connections.

        **Example Response**
        ::

            {"http": "http://user:pass@10.10.1.10:3128/"}

        Returns:
           (dict): Dictionary of proxy settings
        """
        return proxies(
            proxy_host=self.inputs.model_unresolved.tc_proxy_host,
            proxy_port=self.inputs.model_unresolved.tc_proxy_port,
            proxy_user=self.inputs.model_unresolved.tc_proxy_username,
            proxy_pass=self.inputs.model_unresolved.tc_proxy_password,
        )

    @registry.factory(RedisClient)
    @scoped_property
    def redis_client(self) -> 'RedisClient':
        """Return redis client instance configure for Playbook/Service Apps."""
        return self.get_redis_client(
            host=self.inputs.contents.get('tc_kvstore_host'),
            port=self.inputs.contents.get('tc_kvstore_port'),
            db=0,
        )

    def results_tc(self, key: str, value: str):
        """Write data to results_tc file in TcEX specified directory.

        The TcEx platform support persistent values between executions of the App.  This
        method will store the values for TC to read and put into the Database.

        Args:
            key: The data key to be stored.
            value: The data value to be stored.
        """
        if os.access(self.inputs.model_unresolved.tc_out_path, os.W_OK):
            results_file = f'{self.inputs.model_unresolved.tc_out_path}/results.tc'
        else:
            results_file = 'results.tc'

        new = True
        # ensure file exists
        open(results_file, 'a').close()  # pylint: disable=consider-using-with
        with open(results_file, 'r+') as fh:
            results = ''
            for line in fh.read().strip().split('\n'):
                if not line:
                    continue
                try:
                    k, v = line.split(' = ')
                except ValueError:
                    # handle null/empty value (e.g., "name =")
                    k, v = line.split(' =')
                if k == key:
                    v = value
                    new = False
                if v is not None:
                    results += f'{k} = {v}\n'
            if new and value is not None:  # indicates the key/value pair didn't already exist
                results += f'{key} = {value}\n'
            fh.seek(0)
            fh.write(results)
            fh.truncate()

    @cached_property
    def service(self) -> Union['ApiService', 'CommonServiceTrigger', 'WebhookTriggerService']:
        """Include the Service Module."""
        if self.ij.model.runtime_level.lower() == 'apiservice':
            from .services import ApiService as Service
        elif self.ij.model.runtime_level.lower() == 'triggerservice':
            from .services import CommonServiceTrigger as Service
        elif self.ij.model.runtime_level.lower() == 'webhooktriggerservice':
            from .services import WebhookTriggerService as Service
        else:
            self.exit(1, 'Could not determine the service type.')

        return Service(self)

    @registry.factory(TcSession)
    @scoped_property
    def session_tc(self) -> 'TcSession':
        """Return an instance of Requests Session configured for the ThreatConnect API."""
        return self.get_session_tc()

    @scoped_property
    def session_external(self) -> 'ExternalSession':
        """Return an instance of Requests Session configured for the ThreatConnect API."""
        return self.get_session_external()

    @registry.factory(Tokens, singleton=True)
    @cached_property
    def token(self) -> 'Tokens':
        """Return token object."""
        _proxies = None
        if self.inputs.model_unresolved.tc_proxy_tc is True:
            _proxies = self.proxies

        _tokens = Tokens(
            self.inputs.model_unresolved.tc_api_path,
            self.inputs.model_unresolved.tc_verify,
            _proxies,
        )

        # register token for Apps that pass token on start
        if all(
            [self.inputs.model_unresolved.tc_token, self.inputs.model_unresolved.tc_token_expires]
        ):
            _tokens.register_token(
                key=threading.current_thread().name,
                token=self.inputs.model_unresolved.tc_token,
                expires=self.inputs.model_unresolved.tc_token_expires,
            )
        return _tokens

    def set_exit_code(self, exit_code: int):
        """Set the exit code (registry)"""
        self.exit_code = exit_code

    @property
    def ti_utils(self) -> 'ThreatIntelUtils':
        """Return instance of Threat Intel Utils."""
        return ThreatIntelUtils(self.session_tc)

    @cached_property
    def utils(self) -> 'Utils':  # pylint: disable=no-self-use
        """Include the Utils module."""
        return Utils()

    @property
    def v2(self) -> 'V2':
        """Return a case management instance."""
        return V2(self.inputs, self.session_tc)

    @property
    def v3(self) -> 'V3':
        """Return a case management instance."""
        return V3(self.session_tc)
