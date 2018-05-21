# -*- coding: utf-8 -*-
""" TcEx Framework """
from builtins import str
import base64  # authorization
import hashlib  # authorization
import hmac  # authorization
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from importlib import import_module
from platform import platform
try:
    from urllib import quote  # Python 2
except ImportError:
    from urllib.parse import quote  # Python 3

from dateutil.relativedelta import relativedelta
import inflect

from .tcex_argparser import TcExArgParser
from .tcex_error_codes import TcExErrorCodes
from .tcex_job import TcExJob
from .tcex_metrics_v2 import TcExMetricsV2
from .tcex_notification_v2 import TcExNotificationV2
from .tcex_session import TcExSession



class TcEx(object):
    """Provides basic functionality for all types of TxEx Apps."""

    def __init__(self):
        """Initialize Class Properties."""
        self.error_codes = TcExErrorCodes()
        # init inflect engine
        self.inflect = inflect.engine()

        self._exit_code = 0
        self._indicator_associations_types_data = {}
        self._indicator_types = []
        self._indicator_types_data = {}
        self._max_message_length = 255
        # NOTE: odd issue where args is not updating properly
        self._tc_token = None
        self._tc_token_expires = None

        # Parser
        self._parsed = False
        self.parser = TcExArgParser()
        self.default_args, unknown = self.parser.parse_known_args()

        # NOTE: odd issue where args is not updating properly
        if self.default_args.tc_token is not None:
            self._tc_token = self.default_args.tc_token
        if self.default_args.tc_token_expires is not None:
            self._tc_token_expires = self.default_args.tc_token_expires

        # logger (must parse args first)
        self.log = self._logger(self.default_args.tc_log_file)

        # inject args using secure param feature
        self._inject_secure_params()

        # Add ThreatConnect Session
        self.session = TcExSession(self)

        # Log system and App data
        self._log()

        # [Deprecated] include jobs module
        self._jobs()

        # include playbook module
        self._playbook()

        # include resources module
        self._resources()

        # include utils module
        self._utils()

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

    def _authorization_token_renew(self):
        """Method for handling token authorization to ThreatConnect API.

        This method will automatically renew the ThreatConnect token if it has expired.

        Returns:
            (dictionary): An dictionary containing the header values for authorization to
                          ThreatConnect.
        """
        authorization = 'TC-Token {}'.format(self._tc_token)

        window_padding = 15  # bcs - possible configuration option
        current_time = int(time.time()) + window_padding
        if self._tc_token_expires < current_time:
            # Renew Token
            request = self.request()
            request.add_payload('expiredToken', self._tc_token)
            request.url = '{}/appAuth'.format(self.default_args.tc_api_path)
            r = request.send()
            if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
                self.handle_error(210, [r.text])
            data = r.json()
            if data['success']:
                self.log.info(u'Expired API token has been renewed.')
                self._tc_token = data['apiToken']  # remove str() due to newstr issue
                self._tc_token_expires = int(data['apiTokenExpires'])
                authorization = 'TC-Token {}'.format(data['apiToken'])
            else:
                self.handle_error(210, [r.text])
        return {'Authorization': authorization}

    def _inject_secure_params(self):
        """Inject secure params retrieved from the API."""
        if not self.default_args.tc_secure_params:
            self.log.info('Secure Params are not enabled')
            return

        # Retrieve secure params and inject them into sys.argv
        r = self.session.get('/internal/job/execution/parameters')

        # check for bad status code and response that is not JSON
        if not r.ok or r.headers.get('content-type') != 'application/json':
            warn = u'Secure params could not be retrieved.'
            self.log.warning(warn)
            return

        # inject args from API endpoint
        data = r.json()
        for arg, value in data.get('inputs', {}).items():
            if isinstance(value, (bool)):
                # handle bool values as flags (e.g., --flag) with no value
                if value:
                    sys.argv.append('--{}'.format(arg))
            else:
                sys.argv.append('--{}'.format(arg))
                sys.argv.append('{}'.format(value))

        # reset default_args now that values have been injected into sys.argv
        self.default_args, unknown = self.parser.parse_known_args()
        self._unknown_args(unknown)

        # reset logging level
        self.log = self._logger(self.default_args.tc_log_file)

    def _jobs(self):
        """**[Deprecated]** Include the jobs Module.

        .. warning:: The job module is deprecated and will be removed in TcEx version 0.9.0. Use
                     tcex.batch instead.
        """
        self.jobs = TcExJob(self)

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
        try:
            install_json = os.path.join(os.getcwd(), 'install.json')
            with open(install_json, 'r') as fh:
                app_data = json.load(fh)
            app_features = ','.join(app_data.get('features', []))
            app_min_ver = app_data.get('minServerVersion', 'N/A')
            app_name = app_data.get('displayName')
            app_runtime_level = app_data.get('runtimeLevel')
            app_version = app_data.get('programVersion')

            self.log.info(u'App Name: {}'.format(app_name))
            if app_features:
                self.log.info(u'App Features: {}'.format(app_features))
            self.log.info(u'App Minimum ThreatConnect Version: {}'.format(app_min_ver))
            self.log.info(u'App Runtime Level: {}'.format(app_runtime_level))
            self.log.info(u'App Version: {}'.format(app_version))
        except IOError:
            self.log.debug(u'Could not retrieve App Data.')

    def _log_platform(self):
        """Log the current Platform."""
        self.log.info(u'Platform: {}'.format(platform()))

    def _log_python_version(self):
        """Log the current Python version."""
        self.log.info(u'Python Version: {}.{}.{}'.format(
            sys.version_info.major, sys.version_info.minor, sys.version_info.micro))

    def _log_tc_proxy(self):
        """Log the proxy settings."""
        if self.default_args.tc_proxy_tc:
            self.log.info(u'Proxy Server (TC): {}:{}.'.format(
                self.default_args.tc_proxy_host, self.default_args.tc_proxy_port))

    def _log_tcex_version(self):
        """Log the current TcEx version number."""
        self.log.info(u'TcEx Version: {}'.format(__import__(__name__).__version__))

    def _logger(self, file_name=None):
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
            file_name (Optional[string]): The name for the log file

        Returns:
            logger: An instance of logging
        """
        if file_name is None:
            file_name = 'app.log'

        level = logging.INFO
        log_level = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }
        name = 'tcex'

        # BCS - temporarily until there is some way to configure App logging level in the UI
        if self.default_args.logging is not None:
            level = log_level[self.default_args.logging]
        elif self.default_args.tc_log_level is not None:
            level = log_level[self.default_args.tc_log_level]

        logfile = os.path.join(self.default_args.tc_log_path, file_name)
        log = logging.getLogger(name)
        log.setLevel(level)

        tx_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s '
        tx_format += '(%(funcName)s:%(lineno)d)'
        formatter = logging.Formatter(tx_format)

        if self.default_args.tc_token is not None and self.default_args.tc_log_to_api:
            # api & file logger
            from .tcex_logger import TcExLogger
            api = TcExLogger(logfile, self)
            api.set_name('api')
            api.setLevel(level)
            api.setFormatter(formatter)
            log.addHandler(api)
        else:
            # file logger
            fh = logging.FileHandler(logfile)
            fh.set_name('fh')
            fh.setLevel(level)
            fh.setFormatter(formatter)
            log.addHandler(fh)

        log.info('Logging Level: {}'.format(logging.getLevelName(level)))
        return log

    def _playbook(self):
        """Include the Playbook Module.

        .. Note:: Playbook methods can be accessed using ``tcex.playbook.<method>``.
        """
        try:
            from .tcex_playbook import TcExPlaybook
            self.playbook = TcExPlaybook(self)
        except ImportError as e:
            warn = u'Required playbook Python dependency is not installed ({}).'.format(e)
            self.log.warning(warn)

    def _resources(self, custom_indicators=False):
        """Initialize the resource module.

        This method will make a request to the ThreatConnect API to dynamically
        build classes to support custom Indicators.  All other resources are available
        via this class.

        .. Note:: Resource Classes can be accessed using ``tcex.resources.<Class>`` or using
                  tcex.resource('<resource name>').
        """
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
                            'PUT': [200]
                        },
                        '_value_fields': value_fields
                    }
                    # Call custom indicator class factory
                    setattr(self.resources, name, self.resources.class_factory(
                        name, self.resources.Indicator, custom))
            except Exception as e:
                self.handle_error(220, [e])

    def _unknown_args(self, args):
        """Log argparser unknown arguments.

        Args:
            args (list): List of unknown arguments
        """
        for u in args:
            self.log.debug(u'Unsupported arg found ({}).'.format(u))

    def _utils(self):
        """Include the Utils module.

        .. Note:: Utils methods can be accessed using ``tcex.utils.<method>``.
        """
        try:
            from .tcex_utils import TcExUtils
            self.utils = TcExUtils(self)
        except ImportError as e:
            warn = u'Required utils Python dependency is not installed ({}).'.format(e)
            self.log.warning(warn)

    @property
    def args(self):
        """The parsed args from argparser

        .. Note:: Accessing args should only be done directly in the App.

        Returns:
            (namespace): ArgParser parsed arguments
        """

        if not self._parsed:
            self.default_args, unknown = self.parser.parse_known_args()
            self.results_tc_args()  # for local testing only
            self._parsed = True

            # log unknown arguments only once
            self._unknown_args(unknown)

        return self.default_args

    def authorization(self, request_prepped):
        """A method to handle the different methods of authenticating to the ThreatConnect API.

        **Token Based Authorization**::

            {'Authorization': authorization}

        **HMAC Based Authorization**::

            {
                'Authorization': authorization,
                'Timestamp': <unix timestamp>
            }

           http://docs.python-requests.org/en/master/api/#requests.Session.prepare_request.

        Args:
            request_prepped (object): A instance of Python Request module requests.
                                        PreparedRequest.
        Returns:
            (dictionary): An dictionary containing the header values for authorization to
                          ThreatConnect.
        """
        authorization = None

        if self._tc_token is not None:
            authorization = {'Authorization': 'TC-Token {}'.format(self._tc_token)}
            if self._tc_token_expires is not None:
                authorization = self._authorization_token_renew()
        elif (self.default_args.api_access_id is not None and
              self.default_args.api_secret_key is not None):
            authorization = self.authorization_hmac(request_prepped)

        return authorization

    def authorization_hmac(self, request_prepped):
        """Method for handling HMAC authorization to ThreatConnect API.

           http://docs.python-requests.org/en/master/api/#requests.Session.prepare_request.

        Args:
            request_prepped (object): A instance of Python Request prepped requests.
                                        PreparedRequest.
        Returns:
            (dictionary): An dictionary containing the header values for authorization to
                          ThreatConnect.
        """
        if request_prepped is None:
            self.handle_error(215, [])

        timestamp = int(time.time())
        signature = '{}:{}:{}'.format(
            request_prepped.path_url, request_prepped.method, timestamp)
        hmac_signature = hmac.new(
            self.default_args.api_secret_key.strip('\'').encode(), signature.encode(),
            digestmod=hashlib.sha256).digest()
        authorization = 'TC {}:{}'.format(
            self.default_args.api_access_id, base64.b64encode(hmac_signature).decode())
        return {
            'Authorization': authorization,
            'Timestamp': str(timestamp)
        }

    def batch(self, owner, action=None, attribute_write_type=None, halt_on_error=False):
        """Return instance of Batch"""
        from .tcex_batch_v2 import TcExBatch
        return TcExBatch(self, owner, action, attribute_write_type, halt_on_error)

    def bulk_enabled(self, owner=None, api_path=None, authorization=None):
        """[Deprecated] Check if bulk indicators is enabled for owner.

        .. warning:: This method is deprecated and will be removed in TcEx version 0.9.0.

        Using the TC API validate that bulk indicator download is enabled and
        has successfully run for the provided owner.

        Args:
            owner (Optional [string]): Owner name to check.
            api_path (Optional [string]): The url to the ThreatConnect API.
            authorization (Optional [string]): The authorization header value.

        Returns:
            (boolean): True if bulk indicator download is enabled and has run
        """
        self.log.warning('This App is using a deprecated method (bulk_enabled).')
        if api_path is None:
            api_path = self.default_args.tc_api_path

        # Dynamically create custom indicator class
        request = self.request()
        if authorization is not None:
            request.authorization = authorization
        if owner is not None:
            request.owner = owner
        request.url = '{}/v2/indicators/bulk'.format(api_path)

        r = request.send()
        if r.ok and 'application/json' in r.headers.get('content-type', ''):
            data = r.json()
            if data.get('status') == 'Success':
                if (data.get('data', {}).get('bulkStatus', {}).get('jsonEnabled') and
                        data.get('data').get('bulkStatus', {}).get('lastRun') is not None):
                    return True
        return False

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
            if code == 0 or (code is None and self.exit_code == 0):
                self.log.info(msg)
            else:
                self.log.error(msg)
            self.message_tc(msg)

        # flush logs to api
        if self.default_args.tc_token is not None and self.default_args.tc_log_to_api:
            if self.log is not None and self.log.handlers:
                for handler in self.log.handlers:
                    if handler.get_name() == 'api':
                        handler.log_to_api()

        if code is None:
            self.log.info(u'exit_code: {}'.format(self.exit_code))
            sys.exit(self.exit_code)
        elif code in [0, 1, 3]:
            self.log.info(u'exit_code: {}'.format(code))
            sys.exit(code)
        else:
            self.log.error(u'Invalid exit code')
            sys.exit(1)  # exit with error

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
            'Task'
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
            self.log.error('Incorrect message values provided for error code {} ({}).'.format(
                code, message_values))
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

    def job(self):
        """**[Deprecated]** Return instance of Job module

        .. warning:: The job module is deprecated and will be removed in TcEx version 0.9.0. Use
                     tcex.batch instead.
        """
        self.log.warning('Jobs module will be deprecated in TcEx version 0.9.0.')
        return TcExJob(self)

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
        return TcExMetricsV2(self, name, description, data_type, interval, keyed)

    def notification(self):
        """Get instance of the Notification module.

        Returns:
            (object): An instance of the Notification Class.
        """
        return TcExNotificationV2(self)

    def message_tc(self, message):
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
        if self._max_message_length - len(message) > 0:
            with open(message_file, 'a') as mh:
                mh.write(message)
        elif self._max_message_length > 0:
            with open(message_file, 'a') as mh:
                mh.write(message[:self._max_message_length])
        self._max_message_length -= len(message)

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
        if (self.default_args.tc_proxy_host is not None and
                self.default_args.tc_proxy_port is not None):

            if (self.default_args.tc_proxy_username is not None and
                    self.default_args.tc_proxy_password is not None):
                tc_proxy_username = quote(self.default_args.tc_proxy_username, safe='~')
                tc_proxy_password = quote(self.default_args.tc_proxy_password, safe='~')

                proxies = {
                    'http': 'http://{}:{}@{}:{}'.format(
                        tc_proxy_username, tc_proxy_password,
                        self.default_args.tc_proxy_host, self.default_args.tc_proxy_port),
                    'https': 'https://{}:{}@{}:{}'.format(
                        tc_proxy_username, tc_proxy_password,
                        self.default_args.tc_proxy_host, self.default_args.tc_proxy_port)
                }
            else:
                proxies = {
                    'http': 'http://{}:{}'.format(
                        self.default_args.tc_proxy_host, self.default_args.tc_proxy_port),
                    'https': 'https://{}:{}'.format(
                        self.default_args.tc_proxy_host, self.default_args.tc_proxy_port)
                }
        return proxies

    def request(self, session=None):
        """Return an instance of the Request Class.

        A wrapper on the Python Request Module specifically for interacting with the
        ThreatConnect API.  However, this can also be used for connecting to other
        API endpoints.

        Returns:
            (object): An instance of Request Class
        """
        try:
            from .tcex_request import TcExRequest
            return TcExRequest(self, session)
        except ImportError as e:
            self.handle_error(105, [e])

    def request_external(self):
        """Return an instance of the Request Class with Proxy Set

        See :py:mod:`~tcex.tcex.TcEx.request`

        Returns:
            (object): An instance of Request Class
        """
        r = self.request()
        if self.default_args.tc_proxy_external:
            self.log.info(u'Using proxy server for external request {}:{}.'.format(
                self.default_args.tc_proxy_host, self.default_args.tc_proxy_port))
            r.proxies = self.proxies
        return r

    def request_tc(self):
        """**[Deprecated]** Return an instance of the Request Class with Proxy and Authorization Set

        .. warning:: This method is deprecated and will be removed in TcEx version 0.9.0. Use
                     tcex.session instead.

        See :py:mod:`~tcex.tcex.TcEx.request`

        Returns:
            (object): An instance of Request Class
        """
        self.log.warning('This App is using a deprecated method (request_tc).')
        r = self.request(self.session)
        return r

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
            result_file = '{}/results.tc'.format(self.default_args.tc_out_path)
        else:
            result_file = 'results.tc'
        results = '{} = {}\n'.format(key, value)
        with open(result_file, 'a') as rh:
            rh.write(results)

    def results_tc_args(self):
        """Read data from results_tc file from previous run of app.

        This method is only required when not running from the with the
        TcEX platform and is only intended for testing apps locally.

        Returns:
            (dictionary): A dictionary of values written to results_tc.
        """
        results = []
        if os.access(self.default_args.tc_out_path, os.W_OK):
            result_file = '{}/results.tc'.format(self.default_args.tc_out_path)
        else:
            result_file = 'results.tc'
        if os.path.isfile(result_file):
            with open(result_file, 'r') as rh:
                results = rh.read().strip().split('\n')
            os.remove(result_file)
        for line in results:
            key, value = line.split(' = ')
            setattr(self.default_args, key, value)

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

    def epoch_seconds(self, delta=None):
        """**[Deprecated]** Get epoch seconds for now or using a time delta.

        .. warning:: This method is deprecated and will be removed in TcEx version 0.9.0.  Use the
                     tcex.utils date methods instead.

        .. code-block:: javascript
            :linenos:
            :lineno-start: 1

            {'days': 1}
            {'weeks': 3}
            {'months': 4}
            {'days': 1, 'weeks': 3, 'months': 4}


        .. Note:: More information can be found at
                  https://dateutil.readthedocs.io/en/stable/relativedelta.html

        Args:
            delta (Optional [integer]): The exit code value for the app.
        Returns:
            (int): A integer representing epoch seconds.
        """
        self.log.warning('This App is using a deprecated method (epoch seconds).')
        epoch = datetime.now()
        if delta is not None:
            epoch = epoch - relativedelta(**delta)

        return int(time.mktime(epoch.timetuple()))

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
        """URL encode value for safe HTTP request.

        Args:
            url (string): The string to URL Encode.

        Returns:
            (string): The urlencoded string.
        """
        if url is not None:
            url = quote(self.s(url, errors=errors), safe='~')
        return url

    def to_string(self, data, errors='strict'):
        """**[Deprecated]** Decode value using correct Python 2/3 method

        .. warning:: This method is deprecated and will be removed in TcEx version 0.9.0.

        Args:
            data (any): Data to ve validated and re-encoded
            errors (string): What method to use when dealing with errors.

        Returns:
            (string): Return decoded data

        """
        self.log.warning('This App is using a deprecated method (to_string).')
        if data is not None and not isinstance(data, str):
            data = str(data, 'utf-8', errors=errors)
        return data
