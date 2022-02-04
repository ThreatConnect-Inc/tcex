"""TcEx Framework"""

# standard library
import inspect
import logging
import os
import platform
import re
import signal
import sys
import threading
from base64 import b64decode
from functools import lru_cache
from typing import Optional, Union
from urllib.parse import quote

from .app_config_object import InstallJson
from .inputs import Inputs
from .logger import Logger, TraceLogger
from .tokens import Tokens

# init tcex logger
logging.setLoggerClass(TraceLogger)
logger = logging.getLogger('tcex')
logger.setLevel(logging.TRACE)  # pylint: disable=E1101


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
        try:
            # catch interupt signals specifically based on thread name
            signal.signal(signal.SIGINT, self._signal_handler)
            if platform.system() != 'Windows':
                signal.signal(signal.SIGHUP, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        except ValueError:  # catch signal being added to thread that is not main
            pass

        # Property defaults
        self._config: dict = kwargs.get('config') or {}
        self._default_args = None
        self._error_codes = None
        self._exit_code = 0
        self._indicator_associations_types_data = {}
        self._indicator_types = None
        self._indicator_types_data = None
        self._jobs = None
        self._key_value_store = None
        self._logger = None
        self._playbook = None
        self._redis_client = None
        self._service = None
        self._session = None
        self._session_external = None
        self._stix_model = None
        self._utils = None
        self._token = None
        self.ij = InstallJson()
        self.main_os_pid = os.getpid()

        # add custom logger if provided
        self._log: object = kwargs.get('logger')

        # init args (needs logger)
        self.inputs = Inputs(self, self._config, kwargs.get('config_file'))

    def _association_types(self):
        """Retrieve Custom Indicator Associations types from the ThreatConnect API."""
        # Dynamically create custom indicator class
        r: object = self.session.get('/v2/types/associationTypes')

        # check for bad status code and response that is not JSON
        if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
            self.log.warning('feature=tcex, event=association-types-download, status=failure')
            return

        # validate successful API results
        data: dict = r.json()
        if data.get('status') != 'Success':
            self.log.warning('feature=tcex, event=association-types-download, status=failure')
            return

        try:
            # Association Type Name is not a unique value at this time, but should be.
            for association in data.get('data', {}).get('associationType', []):
                self._indicator_associations_types_data[association.get('name')] = association
        except Exception as e:
            self.handle_error(200, [e])

    def _signal_handler(
        self, signal_interupt: int, frame: object  # pylint: disable=unused-argument
    ) -> None:
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

    @property
    def _user_agent(self):
        """Return a User-Agent string."""
        return {
            'User-Agent': (
                f'TcEx/{__import__(__name__).__version__}, '
                f'{self.ij.display_name}/{self.ij.program_version}'
            )
        }

    def advanced_request(
        self, session: object, timeout: Optional[int] = 600, output_prefix: Optional[str] = None
    ) -> 'AdvancedRequest':  # noqa: F821
        """Return instance of AdvancedRequest.

        Args:
            session (object): An instance of requests.Session.
            timeout (int): The number of second before timing out the request.

        Returns:
            object: An instance of AdvancedRequest
        """
        from .app_feature import AdvancedRequest

        return AdvancedRequest(session, self, timeout, output_prefix)

    def aot_rpush(self, exit_code: int) -> None:
        """Push message to AOT action channel."""
        if self.default_args.tc_playbook_db_type == 'Redis':
            try:
                self.redis_client.rpush(self.default_args.tc_exit_channel, exit_code)
            except Exception as e:  # pragma: no cover
                self.exit(1, f'Exception during AOT exit push ({e}).')

    @property
    def args(self) -> 'Namespace':  # noqa: F821
        """Argparser args Namespace."""
        return self.inputs.args()

    def batch(
        self,
        owner: str,
        action: Optional[str] = 'Create',
        attribute_write_type: Optional[str] = 'Replace',
        halt_on_error: Optional[bool] = False,
        playbook_triggers_enabled: Optional[bool] = False,
        tag_write_type: Optional[str] = 'Replace',
        security_label_write_type: Optional[str] = 'Replace',
    ) -> 'Batch':  # noqa: F821
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

        Returns:
            object: An instance of the Batch Class.
        """
        from .batch import Batch

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
    ) -> 'BatchSubmit':  # noqa: F821
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

        Returns:
            object: An instance of the Batch Class.
        """
        from .batch.batch_submit import BatchSubmit

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

    def batch_writer(self, output_dir: str, **kwargs) -> 'BatchWriter':  # noqa: F821
        """Return instance of Batch

        Args:
            tcex: An instance of TcEx object.
            output_dir: Deprecated input, will not be used.
            output_extension (kwargs: str): Append this extension to output files.
            write_callback (kwargs: Callable): A callback method to call when a batch json file
                is written. The callback will be passed the fully qualified name of the written
                file.
            write_callback_kwargs (kwargs: dict): Additional values to send to callback method.

        Returns:
            object: An instance of the Batch Class.
        """
        from .batch.batch_writer import BatchWriter

        return BatchWriter(self, output_dir, **kwargs)

    def cache(
        self,
        domain: str,
        data_type: str,
        ttl_seconds: Optional[int] = None,
        mapping: Optional[dict] = None,
    ) -> 'Cache':  # noqa: F821
        """Get instance of the Cache module.

        Args:
            domain: The domain can be either "system", "organization", or "local". When using
                "organization" the data store can be accessed by any Application in the entire org,
                while "local" access is restricted to the App writing the data. The "system" option
                should not be used in almost all cases.
            data_type: The data type descriptor (e.g., tc:whois:cache).
            ttl_seconds: The number of seconds the cache is valid.
            mapping: Advanced - The datastore mapping if required.

        Returns:
            object: An instance of the Cache Class.
        """
        from .datastore import Cache

        return Cache(self, domain, data_type, ttl_seconds, mapping)

    @property
    def case_management(self) -> 'CaseManagement':  # noqa: F821
        """Include the Threat Intel Module.

        .. Note:: Threat Intell methods can be accessed using ``tcex.ti.<method>``.

        Returns:
            object: An instance of the CaseManagement Class.
        """
        from .case_management import CaseManagement

        return CaseManagement(self)

    @property
    def cm(self) -> 'CaseManagement':  # noqa: F821
        """Include the Case Management Module."""
        return self.case_management

    def datastore(
        self, domain: str, data_type: str, mapping: Optional[dict] = None
    ) -> 'DataStore':  # noqa: F821
        """Get instance of the DataStore module.

        Args:
            domain: The domain can be either "system", "organization", or "local". When using
                "organization" the data store can be accessed by any Application in the entire org,
                while "local" access is restricted to the App writing the data. The "system" option
                should not be used in almost all cases.
            data_type: The data type descriptor (e.g., tc:whois:cache).
            mapping: ElasticSearch mappings data.

        Returns:
            object: An instance of the DataStore Class.
        """
        from .datastore import DataStore

        return DataStore(self, domain, data_type, mapping)

    @property
    def default_args(self) -> 'Namespace':  # noqa: F821
        """Argparser args Namespace."""
        return self._default_args

    @property
    def error_codes(self) -> 'TcExErrorCodes':  # noqa: F821
        """Return TcEx error codes."""
        if self._error_codes is None:
            from .tcex_error_codes import TcExErrorCodes

            self._error_codes = TcExErrorCodes()
        return self._error_codes

    def exit(self, code: Optional[int] = None, msg: Optional[str] = None) -> None:
        """Application exit method with proper exit code

        The method will run the Python standard sys.exit() with the exit code
        previously defined via :py:meth:`~tcex.tcex.TcEx.exit_code` or provided
        during the call of this method.

        Args:
            code: The exit code value for the app.
            msg: A message to log and add to message tc output.
        """
        # add exit message to message.tc file and log
        if msg is not None:
            if code in [0, 3] or (code is None and self.exit_code in [0, 3]):
                self.log.info(msg)
            else:
                self.log.error(msg)
            self.message_tc(msg)

        if code is None:
            code = self.exit_code
        elif code in [0, 1, 3, 4]:
            pass
        else:
            self.log.error('Invalid exit code')
            code = 1

        if self.default_args.tc_aot_enabled:
            # push exit message
            self.aot_rpush(code)

        # exit token renewal thread
        self.token.shutdown = True

        self.log.info(f'Exit Code: {code}')
        sys.exit(code)

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

    @staticmethod
    def expand_indicators(indicator: str) -> list:
        """Process indicators expanding file hashes/custom indicators into multiple entries.

        Args:
            indicator: An " : " delimited string.

        Returns:
            (list): a list of indicators split on " : ".
        """
        if indicator.count(' : ') > 0:
            # handle all multi-valued indicators types (file hashes and custom indicators)
            indicator_list = []

            # group 1 - lazy capture everything to first <space>:<space> or end of line
            iregx_pattern = r'^(.*?(?=\s\:\s|$))?'
            iregx_pattern += r'(?:\s\:\s)?'  # remove <space>:<space>
            # group 2 - look behind for <space>:<space>, lazy capture everything
            #           to look ahead (optional <space>):<space> or end of line
            iregx_pattern += r'((?<=\s\:\s).*?(?=(?:\s)?\:\s|$))?'
            iregx_pattern += r'(?:(?:\s)?\:\s)?'  # remove (optional <space>):<space>
            # group 3 - look behind for <space>:<space>, lazy capture everything
            #           to look ahead end of line
            iregx_pattern += r'((?<=\s\:\s).*?(?=$))?$'
            iregx = re.compile(iregx_pattern)

            indicators = iregx.search(indicator)
            if indicators is not None:
                indicator_list = list(indicators.groups())
        else:
            # handle all single valued indicator types (address, host, etc)
            indicator_list = [indicator]

        return indicator_list

    # TODO: [high] testing ... organize this later
    def get_session(self) -> 'TcSession':  # noqa: F821
        """Return an instance of Requests Session configured for the ThreatConnect API."""
        from .sessions import TcSession

        _session = TcSession(
            logger=self.log,
            api_access_id=self.default_args.api_access_id,
            api_secret_key=self.default_args.api_secret_key,
            base_url=self.default_args.tc_api_path,
        )

        # set verify
        _session.verify = self.default_args.tc_verify

        # set token
        _session.token = self.token

        # update User-Agent
        _session.headers.update(self._user_agent)

        # add proxy support if requested
        if self.default_args.tc_proxy_tc:
            _session.proxies = self.proxies
            self.log.info(
                f'Using proxy host {self.default_args.tc_proxy_host}:'
                f'{self.default_args.tc_proxy_port} for ThreatConnect session.'
            )

        # enable curl logging if tc_log_curl param is set.
        if self.default_args.tc_log_curl:
            _session.log_curl = True

        # return session
        return _session

    def get_ti(self) -> 'ThreatIntelligence':  # noqa: F821
        """Include the Threat Intel Module.

        .. Note:: Threat Intel methods can be accessed using ``tcex.ti.<method>``.
        """
        from .threat_intelligence import ThreatIntelligence

        return ThreatIntelligence(session=self.get_session())

    @property
    def group_types(self) -> list:
        """Return all defined ThreatConnect Group types.

        Returns:
            (list): A list of ThreatConnect Group types.
        """
        return list(self.group_types_data.keys())

    @property
    def group_types_data(self) -> dict:
        """Return supported ThreatConnect Group types."""
        return {
            'Adversary': {'apiBranch': 'adversaries', 'apiEntity': 'adversary'},
            'Attack Pattern': {'apiBranch': 'attackPatterns', 'apiEntity': 'attackPattern'},
            'Campaign': {'apiBranch': 'campaigns', 'apiEntity': 'campaign'},
            'Course of Action': {'apiBranch': 'coursesOfAction', 'apiEntity': 'courseOfAction'},
            'Document': {'apiBranch': 'documents', 'apiEntity': 'document'},
            'Email': {'apiBranch': 'emails', 'apiEntity': 'email'},
            'Event': {'apiBranch': 'events', 'apiEntity': 'event'},
            'Incident': {'apiBranch': 'incidents', 'apiEntity': 'incident'},
            'Intrusion Set': {'apiBranch': 'intrusionSets', 'apiEntity': 'intrusionSet'},
            'Malware': {'apiBranch': 'malware', 'apiEntity': 'malware'},
            'Report': {'apiBranch': 'reports', 'apiEntity': 'report'},
            'Signature': {'apiBranch': 'signatures', 'apiEntity': 'signature'},
            'Tactic': {'apiBranch': 'tactics', 'apiEntity': 'tactic'},
            'Task': {'apiBranch': 'tasks', 'apiEntity': 'task'},
            'Threat': {'apiBranch': 'threats', 'apiEntity': 'threat'},
            'Tool': {'apiBranch': 'tools', 'apiEntity': 'tool'},
            'Vulnerability': {'apiBranch': 'vulnerabilities', 'apiEntity': 'vulnerability'},
        }

    def get_type_from_api_entity(self, api_entity: dict) -> Optional[str]:
        """Return the object type as a string given a api entity.

        Args:
            api_entity: A TCEntity object.

        Returns:
            str, None: The type value or None.

        """
        merged = self.group_types_data.copy()
        merged.update(self.indicator_types_data)
        for key, value in merged.items():
            if value.get('apiEntity') == api_entity:
                return key
        return None

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

    @property
    def indicator_associations_types_data(self) -> dict:
        """Return ThreatConnect associations type data.

        Retrieve the data from the API if it hasn't already been retrieved.

        Returns:
            (dict): A dictionary of ThreatConnect associations types.
        """
        if not self._indicator_associations_types_data:
            self._association_types()  # load custom indicator associations
        return self._indicator_associations_types_data

    @property
    def indicator_types(self) -> list:
        """Return ThreatConnect Indicator types.

        Retrieve the data from the API if it hasn't already been retrieved.

        Returns:
            (list): A list of ThreatConnect Indicator types.
        """
        if not self._indicator_types:
            self._indicator_types = self.indicator_types_data.keys()
        return self._indicator_types

    @property
    def indicator_types_data(self) -> dict:
        """Return ThreatConnect indicator types data.

        Retrieve the data from the API if it hasn't already been retrieved.

        Returns:
            (dict): A dictionary of ThreatConnect Indicator data.
        """
        if not self._indicator_types_data:
            self._indicator_types_data = {}

            # retrieve data from API
            r = self.session.get('/v2/types/indicatorTypes')
            # TODO: use handle error instead
            if not r.ok:
                raise RuntimeError('Could not retrieve indicator types from ThreatConnect API.')

            for itd in r.json().get('data', {}).get('indicatorType'):
                self._indicator_types_data[itd.get('name')] = itd
        return self._indicator_types_data

    @property
    def key_value_store(self) -> Union['KeyValueRedis', 'KeyValueApi']:  # noqa: F821
        """Return the correct KV store for this execution.

        The TCKeyValueAPI KV store is limited to two operations (create and read),
        while the Redis kvstore wraps a few other Redis methods.
        """
        if self._key_value_store is None:
            if self.default_args.tc_playbook_db_type == 'Redis':
                from .key_value_store import KeyValueRedis

                self._key_value_store = KeyValueRedis(self.redis_client)
            elif self.default_args.tc_playbook_db_type == 'TCKeyValueAPI':
                from .key_value_store import KeyValueApi

                # providing runtime_level to KeyValueApi for service Apps so that the new
                # API endpoint (in TC 6.0.7) can be used with the context. this new
                # endpoint could be used for PB Apps, however to support versions of
                # TC < 6.0.7 the old endpoint must still be used.
                self._key_value_store = KeyValueApi(self.session, self.ij.runtime_level.lower())
            else:  # pragma: no cover
                raise RuntimeError(f'Invalid DB Type: ({self.default_args.tc_playbook_db_type})')
        return self._key_value_store

    @property
    def log(self) -> 'TraceLogger':  # noqa: F821
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
    ) -> 'Metrics':  # noqa: F821
        """Get instance of the Metrics module.

        Args:
            name: The name for the metric.
            description: The description of the metric.
            data_type: The type of metric: Sum, Count, Min, Max, First, Last, and Average.
            interval: The metric interval: Hourly, Daily, Weekly, Monthly, and Yearly.
            keyed: Indicates whether the data will have a keyed value.

        Returns:
            (object): An instance of the Metrics Class.
        """
        from .metrics import Metrics

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

        if os.access(self.default_args.tc_out_path, os.W_OK):
            message_file = os.path.join(self.default_args.tc_out_path, 'message.tc')
        else:
            message_file = 'message.tc'

        if not message.endswith('\n'):
            message += '\n'
        with open(message_file, 'w') as mh:
            # write last <max_length> characters to file
            mh.write(message[-max_length:])

    def notification(self) -> 'Notifications':  # noqa: F821
        """Get instance of the Notification module.

        Returns:
            (object): An instance of the Notification Class.
        """
        from .notifications import Notifications

        return Notifications(self)

    @property
    def parser(self) -> 'TcArgumentParser':  # noqa: F821
        """Instance tcex args parser."""
        return self.inputs.parser

    def pb(self, context: str, output_variables: list) -> 'Playbooks':  # noqa: F821
        """Return a new instance of playbook module.

        Args:
            context: The Redis context for Playbook or Service Apps.
            output_variables: A list of requested PB/Service output variables.

        Returns:
            tcex.playbook.Playbooks: An instance of Playbooks
        """
        from .playbooks import Playbooks

        return Playbooks(self, context, output_variables)

    @property
    def playbook(self) -> 'Playbooks':  # noqa: F821
        """Return an instance of Playbooks module.

        This property defaults context and outputvariables to arg values.

        .. Note:: Playbook methods can be accessed using ``tcex.playbook.<method>``.

        Returns:
            tcex.playbook.Playbooks: An instance of Playbooks
        """
        if self._playbook is None:
            # handle outputs coming in as a csv string and list
            outputs: list = self.default_args.tc_playbook_out_variables or []
            if isinstance(outputs, str):
                outputs = outputs.split(',')
            self._playbook = self.pb(self.default_args.tc_playbook_db_context, outputs)
        return self._playbook

    @property
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
        proxies = {}
        if (
            self.default_args.tc_proxy_host is not None
            and self.default_args.tc_proxy_port is not None
        ):

            if (
                self.default_args.tc_proxy_username is not None
                and self.default_args.tc_proxy_password is not None
            ):
                tc_proxy_username = quote(self.default_args.tc_proxy_username, safe='~')
                tc_proxy_password = quote(self.default_args.tc_proxy_password, safe='~')

                # proxy url with auth
                proxy_url = (
                    f'{tc_proxy_username}:{tc_proxy_password}'
                    f'@{self.default_args.tc_proxy_host}:{self.default_args.tc_proxy_port}'
                )
            else:
                # proxy url without auth
                proxy_url = f'{self.default_args.tc_proxy_host}:{self.default_args.tc_proxy_port}'
            proxies = {'http': f'http://{proxy_url}', 'https': f'http://{proxy_url}'}
        return proxies

    @property
    def rargs(self) -> 'Namespace':  # noqa: F821
        """Return argparser args Namespace with Playbook args automatically resolved."""
        return self.inputs.resolved_args()

    @staticmethod
    def rc(host, port, db=0, blocking=False, **kwargs) -> 'RedisClient':  # noqa: F821
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
        from .key_value_store import RedisClient

        return RedisClient(host=host, port=port, db=db, blocking=blocking, **kwargs).client

    @property
    def redis_client(self) -> 'RedisClient':  # noqa: F821
        """Return redis client instance configure for Playbook/Service Apps."""
        if self._redis_client is None:
            from .key_value_store import RedisClient

            self._redis_client = RedisClient(
                host=self.default_args.tc_playbook_db_path,
                port=self.default_args.tc_playbook_db_port,
                db=0,
            ).client

        return self._redis_client

    def resolve_variable(self, provider: str, lookup: str, id_: str) -> Union[bytes, str]:
        """Resolve TEXT/KEYCHAIN/FILE variables.

        Feature: PLAT-2688

        Data Format:
        {
            "data": "value"
        }

        Args:
            provider: The variable value provider (e.g. TC).
            lookup: The value to lookup (the key).
            id_: The id/type field (e.g. TEXT/KEYCHAIN/FILE).
        """
        data = None

        # retrieve value from API
        r = self.session.get(f'/internal/variable/runtime/{provider}/{lookup}')
        if r.ok:
            try:
                data = r.json().get('data')

                if id_.lower() == 'file':
                    data = b64decode(data)  # returns bytes
                elif id_.lower() == 'keychain':
                    self.logger.filter_sensitive.add(data)

            except Exception as ex:
                raise RuntimeError(
                    f'Could not retrieve variable: provider={provider}, key={lookup}, type={id_}.'
                ) from ex
        else:
            raise RuntimeError(
                f'Could not retrieve variable: provider={provider}, key={lookup}, type={id_}.'
            )

        return data

    def results_tc(self, key: str, value: str) -> None:
        """Write data to results_tc file in TcEX specified directory.

        The TcEx platform support persistent values between executions of the App.  This
        method will store the values for TC to read and put into the Database.

        Args:
            key: The data key to be stored.
            value: The data value to be stored.
        """
        if os.access(self.default_args.tc_out_path, os.W_OK):
            results_file = f'{self.default_args.tc_out_path}/results.tc'
        else:
            results_file = 'results.tc'

        new = True
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

    @staticmethod
    def safe_indicator(indicator: str) -> str:
        """Format indicator value for safe HTTP request.

        Args:
            indicator: Indicator to URL Encode

        Returns:
            (str): The urlencoded string
        """
        if indicator is not None:
            indicator = quote(indicator, safe='~')
        return indicator

    @staticmethod
    def safe_rt(resource_type: str, lower: Optional[bool] = False) -> str:
        """Format the Resource Type.

        Takes Custom Indicator types with a space character and return a *safe* string.

        (e.g. *User Agent* is converted to User_Agent or user_agent.)

        Args:
           resource_type: The resource type to format.
           lower: Return type in all lower case

        Returns:
            (str): The formatted resource type.
        """
        if resource_type is not None:
            resource_type = resource_type.replace(' ', '_')
            if lower:
                resource_type = resource_type.lower()
        return resource_type

    @staticmethod
    def safe_group_name(
        group_name: str, group_max_length: Optional[int] = 100, ellipsis: Optional[bool] = True
    ) -> str:
        """Truncate group name to match limit breaking on space and optionally add an ellipsis.

        .. note:: Currently the ThreatConnect group name limit is 100 characters.

        Args:
           group_name: The raw group name to be truncated.
           group_max_length: The max length of the group name.
           ellipsis: If true the truncated name will have '...' appended.

        Returns:
            (str): The truncated group name with optional ellipsis.
        """
        ellipsis_value = ''
        if ellipsis:
            ellipsis_value = ' ...'

        if group_name is not None and len(group_name) > group_max_length:
            # split name by spaces and reset group_name
            group_name_array = group_name.split(' ')
            group_name = ''
            for word in group_name_array:
                word = f'{word}'
                if (len(group_name) + len(word) + len(ellipsis_value)) >= group_max_length:
                    group_name = f'{group_name}{ellipsis_value}'
                    group_name = group_name.lstrip(' ')
                    break
                group_name += f' {word}'
        return group_name

    @staticmethod
    def safe_tag(tag: str) -> str:
        """Encode and truncate tag to match limit (128 characters) of ThreatConnect API.

        Args:
           tag: The tag to be truncated

        Returns:
            (str): The truncated and quoted tag.
        """
        if tag is not None:
            tag = quote(tag[:128], safe='~')
        return tag

    @staticmethod
    def safe_url(url: str) -> str:
        """Encode value for safe HTTP request.

        Args:
            url (str): The string to URL Encode.

        Returns:
            (str): The urlencoded string.
        """
        if url is not None:
            url: str = quote(url, safe='~')
        return url

    @property
    def service(self) -> 'CommonService':  # noqa: F821
        """Include the Service Module.

        .. Note:: Service methods can be accessed using ``tcex.service.<method>``.
        """
        if self._service is None:
            if self.ij.runtime_level.lower() == 'apiservice':
                from .services import ApiService as Service
            elif self.ij.runtime_level.lower() == 'triggerservice':
                from .services import CommonServiceTrigger as Service
            elif self.ij.runtime_level.lower() == 'webhooktriggerservice':
                from .services import WebhookTriggerService as Service
            else:
                self.exit(1, 'Could not determine the service type.')

            self._service = Service(self)
        return self._service

    @property
    def session(self) -> 'TcSession':  # noqa: F821
        """Return an instance of Requests Session configured for the ThreatConnect API."""
        if self._session is None:
            self._session = self.get_session()
        return self._session

    @property
    def session_external(self) -> 'ExternalSession':  # noqa: F821
        """Return an instance of Requests Session configured for the ThreatConnect API."""
        if self._session_external is None:
            from .sessions import ExternalSession

            self._session_external = ExternalSession(logger=self.log)

            # add User-Agent to headers
            self._session_external.headers.update(self._user_agent)

            # add proxy support if requested
            if self.default_args.tc_proxy_external:
                self._session_external.proxies = self.proxies
                self.log.info(
                    f'Using proxy host {self.default_args.tc_proxy_host}:'
                    f'{self.default_args.tc_proxy_port} for external session.'
                )

            if self.default_args.tc_log_curl:
                self._session_external.log_curl = True
        return self._session_external

    @property
    def stix_model(self) -> 'StixModel':  # noqa: F821
        """Include the Threat Intel Module.

        .. Note:: Threat Intell methods can be accessed using ``tcex.ti.<method>``.
        """
        if self._stix_model is None:
            from .stix import StixModel

            self._stix_model = StixModel(self.logger)
        return self._stix_model

    @property
    @lru_cache()
    def ti(self) -> 'ThreatIntelligence':  # noqa: F821
        """Include the Threat Intel Module.

        .. Note:: Threat Intel methods can be accessed using ``tcex.ti.<method>``.
        """
        return self.get_ti()

    @property
    def token(self) -> Tokens:
        """Return token object."""
        if self._token is None:
            proxies = None
            if self.default_args.tc_proxy_tc:
                proxies = self.proxies
            sleep_interval = int(os.getenv('TC_TOKEN_SLEEP_INTERVAL', '30'))
            self._token = Tokens(
                self.default_args.tc_api_path,
                sleep_interval,
                self.default_args.tc_verify,
                self.log,
                proxies,
            )
        return self._token

    @property
    def utils(self) -> 'Utils':  # noqa: F821
        """Include the Utils module.

        .. Note:: Utils methods can be accessed using ``tcex.utils.<method>``.
        """
        if self._utils is None:
            from .utils import Utils

            self._utils = Utils(temp_path=self.default_args.tc_temp_path)
        return self._utils

    @property
    def victim_asset_types(self) -> list:
        """Return all defined ThreatConnect Asset types.

        Returns:
            (list): A list of ThreatConnect Asset types.
        """
        return [
            'EmailAddress',
            'SocialNetwork',
            'NetworkAccount',
            'WebSite',
            'Phone',
        ]
