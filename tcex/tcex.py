"""TcEx Framework"""

# standard library
import inspect
import logging
import os
import platform
import signal
import sys
import threading
from typing import Optional, Union

# third-party
from requests import Session

# first-party
from tcex.app_config import InstallJson
from tcex.app_feature import AdvancedRequest
from tcex.backports import cached_property
from tcex.batch.batch import Batch
from tcex.batch.batch_submit import BatchSubmit
from tcex.batch.batch_writer import BatchWriter
from tcex.case_management import CaseManagement
from tcex.datastore import Cache, DataStore
from tcex.input import Input
from tcex.key_value_store import KeyValueApi, KeyValueRedis, RedisClient
from tcex.logger import Logger, TraceLogger
from tcex.metrics import Metrics
from tcex.notifications import Notifications
from tcex.playbook import Playbook
from tcex.pleb import Event, proxies
from tcex.services.api_service import ApiService
from tcex.services.common_service_trigger import CommonServiceTrigger
from tcex.services.webhook_trigger_service import WebhookTriggerService
from tcex.sessions import ExternalSession, TcSession
from tcex.stix import StixModel
from tcex.tcex_error_codes import TcExErrorCodes
from tcex.threat_intelligence import ThreatIntelligence
from tcex.tokens import Tokens
from tcex.utils import Utils


