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
from typing import Optional
from urllib.parse import quote

from .app_config_object import InstallJson
from .inputs import Inputs
from .logger import Logger
from .tokens import Tokens


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
        # catch interupt signals
        if threading.current_thread().name == 'MainThread':
            signal.signal(signal.SIGINT, self._signal_handler)
            if platform.system() != 'Windows':
                signal.signal(signal.SIGHUP, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

        # Property defaults
        self._config: dict = kwargs.get('config') or {}
        self._default_args = None
        self._error_codes = None
        self._exit_code = 0
        self._indicator_associations_types_data = {}
        self._indicator_types = None
        self._indicator_types_data = None
        self._jobs = None
        self._logger = None
        self._playbook = None
        self._redis_client = None
        self._service = None
        self._session = None
        self._session_external = None
        self._utils = None
        self._ti = None
        self._token = None
        self.ij = InstallJson()

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
        if signal_interupt in (2, 15):
            self.exit(1, 'The App received an interrupt signal and will now exit.')

    def advanced_request(self, session: object, timeout: Optional[int] = 600) -> object:
        """Return instance of AdvancedRequest.

        Args:
            session (object): An instance of requests.Session.
            timeout (int): The number of second before timing out the request.

        Returns:
            object: An instance of AdvancedRequest
        """
        from .app_feature import AdvancedRequest

        return AdvancedRequest(session, self, timeout)

    def aot_rpush(self, exit_code: int) -> None:
        """Push message to AOT action channel."""
        if self.default_args.tc_playbook_db_type == 'Redis':
            try:
                self.redis_client.rpush(self.default_args.tc_exit_channel, exit_code)
            except Exception as e:  # pragma: no cover
                self.exit(1, f'Exception during AOT exit push ({e}).')

    @property
    def args(self) -> object:
        """Argparser args Namespace."""
        return self.inputs.args()

    def batch(
        self,
        owner: str,
        action: Optional[str] = None,
        attribute_write_type: Optional[str] = 'Replace',
        halt_on_error: Optional[bool] = False,
        playbook_triggers_enabled: Optional[bool] = False,
    ) -> object:
        """Return instance of Batch

        Args:
            tcex: An instance of TcEx object.
            owner: The ThreatConnect owner for Batch action.
            action default:Create): Action for the batch job ['Create', 'Delete'].
            attribute_write_type: Write type for TI attributes ['Append', 'Replace'].
            halt_on_error: If True any batch error will halt the batch job.
            playbook_triggers_enabled: Deprecated input, will not be used.

        Returns:
            object: An instance of the Batch Class.
        """
        from .batch import Batch

        return Batch(
            self, owner, action, attribute_write_type, halt_on_error, playbook_triggers_enabled
        )

    def cache(
        self,
        domain: str,
        data_type: str,
        ttl_seconds: Optional[int] = None,
        mapping: Optional[dict] = None,
    ) -> object:
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
    def case_management(self) -> object:
        """Include the Threat Intel Module.

        .. Note:: Threat Intell methods can be accessed using ``tcex.ti.<method>``.

        Returns:
            object: An instance of the CaseManagement Class.
        """
        from .case_management import CaseManagement

        return CaseManagement(self)

    @property
    def cm(self) -> object:
        """Include the Case Management Module."""
        return self.case_management

    def datastore(self, domain: str, data_type: str, mapping: Optional[dict] = None) -> object:
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
    def default_args(self) -> object:
        """Argparser args Namespace."""
        return self._default_args

    @property
    def error_codes(self) -> object:
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
        elif code in [0, 1, 3]:
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

    @property
    def group_types(self) -> list:
        """Return all defined ThreatConnect Group types.

        Returns:
            (list): A list of ThreatConnect Group types.
        """
        return [
            'Adversary',
            'Campaign',
            'Document',
            'Email',
            'Event',
            'Incident',
            'Intrusion Set',
            'Signature',
            'Report',
            'Threat',
            'Task',
        ]

    @property
    def group_types_data(self) -> dict:
        """Return supported ThreatConnect Group types."""
        return {
            'Adversary': {'apiBranch': 'adversaries', 'apiEntity': 'adversary'},
            'Campaign': {'apiBranch': 'campaigns', 'apiEntity': 'campaign'},
            'Document': {'apiBranch': 'documents', 'apiEntity': 'document'},
            'Email': {'apiBranch': 'emails', 'apiEntity': 'email'},
            'Event': {'apiBranch': 'events', 'apiEntity': 'event'},
            'Incident': {'apiBranch': 'incidents', 'apiEntity': 'incident'},
            'Intrusion Set': {'apiBranch': 'intrusionSets', 'apiEntity': 'intrusionSet'},
            'Report': {'apiBranch': 'reports', 'apiEntity': 'report'},
            'Signature': {'apiBranch': 'signatures', 'apiEntity': 'signature'},
            'Threat': {'apiBranch': 'threats', 'apiEntity': 'threat'},
            'Task': {'apiBranch': 'tasks', 'apiEntity': 'task'},
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
    def log(self) -> object:
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
    def logger(self) -> object:
        """Return logger."""
        if self._logger is None:
            logger_name = self._config.get('tc_logger_name', 'tcex')
            self._logger = Logger(self, logger_name)
            self._logger.add_cache_handler('cache')
        return self._logger

    def metric(
        self,
        name: str,
        description: str,
        data_type: str,
        interval: str,
        keyed: Optional[bool] = False,
    ) -> object:
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

        if os.path.isfile(message_file):
            with open(message_file) as mh:
                message = mh.read() + message

        if not message.endswith('\n'):
            message += '\n'
        with open(message_file, 'w') as mh:
            # write last <max_length> characters to file
            mh.write(message[-max_length:])

    def notification(self) -> object:
        """Get instance of the Notification module.

        Returns:
            (object): An instance of the Notification Class.
        """
        from .notifications import Notifications

        return Notifications(self)

    @property
    def parser(self) -> object:
        """Instance tcex args parser."""
        return self.inputs.parser

    def pb(self, context: str, output_variables: list) -> object:
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
    def playbook(self) -> object:
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
            self._playbook: object = self.pb(self.default_args.tc_playbook_db_context, outputs)
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
            proxies = {'http': f'http://{proxy_url}', 'https': f'https://{proxy_url}'}
        return proxies

    @property
    def rargs(self) -> object:
        """Return argparser args Namespace with Playbook args automatically resolved."""
        return self.inputs.resolved_args()

    @staticmethod
    def rc(host, port, db=0, blocking=False, **kwargs) -> object:
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
    def redis_client(self) -> object:
        """Return redis client instance configure for Playbook/Service Apps."""
        if self._redis_client is None:
            from .key_value_store import RedisClient

            self._redis_client = RedisClient(
                host=self.default_args.tc_playbook_db_path,
                port=self.default_args.tc_playbook_db_port,
                db=0,
            ).client

        return self._redis_client

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
    ):
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
    def service(self) -> object:
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
    def session(self) -> object:
        """Return an instance of Requests Session configured for the ThreatConnect API."""
        if self._session is None:
            from .sessions import TcSession

            self._session = TcSession(
                logger=self.log,
                api_access_id=self.default_args.api_access_id,
                api_secret_key=self.default_args.api_secret_key,
                base_url=self.default_args.tc_api_path,
            )

            # set verify
            self._session.verify = self.default_args.tc_verify

            # set token
            self._session.token = self.token

            # update User-Agent
            self._session.headers.update(
                {'User-Agent': f'TcEx: {__import__(__name__).__version__}'}
            )

            # add proxy support if requested
            if self.default_args.tc_proxy_tc:
                self._session.proxies = self.proxies
                self.log.info(
                    f'Using proxy host {self.args.tc_proxy_host}:'
                    f'{self.args.tc_proxy_port} for ThreatConnect session.'
                )
        return self._session

    @property
    def session_external(self) -> object:
        """Return an instance of Requests Session configured for the ThreatConnect API."""
        if self._session_external is None:
            from .sessions import ExternalSession

            self._session_external = ExternalSession(logger=self.log)

            # add User-Agent to headers
            self._session_external.headers.update(
                {'User-Agent': f'TcEx App: {self.ij.display_name} - {self.ij.program_version}'}
            )

            # add proxy support if requested
            if self.default_args.tc_proxy_external:
                self._session_external.proxies = self.proxies
                self.log.info(
                    f'Using proxy host {self.args.tc_proxy_host}:'
                    f'{self.args.tc_proxy_port} for external session.'
                )
        return self._session_external

    @property
    def ti(self) -> object:
        """Include the Threat Intel Module.

        .. Note:: Threat Intell methods can be accessed using ``tcex.ti.<method>``.
        """
        if self._ti is None:
            from .threat_intelligence import ThreatIntelligence

            self._ti = ThreatIntelligence(self)
        return self._ti

    @property
    def token(self) -> object:
        """Return token object."""
        if self._token is None:
            sleep_interval = int(os.getenv('TC_TOKEN_SLEEP_INTERVAL', '30'))
            self._token = Tokens(
                self.default_args.tc_api_path, sleep_interval, self.default_args.tc_verify, self.log
            )
        return self._token

    @property
    def utils(self) -> object:
        """Include the Utils module.

        .. Note:: Utils methods can be accessed using ``tcex.utils.<method>``.
        """
        if self._utils is None:
            from .utils import Utils

            self._utils = Utils(temp_path=self.default_args.tc_temp_path)
        return self._utils
