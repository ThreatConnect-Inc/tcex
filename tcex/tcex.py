# -*- coding: utf-8 -*-
"""TcEx Framework"""
from builtins import str
import inspect
import json
import logging
import platform
import os
import re
import signal
import sys

try:
    from urllib import quote  # Python 2
except ImportError:
    from urllib.parse import quote  # Python 3

from .tcex_args import TcExArgs


class TcEx(object):
    """Provides basic functionality for all types of TxEx Apps."""

    def __init__(self):
        """Initialize Class Properties."""
        # catch interupt signals
        signal.signal(signal.SIGINT, self._signal_handler)
        if platform.system() != 'Windows':
            signal.signal(signal.SIGHUP, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        # init logger
        self.log = logging.getLogger('tcex')
        self._logger_stream()
        # Property defaults
        self._error_codes = None
        self._exit_code = 0
        self._install_json = None
        self._install_json_params = {}
        self._indicator_associations_types_data = {}
        self._indicator_types = []
        self._indicator_types_data = {}
        self._jobs = None
        self._playbook = None
        self._session = None
        self._utils = None
        self._ti = None

        # Parser
        self.tcex_args = TcExArgs(self)

        # NOTE: odd issue where args is not updating properly
        if self.default_args.tc_token is not None:
            self._tc_token = self.default_args.tc_token
        if self.default_args.tc_token_expires is not None:
            self._tc_token_expires = self.default_args.tc_token_expires

        # Log system and App data
        self._log()

        # include resources module
        self._resources()

    def _association_types(self):
        """Retrieve Custom Indicator Associations types from the ThreatConnect API."""
        # Dynamically create custom indicator class
        r = self.session.get('/v2/types/associationTypes')

        # check for bad status code and response that is not JSON
        if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
            warn = u'Custom Indicators Associations are not supported.'
            self.log.warning(warn)
            return

        # validate successful API results
        data = r.json()
        if data.get('status') != 'Success':
            warn = u'Bad Status: Custom Indicators Associations are not supported.'
            self.log.warning(warn)
            return

        try:
            # Association Type Name is not a unique value at this time, but should be.
            for association in data.get('data', {}).get('associationType', []):
                self._indicator_associations_types_data[association.get('name')] = association
        except Exception as e:
            self.handle_error(200, [e])

    def _log(self):
        """Send System and App data to logs."""
        self._log_platform()
        self._log_app_data()
        self._log_python_version()
        self._log_tcex_version()
        self._log_tc_proxy()

    def _log_app_data(self):
        """Log the App data information."""
        # Best Effort
        if self.install_json:
            app_commit_hash = self.install_json.get('commitHash')
            app_features = ','.join(self.install_json.get('features', []))
            app_min_ver = self.install_json.get('minServerVersion', 'N/A')
            app_name = self.install_json.get('displayName')
            app_runtime_level = self.install_json.get('runtimeLevel')
            app_version = self.install_json.get('programVersion')

            self.log.info(u'App Name: {}'.format(app_name))
            if app_features:
                self.log.info(u'App Features: {}'.format(app_features))
            self.log.info(u'App Minimum ThreatConnect Version: {}'.format(app_min_ver))
            self.log.info(u'App Runtime Level: {}'.format(app_runtime_level))
            self.log.info(u'App Version: {}'.format(app_version))
            if app_commit_hash is not None:
                self.log.info(u'App Commit Hash: {}'.format(app_commit_hash))

    def _log_platform(self):
        """Log the current Platform."""
        self.log.info(u'Platform: {}'.format(platform.platform()))

    def _log_python_version(self):
        """Log the current Python version."""
        self.log.info(
            u'Python Version: {}.{}.{}'.format(
                sys.version_info.major, sys.version_info.minor, sys.version_info.micro
            )
        )

    def _log_tc_proxy(self):
        """Log the proxy settings."""
        if self.default_args.tc_proxy_tc:
            self.log.info(
                u'Proxy Server (TC): {}:{}.'.format(
                    self.default_args.tc_proxy_host, self.default_args.tc_proxy_port
                )
            )

    def _log_tcex_version(self):
        """Log the current TcEx version number."""
        self.log.info(u'TcEx Version: {}'.format(__import__(__name__).__version__))

    def _logger(self):
        """Create TcEx app logger instance.

        The logger is accessible via the ``tc.log.<level>`` call.

        **Logging examples**

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            tcex.log.debug('logging debug')
            tcex.log.info('logging info')
            tcex.log.warning('logging warning')
            tcex.log.error('logging error')

        Args:
            stream_only (bool, default:False): If True only the Stream handler will be enabled.

        Returns:
            logger: An instance of logging
        """
        level = logging.INFO
        self.log.setLevel(level)

        # clear all handlers
        self.log.handlers = []

        # update logging level
        if self.default_args.logging is not None:
            level = self._logger_levels[self.default_args.logging]
        elif self.default_args.tc_log_level is not None:
            level = self._logger_levels[self.default_args.tc_log_level]
        self.log.setLevel(level)

        # add file handler if not already added
        if self.default_args.tc_log_path:
            self._logger_fh()

        # add api handler if not already added
        if self.default_args.tc_token is not None and self.default_args.tc_log_to_api:
            self._logger_api()

        self.log.info('Logging Level: {}'.format(logging.getLevelName(level)))

    def _logger_api(self):
        """Add API logging handler."""
        from .tcex_logger import TcExLogHandler, TcExLogFormatter

        api = TcExLogHandler(self.session)
        api.set_name('api')
        api.setLevel(logging.DEBUG)
        api.setFormatter(TcExLogFormatter())
        self.log.addHandler(api)

    def _logger_fh(self):
        """Add File logging handler."""
        logfile = os.path.join(self.default_args.tc_log_path, self.default_args.tc_log_file)
        fh = logging.FileHandler(logfile)
        fh.set_name('fh')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(self._logger_formatter)
        self.log.addHandler(fh)

    @property
    def _logger_formatter(self):
        """Return log formatter."""
        tx_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s '
        tx_format += '(%(filename)s:%(funcName)s:%(lineno)d)'
        return logging.Formatter(tx_format)

    @property
    def _logger_levels(self):
        """Return log levels."""
        return {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL,
        }

    def _logger_stream(self):
        """Add stream logging handler."""
        sh = logging.StreamHandler()
        sh.set_name('sh')
        sh.setLevel(logging.INFO)
        sh.setFormatter(self._logger_formatter)
        self.log.addHandler(sh)

    def _resources(self, custom_indicators=False):
        """Initialize the resource module.

        This method will make a request to the ThreatConnect API to dynamically
        build classes to support custom Indicators.  All other resources are available
        via this class.

        .. Note:: Resource Classes can be accessed using ``tcex.resources.<Class>`` or using
                  tcex.resource('<resource name>').
        """
        from importlib import import_module

        # create resource object
        self.resources = import_module('tcex.tcex_resources')

        if custom_indicators:
            self.log.info('Loading custom indicator types.')
            # Retrieve all indicator types from the API
            r = self.session.get('/v2/types/indicatorTypes')

            # check for bad status code and response that is not JSON
            if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
                warn = u'Custom Indicators are not supported ({}).'.format(r.text)
                self.log.warning(warn)
                return
            response = r.json()
            if response.get('status') != 'Success':
                warn = u'Bad Status: Custom Indicators are not supported ({}).'.format(r.text)
                self.log.warning(warn)
                return

            try:
                # Dynamically create custom indicator class
                data = response.get('data', {}).get('indicatorType', [])
                for entry in data:
                    name = self.safe_rt(entry.get('name'))
                    # temp fix for API issue where boolean are returned as strings
                    entry['custom'] = self.utils.to_bool(entry.get('custom'))
                    entry['parsable'] = self.utils.to_bool(entry.get('parsable'))
                    self._indicator_types.append(u'{}'.format(entry.get('name')))
                    self._indicator_types_data[entry.get('name')] = entry
                    if not entry['custom']:
                        continue

                    # Custom Indicator have 3 values. Only add the value if it is set.
                    value_fields = []
                    if entry.get('value1Label'):
                        value_fields.append(entry.get('value1Label'))
                    if entry.get('value2Label'):
                        value_fields.append(entry.get('value2Label'))
                    if entry.get('value3Label'):
                        value_fields.append(entry.get('value3Label'))

                    # get instance of Indicator Class
                    i = self.resources.Indicator(self)
                    custom = {
                        '_api_branch': entry['apiBranch'],
                        '_api_entity': entry['apiEntity'],
                        '_api_uri': '{}/{}'.format(i.api_branch, entry['apiBranch']),
                        '_case_preference': entry['casePreference'],
                        '_custom': entry['custom'],
                        '_name': name,
                        '_parsable': entry['parsable'],
                        '_request_entity': entry['apiEntity'],
                        '_request_uri': '{}/{}'.format(i.api_branch, entry['apiBranch']),
                        '_status_codes': {
                            'DELETE': [200],
                            'GET': [200],
                            'POST': [200, 201],
                            'PUT': [200],
                        },
                        '_value_fields': value_fields,
                    }
                    # Call custom indicator class factory
                    setattr(
                        self.resources,
                        name,
                        self.resources.class_factory(name, self.resources.Indicator, custom),
                    )
            except Exception as e:
                self.handle_error(220, [e])

    def _signal_handler(self, signal_interupt, frame):  # pylint: disable=W0613
        """Handle singal interrupt."""
        call_file = os.path.basename(inspect.stack()[1][0].f_code.co_filename)
        call_module = inspect.stack()[1][0].f_globals['__name__'].lstrip('Functions.')
        call_line = inspect.stack()[1][0].f_lineno
        self.log.error(
            'App interrupted - file: {}, method: {}, line: {}.'.format(
                call_file, call_module, call_line
            )
        )
        if signal_interupt in (2, 15):
            self.exit(1, 'The App received an interrupt signal and will now exit.')

    @property
    def utils(self):
        """Include the Utils module.

        .. Note:: Utils methods can be accessed using ``tcex.utils.<method>``.
        """
        if self._utils is None:
            from .tcex_utils import TcExUtils

            self._utils = TcExUtils(self)
        return self._utils

    @property
    def args(self):
        """Argparser args Namespace."""
        return self.tcex_args.args()

    @property
    def rargs(self):
        """Argparser args Namespace with Playbook args automatically resolved (resolved args)."""
        return self.tcex_args.resolved_args()

    def batch(
        self,
        owner,
        action=None,
        attribute_write_type=None,
        halt_on_error=False,
        playbook_triggers_enabled=None,
    ):
        """Return instance of Batch"""
        from .tcex_ti_batch import TcExBatch

        return TcExBatch(
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
        from .tcex_cache import TcExCache

        return TcExCache(self, domain, data_type, ttl_minutes, mapping)

    # TODO: remove this method and use JMESPath instead.
    def data_filter(self, data):
        """Return an instance of the Data Filter Class.

        A simple helper module to filter results from ThreatConnect API or other data
        source.  For example if results need to be filtered by an unsupported field the module
        allows you to pass the data array/list in and specify one or more filters to get just the
        results required.

        Args:
            data (list): The list of dictionary structure to filter.

        Returns:
            (object): An instance of DataFilter Class
        """
        try:
            from .tcex_data_filter import DataFilter

            return DataFilter(self, data)
        except ImportError as e:
            warn = u'Required Module is not installed ({}).'.format(e)
            self.log.warning(warn)

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
        from .tcex_datastore import TcExDataStore

        return TcExDataStore(self, domain, data_type, mapping)

    @property
    def default_args(self):
        """All args parsed before App args are added."""
        return self.tcex_args.default_args

    @property
    def error_codes(self):
        """ThreatConnect error codes."""
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
            self.log.error(u'Invalid exit code')
            code = 1

        if self.default_args.tc_aot_enabled:
            # push exit message
            self.playbook.aot_rpush(code)

        self.log.info(u'Exit Code: {}'.format(code))
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
            self.log.warning(u'Invalid exit code')

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

    def handle_error(self, code, message_values=None, raise_error=True):
        """Raise RuntimeError

        Args:
            code (integer): The error code from API or SDK.
            message (string): The error message from API or SDK.
        """
        try:
            if message_values is None:
                message_values = []
            message = self.error_codes.message(code).format(*message_values)
            self.log.error('Error code: {}, {}'.format(code, message))
        except AttributeError:
            self.log.error('Incorrect error code provided ({}).'.format(code))
            raise RuntimeError(1000, 'Generic Failure, see logs for more details.')
        except IndexError:
            self.log.error(
                'Incorrect message values provided for error code {} ({}).'.format(
                    code, message_values
                )
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
            self._resources(True)  # load custom indicator associations
        return self._indicator_types

    @property
    def indicator_types_data(self):
        """Return ThreatConnect indicator types data.

        Retrieve the data from the API if it hasn't already been retrieved.

        Returns:
            (dict): A dictionary of ThreatConnect Indicator data.
        """
        if not self._indicator_types_data:
            # load custom indicator associations
            self._resources(True)
        return self._indicator_types_data

    @property
    def group_types_data(self):
        """All supported ThreatConnect Group types."""
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
        """
        Returns the object type as a string given a api entity.

        Args:
            api_entity:

        Returns:

        """
        merged = self.group_types_data.copy()
        merged.update(self.indicator_types_data)
        print(merged)
        for (key, value) in merged.items():
            if value.get('apiEntity') == api_entity:
                return key
        return None

    @property
    def install_json(self):
        """Return contents of install.json configuration file, loading from disk if required."""
        if self._install_json is None:
            try:
                install_json_filename = os.path.join(os.getcwd(), 'install.json')
                with open(install_json_filename, 'r') as fh:
                    self._install_json = json.load(fh)
            except IOError:
                self.log.warning(u'Could not retrieve App Data.')
                self._install_json = {}
        return self._install_json

    @property
    def install_json_params(self):
        """Parse params from install.json into a dict by name."""
        if not self._install_json_params:
            for param in self.install_json.get('params') or []:
                self._install_json_params[param.get('name')] = param
        return self._install_json_params

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
        from .tcex_metrics_v2 import TcExMetricsV2

        return TcExMetricsV2(self, name, description, data_type, interval, keyed)

    def notification(self):
        """Get instance of the Notification module.

        Returns:
            (object): An instance of the Notification Class.
        """
        from .tcex_notification_v2 import TcExNotificationV2

        return TcExNotificationV2(self)

    def message_tc(self, message, max_length=255):
        """Write data to message_tc file in TcEX specified directory.

        This method is used to set and exit message in the ThreatConnect Platform.
        ThreatConnect only supports files of max_message_length.  Any data exceeding
        this limit will be truncated by this method.

        Args:
            message (string): The message to add to message_tc file
        """
        if os.access(self.default_args.tc_out_path, os.W_OK):
            message_file = '{}/message.tc'.format(self.default_args.tc_out_path)
        else:
            message_file = 'message.tc'

        message = '{}\n'.format(message)
        if max_length - len(message) > 0:
            with open(message_file, 'a') as mh:
                mh.write(message)
        elif max_length > 0:
            with open(message_file, 'a') as mh:
                mh.write(message[:max_length])
        max_length -= len(message)

    @property
    def parser(self):
        """Instance tcex args parser."""
        return self.tcex_args.parser

    @property
    def playbook(self):
        """Include the Playbook Module.

        .. Note:: Playbook methods can be accessed using ``tcex.playbook.<method>``.
        """
        if self._playbook is None:
            from .tcex_playbook import TcExPlaybook

            self._playbook = TcExPlaybook(self)
        return self._playbook

    @property
    def proxies(self):
        """Formats proxy configuration into required format for Python Requests module.

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
                proxy_url = '{}:{}@{}:{}'.format(
                    tc_proxy_username,
                    tc_proxy_password,
                    self.default_args.tc_proxy_host,
                    self.default_args.tc_proxy_port,
                )
            else:
                # proxy url without auth
                proxy_url = '{}:{}'.format(
                    self.default_args.tc_proxy_host, self.default_args.tc_proxy_port
                )
            proxies = {
                'http': 'http://{}'.format(proxy_url),
                'https': 'https://{}'.format(proxy_url),
            }
        return proxies

    def request(self, session=None):
        """Return an instance of the Request Class.

        A wrapper on the Python Requests module that provides a different interface for creating
        requests. The session property of this instance has built-in logging, session level
        retries, and preconfigured proxy configuration.

        Returns:
            (object): An instance of Request Class
        """
        try:
            from .tcex_request import TcExRequest

            r = TcExRequest(self, session)
            if session is None and self.default_args.tc_proxy_external:
                self.log.info(
                    'Using proxy server for external request {}:{}.'.format(
                        self.default_args.tc_proxy_host, self.default_args.tc_proxy_port
                    )
                )
                r.proxies = self.proxies
            return r
        except ImportError as e:
            self.handle_error(105, [e])

    def resource(self, resource_type):
        """Get instance of Resource Class with dynamic type.

        Args:
            resource_type: The resource type name (e.g Adversary, User Agent, etc).

        Returns:
            (object): Instance of Resource Object child class.
        """
        try:
            resource = getattr(self.resources, self.safe_rt(resource_type))(self)
        except AttributeError:
            self._resources(True)
            resource = getattr(self.resources, self.safe_rt(resource_type))(self)
        return resource

    def results_tc(self, key, value):
        """Write data to results_tc file in TcEX specified directory.

        The TcEx platform support persistent values between executions of the App.  This
        method will store the values for TC to read and put into the Database.

        Args:
            key (string): The data key to be stored.
            value (string): The data value to be stored.
        """
        if os.access(self.default_args.tc_out_path, os.W_OK):
            results_file = '{}/results.tc'.format(self.default_args.tc_out_path)
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
                    results += '{} = {}\n'.format(k, v)
            if new and value is not None:  # indicates the key/value pair didn't already exist
                results += '{} = {}\n'.format(key, value)
            fh.seek(0)
            fh.write(results)
            fh.truncate()

    def s(self, data, errors='strict'):
        """Decode value using correct Python 2/3 method.

        This method is intended to replace the :py:meth:`~tcex.tcex.TcEx.to_string` method with
        better logic to handle poorly encoded unicode data in Python2 and still work in Python3.

        Args:
            data (any): Data to ve validated and (de)encoded
            errors (string): What method to use when dealing with errors.

        Returns:
            (string): Return decoded data
        """
        try:
            if data is None or isinstance(data, (int, list, dict)):
                pass  # Do nothing with these types
            elif isinstance(data, unicode):
                try:
                    data.decode('utf-8')
                except UnicodeEncodeError:  # 2to3 converts unicode to str
                    # 2to3 converts unicode to str
                    data = str(data.encode('utf-8').strip(), errors=errors)
                    self.log.warning(u'Encoding poorly encoded string ({})'.format(data))
                except AttributeError:
                    pass  # Python 3 can't decode a str
            else:
                data = str(data, 'utf-8', errors=errors)  # 2to3 converts unicode to str
        except NameError:
            pass  # Can't decode str in Python 3
        return data

    def safe_indicator(self, indicator, errors='strict'):
        """Indicator encode value for safe HTTP request.

        Args:
            indicator (string): Indicator to URL Encode
            errors (string): The error handler type.

        Returns:
            (string): The urlencoded string
        """
        if indicator is not None:
            try:
                indicator = quote(self.s(str(indicator), errors=errors), safe='~')
            except KeyError:
                indicator = quote(bytes(indicator), safe='~')
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
                word = u'{}'.format(word)
                if (len(group_name) + len(word) + len(ellipsis_value)) >= group_max_length:
                    group_name = '{}{}'.format(group_name, ellipsis_value)
                    group_name = group_name.lstrip(' ')
                    break
                group_name += ' {}'.format(word)
        return group_name

    def safetag(self, tag, errors='strict'):
        """Wrapper method for safe_tag."""
        return self.safe_tag(tag, errors)

    def safe_tag(self, tag, errors='strict'):
        """URL Encode and truncate tag to match limit (128 characters) of ThreatConnect API.

        Args:
           tag (string): The tag to be truncated

        Returns:
            (string): The truncated tag
        """
        if tag is not None:
            try:
                # handle unicode characters and url encode tag value
                tag = quote(self.s(tag, errors=errors), safe='~')[:128]
            except KeyError as e:
                warn = 'Failed converting tag to safetag ({})'.format(e)
                self.log.warning(warn)
        return tag

    def safeurl(self, url, errors='strict'):
        """Wrapper method for safe_url."""
        return self.safe_url(url, errors)

    def safe_url(self, url, errors='strict'):
        """URL encode value for safe HTTP request.

        Args:
            url (string): The string to URL Encode.

        Returns:
            (string): The urlencoded string.
        """
        if url is not None:
            url = quote(self.s(url, errors=errors), safe='~')
        return url

    @property
    def session(self):
        """Return an instance of Requests Session configured for the ThreatConnect API."""
        if self._session is None:
            from .tcex_session import TcExSession

            self._session = TcExSession(self)
        return self._session

    @property
    def ti(self):
        """Include the Threat Intel Module.

        .. Note:: Threat Intell methods can be accessed using ``tcex.ti.<method>``.
        """
        if self._ti is None:
            from .tcex_ti import TcExTi

            self._ti = TcExTi(self)
        return self._ti