class TcEx:
    """Provides basic functionality for all types of TxEx Apps.

    Args:
        config (dict, kwargs): A dictionary containing configuration items typically used by
            external Apps.
        config_file (str, kwargs): A filename containing JSON configuration items typically used
            by external Apps.
        logger (logging.Logger, kwargs): An pre-configured instance of logger to use instead of
            tcex logger.
    """

    def __init__(self, **kwargs):
        """Initialize Class Properties."""
        # catch interupt signals specifically based on thread name
        signal.signal(signal.SIGINT, self._signal_handler)
        if platform.system() != 'Windows':
            signal.signal(signal.SIGHUP, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Property defaults
        self._config: dict = kwargs.get('config') or {}
        self._exit_code = 0
        self._jobs = None
        self._logger = None
        self._redis_client = None
        self._service = None
        self.event = Event()
        self.ij = InstallJson()
        self.main_os_pid = os.getpid()

        # add custom logger if provided
        self._log: object = kwargs.get('logger')

        # init inputs
        self.inputs = Input(self._config, kwargs.get('config_file'))

        # method subscription for Event module
        self.event.subscribe(channel='exit', callback=self.exit)
        self.event.subscribe(channel='exit_code', callback=self.exit_code)
        self.event.subscribe(channel='handle_error', callback=self.handle_error)
        # support external Apps that will not use tokens
        if self.ij.fqfn.is_file():
            self.event.subscribe(channel='register_token', callback=self.token.register_token)

    def _signal_handler(self, signal_interupt: int, _) -> None:
        """Handle singal interrupt."""
        call_file: str = os.path.basename(inspect.stack()[1][0].f_code.co_filename)
        call_module: str = inspect.stack()[1][0].f_globals['__name__'].lstrip('Functions.')
        call_line: int = inspect.stack()[1][0].f_lineno
        self.log.error(
            f'App interrupted - file: {call_file}, method: {call_module}, line: {call_line}.'
        )
        exit_code = 0
        if threading.current_thread().name == 'MainThread' and signal_interupt in (2, 15):
            exit_code = 1

        self.exit(exit_code, 'The App received an interrupt signal and will now exit.')

    def advanced_request(
        self, session: Session, timeout: Optional[int] = 600, output_prefix: Optional[str] = None
    ) -> AdvancedRequest:
        """Return instance of AdvancedRequest.

        Args:
            session: An instance of requests.Session.
            timeout: The number of second before timing out the request.
            output_prefix: A value to prepend to outputs.
        """
        return AdvancedRequest(self.inputs, self.playbook, session, timeout, output_prefix)

    def aot_rpush(self, exit_code: int) -> None:
        """Push message to AOT action channel."""
        if self.inputs.data.tc_playbook_db_type == 'Redis':
            try:
                self.redis_client.rpush(self.inputs.data.tc_exit_channel, exit_code)
            except Exception as e:  # pragma: no cover
                self.exit(1, f'Exception during AOT exit push ({e}).')

    def batch(
        self,
        owner: str,
        action: Optional[str] = 'Create',
        attribute_write_type: Optional[str] = 'Replace',
        halt_on_error: Optional[bool] = False,
        playbook_triggers_enabled: Optional[bool] = False,
        tag_write_type: Optional[str] = 'Replace',
        security_label_write_type: Optional[str] = 'Replace',
    ) -> Batch:
        """Return instance of Batch

        Args:
            tcex: An instance of TcEx object.
            owner: The ThreatConnect owner for Batch action.
            action: Action for the batch job ['Create', 'Delete'].
            attribute_write_type: Write type for TI attributes ['Append', 'Replace'].
            halt_on_error: If True any batch error will halt the batch job.
            playbook_triggers_enabled: Deprecated input, will not be used.
            security_label_write_type: Write type for labels ['Append', 'Replace'].
            tag_write_type: Write type for tags ['Append', 'Replace'].
        """
        return Batch(
            self,
            owner,
            action,
            attribute_write_type,
            halt_on_error,
            playbook_triggers_enabled,
            tag_write_type,
            security_label_write_type,
        )

    def batch_submit(
        self,
        owner: str,
        action: Optional[str] = 'Create',
        attribute_write_type: Optional[str] = 'Replace',
        halt_on_error: Optional[bool] = False,
        playbook_triggers_enabled: Optional[bool] = False,
        tag_write_type: Optional[str] = 'Replace',
        security_label_write_type: Optional[str] = 'Replace',
    ) -> BatchSubmit:
        """Return instance of Batch

        Args:
            tcex: An instance of TcEx object.
            owner: The ThreatConnect owner for Batch action.
            action: Action for the batch job ['Create', 'Delete'].
            attribute_write_type: Write type for TI attributes ['Append', 'Replace'].
            halt_on_error: If True any batch error will halt the batch job.
            playbook_triggers_enabled: Deprecated input, will not be used.
            security_label_write_type: Write type for labels ['Append', 'Replace'].
            tag_write_type: Write type for tags ['Append', 'Replace'].
        """
        return BatchSubmit(
            self,
            owner,
            action,
            attribute_write_type,
            halt_on_error,
            playbook_triggers_enabled,
            tag_write_type,
            security_label_write_type,
        )

    def batch_writer(self, output_dir: str, **kwargs) -> BatchWriter:
        """Return instance of Batch

        Args:
            tcex: An instance of TcEx object.
            output_dir: Deprecated input, will not be used.
            output_extension (kwargs: str): Append this extension to output files.
            write_callback (kwargs: Callable): A callback method to call when a batch json file
                is written. The callback will be passed the fully qualified name of the written
                file.
            write_callback_kwargs (kwargs: dict): Additional values to send to callback method.
        """
        return BatchWriter(self, output_dir, **kwargs)

    def cache(
        self,
        domain: str,
        data_type: str,
        ttl_seconds: Optional[int] = None,
        mapping: Optional[dict] = None,
    ) -> Cache:
        """Get instance of the Cache module.

        Args:
            domain: The domain can be either "system", "organization", or "local". When using
                "organization" the data store can be accessed by any Application in the entire org,
                while "local" access is restricted to the App writing the data. The "system" option
                should not be used in almost all cases.
            data_type: The data type descriptor (e.g., tc:whois:cache).
            ttl_seconds: The number of seconds the cache is valid.
            mapping: Advanced - The datastore mapping if required.
        """
        return Cache(self.session, domain, data_type, ttl_seconds, mapping)

    @property
    def case_management(self) -> CaseManagement:
        """Return a case management instance."""
        return CaseManagement(self.session)

    @property
    def cm(self) -> CaseManagement:
        """Alias for case_management."""
        return self.case_management

    def datastore(self, domain: str, data_type: str, mapping: Optional[dict] = None) -> DataStore:
        """Get instance of the DataStore module.

        Args:
            domain: The domain can be either "system", "organization", or "local". When using
                "organization" the data store can be accessed by any Application in the entire org,
                while "local" access is restricted to the App writing the data. The "system" option
                should not be used in almost all cases.
            data_type: The data type descriptor (e.g., tc:whois:cache).
            mapping: ElasticSearch mappings data.
        """
        return DataStore(self.session, domain, data_type, mapping)

    @cached_property
    def error_codes(self) -> TcExErrorCodes:  # pylint: disable=no-self-use
        """Return TcEx error codes."""
        return TcExErrorCodes()

    def exit(self, code: Optional[int] = None, msg: Optional[str] = None) -> None:
        """Application exit method with proper exit code

        The method will run the Python standard sys.exit() with the exit code
        previously defined via :py:meth:`~tcex.tcex.TcEx.exit_code` or provided
        during the call of this method.

        Args:
            code: The exit code value for the app.
            msg: A message to log and add to message tc output.
        """
        # get correct code
        code = self.exit_code_handler(code)

        # handle exit msg logging
        self.exit_msg_handler(code, msg)

        # playbook exit
        self.exit_playbook_handler(msg)

        # aot notify
        if self.inputs.data.tc_aot_enabled:
            # push exit message
            self.aot_rpush(code)

        # exit token renewal thread
        self.token.shutdown = True

        self.log.info(f'Exit Code: {code}')
        sys.exit(code)

    def exit_code_handler(self, code: int) -> int:
        """Return a valid exit code based on the App Type"""
        code = code or self.exit_code

        if code == 3 and self.ij.data.runtime_level.lower() == 'playbook':
            self.log.info('Changing exit code from 3 to 0 for Playbook App.')
            code = 0
        elif code in [0, 1, 3]:
            pass
        else:
            self.log.error('Invalid exit code')
            code = 1

        return code

    def exit_msg_handler(self, code: int, msg: str) -> None:
        """Handle exit message. Write to both log and message_tc."""
        if msg is not None:
            if code in [0, 3] or (code is None and self.exit_code in [0, 3]):
                self.log.info(msg)
            else:
                self.log.error(msg)
            self.message_tc(msg)

    def exit_playbook_handler(self, msg: str) -> None:
        """Perform special action for PB Apps before exit."""
        # write outputs before exiting
        self.playbook.write_output()

        # required only for tcex testing framework
        if self.inputs.data.tcex_testing_context is not None:  # pragma: no cover
            self.redis_client.hset(self.inputs.data.tcex_testing_context, '_exit_message', msg)

    @property
    def exit_code(self) -> None:
        """Return the current exit code."""
        return self._exit_code

    @exit_code.setter
    def exit_code(self, code: int) -> None:
        """Set the App exit code.

        For TC Exchange Apps there are 3 supported exit codes.
        * 0 indicates a normal exit
        * 1 indicates a failure during execution
        * 3 indicates a partial failure

        Args:
            code (int): The exit code value for the app.
        """
        if code is not None and code in [0, 1, 3]:
            self._exit_code = code
        else:
            self.log.warning('Invalid exit code')

    def get_playbook(
        self, context: Optional[str] = None, output_variables: Optional[list] = None
    ) -> Playbook:
        """Return a new instance of playbook module.

        Args:
            context: The KV Store context/session_id. For PB Apps the context is provided on
                startup, but for service Apps each request gets a different context.
            output_variables: The requested output variables. For PB Apps outputs are provided on
                startup, but for service Apps each request gets different outputs.
        """
        return Playbook(self.key_value_store, context, output_variables)

    @staticmethod
    def get_redis_client(host, port, db=0, blocking=False, **kwargs) -> RedisClient:
        """Return a *new* instance of Redis client.

        For a full list of kwargs see https://redis-py.readthedocs.io/en/latest/#redis.Connection.

        Args:
            host (str, optional): The REDIS host. Defaults to localhost.
            port (int, optional): The REDIS port. Defaults to 6379.
            db (int, optional): The REDIS db. Defaults to 0.
            blocking_pool (bool): Use BlockingConnectionPool instead of ConnectionPool.
            errors (str, kwargs): The REDIS errors policy (e.g. strict).
            max_connections (int, kwargs): The maximum number of connections to REDIS.
            password (str, kwargs): The REDIS password.
            socket_timeout (int, kwargs): The REDIS socket timeout.
            timeout (int, kwargs): The REDIS Blocking Connection Pool timeout value.

        Returns:
            Redis.client: An instance of redis client.
        """
        return RedisClient(host=host, port=port, db=db, blocking=blocking, **kwargs).client

    # TODO: [high] testing ... organize this later
    def get_session(self) -> TcSession:
        """Return an instance of Requests Session configured for the ThreatConnect API."""
        _session = TcSession(
            tc_api_access_id=self.inputs.data.tc_api_access_id,
            tc_api_secret_key=self.inputs.data.tc_api_secret_key,
            tc_base_url=self.inputs.data.tc_api_path,
        )

        # set verify
        _session.verify = self.inputs.data.tc_verify

        # set token
        _session.token = self.token

        # update User-Agent
        _session.headers.update({'User-Agent': f'TcEx: {__import__(__name__).__version__}'})

        # add proxy support if requested
        if self.inputs.data.tc_proxy_tc:
            _session.proxies = self.proxies
            self.log.info(
                f'Using proxy host {self.inputs.data.tc_proxy_host}:'
                f'{self.inputs.data.tc_proxy_port} for ThreatConnect session.'
            )

        # enable curl logging if tc_log_curl param is set.
        if self.inputs.data.tc_log_curl:
            _session.log_curl = True

        return _session

    def get_session_external(self) -> ExternalSession:
        """Return an instance of Requests Session configured for the ThreatConnect API."""
        _session_external = ExternalSession(logger=self.log)

        # add User-Agent to headers
        _session_external.headers.update(
            {
                'User-Agent': (
                    f'TcEx App: {self.ij.data.display_name} - {self.ij.data.program_version}'
                )
            }
        )

        # add proxy support if requested
        if self.inputs.data.tc_proxy_external:
            _session_external.proxies = self.proxies
            self.log.info(
                f'Using proxy host {self.inputs.data.tc_proxy_host}:'
                f'{self.inputs.data.tc_proxy_port} for external session.'
            )

        if self.inputs.data.tc_log_curl:
            _session_external.log_curl = True

        return _session_external

    def get_ti(self) -> ThreatIntelligence:
        """Include the Threat Intel Module."""
        return ThreatIntelligence(session=self.get_session())

    def handle_error(
        self, code: int, message_values: Optional[list] = None, raise_error: Optional[bool] = True
    ) -> None:
        """Raise RuntimeError

        Args:
            code: The error code from API or SDK.
            message: The error message from API or SDK.
            raise_error: Raise a Runtime error. Defaults to True.

        Raises:
            RuntimeError: Raised a defined error.
        """
        try:
            if message_values is None:
                message_values = []
            message = self.error_codes.message(code).format(*message_values)
            self.log.error(f'Error code: {code}, {message}')
        except AttributeError:
            self.log.error(f'Incorrect error code provided ({code}).')
            raise RuntimeError(100, 'Generic Failure, see logs for more details.')
        except IndexError:
            self.log.error(
                f'Incorrect message values provided for error code {code} ({message_values}).'
            )
            raise RuntimeError(100, 'Generic Failure, see logs for more details.')
        if raise_error:
            raise RuntimeError(code, message)

    # TODO: [med] update to support scoped instance
    @property
    def key_value_store(self) -> Union[KeyValueApi, KeyValueRedis]:
        """Return the correct KV store for this execution.

        The TCKeyValueAPI KV store is limited to two operations (create and read),
        while the Redis kvstore wraps a few other Redis methods.
        """
        if self.inputs.data.tc_kvstore_type == 'Redis':
            return KeyValueRedis(self.redis_client)

        if self.inputs.data.tc_kvstore_type == 'TCKeyValueAPI':
            return KeyValueApi(self.session)

        raise RuntimeError(f'Invalid KV Store Type: ({self.inputs.data.tc_kvstore_type})')

    @property
    def log(self) -> TraceLogger:
        """Return a valid logger."""
        if self._log is None:
            self._log = self.logger.log
        return self._log

    @log.setter
    def log(self, log: object) -> None:
        """Return a valid logger."""
        if isinstance(log, logging.Logger):
            self._log = log

    @property
    def logger(self) -> Logger:
        """Return logger."""
        if self._logger is None:
            self._logger = Logger(self, 'tcex')
            self._logger.add_cache_handler('cache')
        return self._logger

    def metric(
        self,
        name: str,
        description: str,
        data_type: str,
        interval: str,
        keyed: Optional[bool] = False,
    ) -> Metrics:
        """Get instance of the Metrics module.

        Args:
            name: The name for the metric.
            description: The description of the metric.
            data_type: The type of metric: Sum, Count, Min, Max, First, Last, and Average.
            interval: The metric interval: Hourly, Daily, Weekly, Monthly, and Yearly.
            keyed: Indicates whether the data will have a keyed value.
        """
        return Metrics(self, name, description, data_type, interval, keyed)

    def message_tc(self, message: str, max_length: Optional[int] = 255) -> None:
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

        if os.access(self.inputs.data.tc_out_path, os.W_OK):
            message_file = os.path.join(self.inputs.data.tc_out_path, 'message.tc')
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

    def notification(self) -> Notifications:
        """Get instance of the Notification module."""
        return Notifications(self)

    @cached_property
    def playbook(self) -> Playbook:
        """Return an instance of Playbooks module.

        This property defaults context and outputvariables to arg values.

        Returns:
            tcex.playbook.Playbooks: An instance of Playbooks
        """
        return self.get_playbook(
            context=self.inputs.data.tc_playbook_kvstore_context,
            output_variables=self.inputs.data.tc_playbook_out_variables,
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
            proxy_host=self.inputs.data.tc_proxy_host,
            proxy_port=self.inputs.data.tc_proxy_port,
            proxy_user=self.inputs.data.tc_proxy_username,
            proxy_pass=self.inputs.data.tc_proxy_password,
        )

    # TODO: [med] update to support scoped instance
    @cached_property
    def redis_client(self) -> RedisClient:
        """Return redis client instance configure for Playbook/Service Apps."""
        return self.get_redis_client(
            host=self.inputs.data.tc_playbook_db_path,
            port=self.inputs.data.tc_playbook_db_port,
            db=0,
        )

    def results_tc(self, key: str, value: str) -> None:
        """Write data to results_tc file in TcEX specified directory.

        The TcEx platform support persistent values between executions of the App.  This
        method will store the values for TC to read and put into the Database.

        Args:
            key: The data key to be stored.
            value: The data value to be stored.
        """
        if os.access(self.inputs.data.tc_out_path, os.W_OK):
            results_file = f'{self.inputs.data.tc_out_path}/results.tc'
        else:
            results_file = 'results.tc'

        new = True
        open(results_file, 'a').close()  # ensure file exists
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

    # TODO: [med] update to support scoped instance
    @cached_property
    def service(self) -> Union[ApiService, CommonServiceTrigger, WebhookTriggerService]:
        """Include the Service Module."""
        if self.ij.data.runtime_level.lower() == 'apiservice':
            from .services import ApiService as Service
        elif self.ij.data.runtime_level.lower() == 'triggerservice':
            from .services import CommonServiceTrigger as Service
        elif self.ij.data.runtime_level.lower() == 'webhooktriggerservice':
            from .services import WebhookTriggerService as Service
        else:
            self.exit(1, 'Could not determine the service type.')

        return Service(self)

    # TODO: [med] update to support scoped instance
    @cached_property
    def session(self) -> TcSession:
        """Return an instance of Requests Session configured for the ThreatConnect API."""
        return self.get_session()

    # TODO: [med] update to support scoped instance
    @cached_property
    def session_external(self) -> ExternalSession:
        """Return an instance of Requests Session configured for the ThreatConnect API."""
        return self.get_session_external()

    # TODO: [med] update to support scoped instance
    @cached_property
    def stix_model(self) -> StixModel:
        """Include the Threat Intel Module."""
        return StixModel(self.logger)

    # TODO: [med] update to support scoped instance
    @cached_property
    def ti(self) -> ThreatIntelligence:
        """Include the Threat Intel Module."""
        return self.get_ti()

    @cached_property
    def token(self) -> Tokens:
        """Return token object."""
        sleep_interval = int(os.getenv('TC_TOKEN_SLEEP_INTERVAL', '30'))
        return Tokens(self.inputs.data.tc_api_path, sleep_interval, self.inputs.data.tc_verify)

    @cached_property
    def utils(self) -> Utils:
        """Include the Utils module."""
        return Utils(temp_path=self.inputs.data.tc_temp_path)
