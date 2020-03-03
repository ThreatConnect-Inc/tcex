# -*- coding: utf-8 -*-
"""TcEx Framework"""
import inspect
import logging
import os
import platform
import re
import signal
import sys
import threading
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
        self._config = kwargs.get('config', {})
        # self._cm = None
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
        self._log = kwargs.get('logger')

        # init args (needs logger)
        self.inputs = Inputs(self, self._config, kwargs.get('config_file'))

        # include resources module
        # self._resources()

    def _association_types(self):
        """Retrieve Custom Indicator Associations types from the ThreatConnect API."""
        # Dynamically create custom indicator class
        r = self.session.get('/v2/types/associationTypes')

        # check for bad status code and response that is not JSON
        if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
            self.log.warning('Custom Indicators Associations are not supported.')
            return

        # validate successful API results
        data = r.json()
        if data.get('status') != 'Success':
            self.log.warning('Bad Status: Custom Indicators Associations are not supported.')
            return

        try:
            # Association Type Name is not a unique value at this time, but should be.
            for association in data.get('data', {}).get('associationType', []):
                self._indicator_associations_types_data[association.get('name')] = association
        except Exception as e:
            self.handle_error(200, [e])

    def _signal_handler(self, signal_interupt, frame):  # pylint: disable=unused-argument
        """Handle singal interrupt."""
        call_file = os.path.basename(inspect.stack()[1][0].f_code.co_filename)
        call_module = inspect.stack()[1][0].f_globals['__name__'].lstrip('Functions.')
        call_line = inspect.stack()[1][0].f_lineno
        self.log.error(
            f'App interrupted - file: {call_file}, method: {call_module}, line: {call_line}.'
        )
        if signal_interupt in (2, 15):
            self.exit(1, 'The App received an interrupt signal and will now exit.')

    def aot_rpush(self, exit_code):
        """Push message to AOT action channel."""
        if self.default_args.tc_playbook_db_type == 'Redis':
            try:
                self.redis_client.rpush(self.default_args.tc_exit_channel, exit_code)
            except Exception as e:  # pragma: no cover
                self.exit(1, f'Exception during AOT exit push ({e}).')

    @property
    def args(self):
        """Argparser args Namespace."""
        return self.inputs.args()

    def batch(
        self,
        owner,
        action=None,
        attribute_write_type=None,
        halt_on_error=False,
        playbook_triggers_enabled=None,
    ):
        """Return instance of Batch"""
        from .batch import Batch

        return Batch(
            self, owner, action, attribute_write_type, halt_on_error, playbook_triggers_enabled
        )

    def cache(self, domain, data_type, ttl_minutes=None, mapping=None):
        """Get instance of the Cache module.

        Args:
            domain (str): The domain can be either "system", "organization", or "local". When using
                "organization" the data store can be accessed by any Application in the entire org,
                while "local" access is restricted to the App writing the data. The "system" option
                should not be used in almost all cases.
            data_type (str): The data type descriptor (e.g., tc:whois:cache).
            ttl_minutes (int): The number of minutes the cache is valid.

        Returns:
            object: An instance of the Cache Class.
        """
        from .datastore import Cache

        return Cache(self, domain, data_type, ttl_minutes, mapping)

    @property
    def case_management(self):
        """Include the Threat Intel Module.

        .. Note:: Threat Intell methods can be accessed using ``tcex.ti.<method>``.
        """
        # if self._cm is None:
        #     from .case_management import CaseManagement

        #     self._cm = CaseManagement(self)
        # return self._cm
        from .case_management import CaseManagement

        return CaseManagement(self)

    @property
    def cm(self):
        """Include the Case Management Module."""
        return self.case_management

    def datastore(self, domain, data_type, mapping=None):
        """Get instance of the DataStore module.

        Args:
            domain (str): The domain can be either "system", "organization", or "local". When using
                "organization" the data store can be accessed by any Application in the entire org,
                while "local" access is restricted to the App writing the data. The "system" option
                should not be used in almost all cases.
            data_type (str): The data type descriptor (e.g., tc:whois:cache).

        Returns:
            object: An instance of the DataStore Class.
        """
        from .datastore import DataStore

        return DataStore(self, domain, data_type, mapping)

    @property
    def default_args(self):
        """Argparser args Namespace."""
        return self._default_args

    @property
    def error_codes(self):
        """Return TcEx error codes."""
        if self._error_codes is None:
            from .tcex_error_codes import TcExErrorCodes

            self._error_codes = TcExErrorCodes()
        return self._error_codes

    def exit(self, code=None, msg=None):
        """Application exit method with proper exit code

        The method will run the Python standard sys.exit() with the exit code
        previously defined via :py:meth:`~tcex.tcex.TcEx.exit_code` or provided
        during the call of this method.

        Args:
            code (Optional [integer]): The exit code value for the app.
            msg (Optional [string]): A message to log and add to message tc output.
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
    def exit_code(self):
        """Return the current exit code."""
        return self._exit_code

    @exit_code.setter
    def exit_code(self, code):
        """Set the App exit code.

        For TC Exchange Apps there are 3 supported exit codes.
        * 0 indicates a normal exit
        * 1 indicates a failure during execution
        * 3 indicates a partial failure

        Args:
            code (integer): The exit code value for the app.
        """
        if code is not None and code in [0, 1, 3]:
            self._exit_code = code
        else:
            self.log.warning('Invalid exit code')

    @staticmethod
    def expand_indicators(indicator):
        """Process indicators expanding file hashes/custom indicators into multiple entries.

        Args:
            indicator (string): " : " delimited string
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
    def group_types(self):
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
    def group_types_data(self):
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

    def get_type_from_api_entity(self, api_entity):
        """Return the object type as a string given a api entity.

        Args:
            api_entity:

        Returns:
            str|None: The type value or None.

        """
        merged = self.group_types_data.copy()
        merged.update(self.indicator_types_data)
        for (key, value) in merged.items():
            if value.get('apiEntity') == api_entity:
                return key
        return None

    def handle_error(self, code, message_values=None, raise_error=True):
        """Raise RuntimeError

        Args:
            code (integer): The error code from API or SDK.
            message (string): The error message from API or SDK.
            raise_error (bool, optional): Raise a Runtime error. Defaults to True.

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
            raise RuntimeError(1000, 'Generic Failure, see logs for more details.')
        except IndexError:
            self.log.error(
                f'Incorrect message values provided for error code {code} ({message_values}).'
            )
            raise RuntimeError(1000, 'Generic Failure, see logs for more details.')
        if raise_error:
            raise RuntimeError(code, message)

    @property
    def indicator_associations_types_data(self):
        """Return ThreatConnect associations type data.

        Retrieve the data from the API if it hasn't already been retrieved.

        Returns:
            (dictionary): A dictionary of ThreatConnect associations types.
        """
        if not self._indicator_associations_types_data:
            self._association_types()  # load custom indicator associations
        return self._indicator_associations_types_data

    @property
    def indicator_types(self):
        """Return ThreatConnect Indicator types.

        Retrieve the data from the API if it hasn't already been retrieved.

        Returns:
            (list): A list of ThreatConnect Indicator types.
        """
        if not self._indicator_types:
            self._indicator_types = self.indicator_types_data.keys()
        return self._indicator_types

    @property
    def indicator_types_data(self):
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
    def log(self):
        """Return a valid logger."""
        if self._log is None:
            self._log = self.logger.log
        return self._log

    @log.setter
    def log(self, log):
        """Return a valid logger."""
        if isinstance(log, logging.Logger):
            self._log = log

    @property
    def logger(self):
        """Return logger."""
        if self._logger is None:
            logger_name = self._config.get('tc_logger_name', 'tcex')
            self._logger = Logger(self, logger_name)
            self._logger.add_cache_handler('cache')
        return self._logger

    def metric(self, name, description, data_type, interval, keyed=False):
        """Get instance of the Metrics module.

        Args:
            name (string): The name for the metric.
            description (string): The description of the metric.
            data_type (string): The type of metric: Sum, Count, Min, Max, First, Last, and Average.
            interval (string): The metric interval: Hourly, Daily, Weekly, Monthly, and Yearly.
            keyed (boolean): Indicates whether the data will have a keyed value.

        Returns:
            (object): An instance of the Metrics Class.
        """
        from .metrics import Metrics

        return Metrics(self, name, description, data_type, interval, keyed)

    def message_tc(self, message, max_length=255):
        """Write data to message_tc file in TcEX specified directory.

        This method is used to set and exit message in the ThreatConnect Platform.
        ThreatConnect only supports files of max_message_length.  Any data exceeding
        this limit will be truncated. The last <max_length> characters will be preserved.

        Args:
            message (string): The message to add to message_tc file
            max_length (int, optional): The maximum length of an exit message. Defaults to 255.
        """
        if os.access(self.default_args.tc_out_path, os.W_OK):
            message_file = os.path.join(self.default_args.tc_out_path, 'message.tc')
        else:
            message_file = 'message.tc'

        if os.path.isfile(message_file):
            with open(message_file, 'r') as mh:
                message = mh.read() + message

        if not message.endswith('\n'):
            message += '\n'
        with open(message_file, 'w') as mh:
            # write last <max_length> characters to file
            mh.write(message[-max_length:])

    def notification(self):
        """Get instance of the Notification module.

        Returns:
            (object): An instance of the Notification Class.
        """
        from .notifications import Notifications

        return Notifications(self)

    @property
    def parser(self):
        """Instance tcex args parser."""
        return self.inputs.parser

    def pb(self, context, output_variables):
        """Return a new instance of playbook module.

        Args:
            context (str): The Redis context for Playbook or Service Apps.
            output_variables (list): A list of requested PB/Service output variables.

        Returns:
            tcex.playbook.Playbooks: An instance of Playbooks
        """
        from .playbooks import Playbooks

        return Playbooks(self, context, output_variables)

    @property
    def playbook(self):
        """Return an instance of Playbooks module.

        This property defaults context and outputvariables to arg values.

        .. Note:: Playbook methods can be accessed using ``tcex.playbook.<method>``.
        """
        if self._playbook is None:
            # handle outputs coming in as a csv string and list
            outputs = self.default_args.tc_playbook_out_variables or []
            if isinstance(outputs, str):
                outputs = outputs.split(',')
            self._playbook = self.pb(self.default_args.tc_playbook_db_context, outputs)
        return self._playbook

    @property
    def proxies(self):
        """Format the proxy configuration for Python Requests module.

        Generates a dictionary for use with the Python Requests module format
        when proxy is required for remote connections.

        **Example Response**
        ::

            {"http": "http://user:pass@10.10.1.10:3128/"}

        Returns:
           (dictionary): Dictionary of proxy settings
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
    def rargs(self):
        """Return argparser args Namespace with Playbook args automatically resolved."""
        return self.inputs.resolved_args()

    @staticmethod
    def rc(host, port, db=0, blocking=False, **kwargs):
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
    def redis_client(self):
        """Return redis client instance configure for Playbook/Service Apps."""
        if self._redis_client is None:
            from .key_value_store import RedisClient

            self._redis_client = RedisClient(
                host=self.default_args.tc_playbook_db_path,
                port=self.default_args.tc_playbook_db_port,
                db=0,
            ).client

        return self._redis_client

    def results_tc(self, key, value):
        """Write data to results_tc file in TcEX specified directory.

        The TcEx platform support persistent values between executions of the App.  This
        method will store the values for TC to read and put into the Database.

        Args:
            key (string): The data key to be stored.
            value (string): The data value to be stored.
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
    def safe_indicator(indicator):
        """Format indicator value for safe HTTP request.

        Args:
            indicator (string): Indicator to URL Encode
            errors (string): The error handler type.

        Returns:
            (string): The urlencoded string
        """
        if indicator is not None:
            indicator = quote(indicator, safe='~')
        return indicator

    @staticmethod
    def safe_rt(resource_type, lower=False):
        """Format the Resource Type.

        Takes Custom Indicator types with a space character and return a *safe* string.

        (e.g. *User Agent* is converted to User_Agent or user_agent.)

        Args:
           resource_type (string): The resource type to format.
           lower (boolean): Return type in all lower case

        Returns:
            (string): The formatted resource type.
        """
        if resource_type is not None:
            resource_type = resource_type.replace(' ', '_')
            if lower:
                resource_type = resource_type.lower()
        return resource_type

    @staticmethod
    def safe_group_name(group_name, group_max_length=100, ellipsis=True):
        """Truncate group name to match limit breaking on space and optionally add an ellipsis.

        .. note:: Currently the ThreatConnect group name limit is 100 characters.

        Args:
           group_name (string): The raw group name to be truncated.
           group_max_length (int): The max length of the group name.
           ellipsis (boolean): If true the truncated name will have '...' appended.

        Returns:
            (string): The truncated group name with optional ellipsis.
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
    def safe_tag(tag):
        """Encode and truncate tag to match limit (128 characters) of ThreatConnect API.

        Args:
           tag (string): The tag to be truncated

        Returns:
            (string): The truncated and quoted tag
        """
        if tag is not None:
            tag = quote(tag[:128], safe='~')
        return tag

    @staticmethod
    def safe_url(url):
        """Encode value for safe HTTP request.

        Args:
            url (string): The string to URL Encode.

        Returns:
            (string): The urlencoded string.
        """
        if url is not None:
            url = quote(url, safe='~')
        return url

    @property
    def service(self):
        """Include the Service Module.

        .. Note:: Service methods can be accessed using ``tcex.service.<method>``.
        """
        if self._service is None:
            from .services import Services

            self._service = Services(self)
        return self._service

    @property
    def session(self):
        """Return an instance of Requests Session configured for the ThreatConnect API."""
        if self._session is None:
            from .sessions import TcSession

            self._session = TcSession(self)
        return self._session

    @property
    def session_external(self):
        """Return an instance of Requests Session configured for the ThreatConnect API."""
        if self._session_external is None:
            from requests import Session

            self._session_external = Session()
            if self.default_args.tc_proxy_external:
                self.log.info(
                    'Using proxy server for external connectivity '
                    f'({self.default_args.tc_proxy_host}:{self.default_args.tc_proxy_port}).'
                )
                self._session_external.proxies = self.proxies
        return self._session_external

    @property
    def ti(self):
        """Include the Threat Intel Module.

        .. Note:: Threat Intell methods can be accessed using ``tcex.ti.<method>``.
        """
        if self._ti is None:
            from .threat_intelligence import ThreatIntelligence

            self._ti = ThreatIntelligence(self)
        return self._ti

    @property
    def token(self):
        """Return token object."""
        if self._token is None:
            sleep_interval = int(os.getenv('TC_TOKEN_SLEEP_INTERVAL', '30'))
            self._token = Tokens(
                self.default_args.tc_api_path, sleep_interval, self.default_args.tc_verify, self.log
            )
        return self._token

    @property
    def utils(self):
        """Include the Utils module.

        .. Note:: Utils methods can be accessed using ``tcex.utils.<method>``.
        """
        if self._utils is None:
            from .utils import Utils

            self._utils = Utils(self)
        return self._utils
