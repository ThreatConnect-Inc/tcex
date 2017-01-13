""" standard """
import argparse
import base64  # authorization
import hashlib  # authorization
import hmac  # authorization
import inspect
import json
import logging
import os
import re
import sys
import urllib
import time
import types
from urlparse import urlparse

""" third party """
from argparser import ArgParser
""" custom """

class TcEx(object):
    """Provides basic functionality for all types of TxEx Apps"""

    def __init__(self):
        """Initialize class data.

        Setup default values and logging method.
        """

        self._exit_code = 0
        # bcs - replace group_type with dynamic values from API
        self.group_types = ['Adversary', 'Document', 'Email', 'Incident', 'Signature', 'Threat']
        self.indicator_types = []
        self._max_message_length = 255
        # bcs - odd issue where args is not updating properly
        self._tc_token = None
        self._tc_token_expires = None

        # Parser
        self._parsed = False
        self._parser = ArgParser()
        self._args, unknown = self._parser.parse_known_args()

        # bcs - odd issue where args is not updating properly
        if self._args.tc_token is not None:
            self._tc_token = self._args.tc_token
        if self._args.tc_token_expires is not None:
            self._tc_token_expires = self._args.tc_token_expires

        # logger (must parse args first)
        self.log = self._logger()

        # Log versions
        self._log_app_version()
        self._log_python_version()
        self._log_tcex_version()

        # include jobs module
        self._jobs()

        # include playbook module
        self._playbook()

        # include resources module
        self._resources()

    def _authorization_token_renew(self):
        """Method for handling token authorization to ThreatConnect API.

        This method will automatically renew the ThreatConnect token if it has expired.

        Returns:
            (dictionary): An dictionary containing the header values for authorization to ThreatConnect.
        """
        authorization = 'TC-Token {}'.format(self._tc_token)

        window_padding = 15  # bcs - possible configuration option
        current_time = int(time.time()) - window_padding
        if (self._tc_token_expires < current_time):
            # Renew Token
            r = self.request
            r.add_payload('expiredToken', self._tc_token)
            r.url = '{}/appAuth'.format(self._args.tc_api_path.strip('api'))
            r.add_payload('expiredToken', self._tc_token)
            results = r.send()
            try:
                data = results.json()
                if data['success']:
                    self.log.info('Expired API token has been renewed.')
                    self._tc_token = str(data['apiToken'])
                    self._tc_token_expires = int(data['apiTokenExpires'])
                    authorization = 'TC-Token {}'.format(data['apiToken'])
                else:
                    err = 'Failed to renew Token. ({})'.format(results.text)
                    raise RuntimeError(err)
            except RuntimeError:
                raise
            except:
                self.log.error('Failure during token renewal. ({})'.format(results.text))

        return {'Authorization': authorization}

    def _jobs(self):
        """Include jobs Module"""
        from tcex_job import TcExJob
        self.jobs = TcExJob(self)

    def _log_app_version(self):
        """Log the current App Version"""

        # Best Effort
        try:
            install_json = os.path.join(os.getcwd(), 'install.json')
            with open(install_json, 'r') as fh:
                app_version = json.load(fh)['programVersion']

            self.log.info('App Version: {}'.format(app_version))
        except:
            self.log.debug('Could not retrieve App Version')

    def _log_python_version(self):
        """Log the current Python Version"""
        self.log.info('Python Version: {}.{}.{}'.format(
            sys.version_info.major, sys.version_info.minor, sys.version_info.micro))

    def _log_tcex_version(self):
        """Log the current TcEx Version"""

        # Get the *actual* path to the module
        module_path = os.path.realpath(
            os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))

        # Open the __init__.py file and extract the version using regex
        with open(os.path.join(module_path, '__init__.py'), 'r') as fd:
            tcex_version = re.search(
                r'^__version__(?:\s+)?=(?:\s+)?[\'|\"]((?:[0-9]{1,3}(?:\.)?){1,3})[\'|\"]', fd.read(), re.MULTILINE).group(1)

        self.log.info('TcEx Version: {}'.format(tcex_version))

    def _logger(self, file_name='app.log'):
        """Create TcEx app logger instance.

        The logger is accessible via the ``tc.log.<level>`` call.

        **Logging examples**

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            tcex.log.debug('logging debug')
            tcex.log.info('logging info')
            tcex.log.error('logging error')
            tcex.log.critical('logging critical')

        Args:
            file_name (Optional[string]): The name for the log file

        Returns:
            logger: An instance of logging
        """

        level = logging.INFO
        log_level = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }
        name = 'tcapp'
        # if self._args.tc_log_level.lower() in log_level.keys():
        #     level = log_level[self._args.tc_log_level]

        # BCS - temporarily until there is some way to configure App logging level in the UI
        if self._args.logging is not None:
            level = log_level[self._args.logging]
        elif self._args.tc_log_level is not None:
            level = log_level[self._args.tc_log_level]

        logfile = os.path.join(self._args.tc_log_path, file_name)
        log = logging.getLogger(name)
        log.setLevel(level)

        tx_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s '
        tx_format += '(%(funcName)s:%(lineno)d)'
        formatter = logging.Formatter(tx_format)

        if self._args.tc_token is not None and self._args.tc_log_to_api:
            # api & file logger
            from api_logging_handler import ApiLoggingHandler
            api = ApiLoggingHandler(logfile, self)
            api.set_name('api')  # not supported in python 2.6
            api.setLevel(level)
            api.setFormatter(formatter)
            log.addHandler(api)
        else:
            # file logger
            fh = logging.FileHandler(logfile)
            fh.set_name('fh')  # not supported in python 2.6
            fh.setLevel(level)
            fh.setFormatter(formatter)
            log.addHandler(fh)

        log.info('Logging Level: {}'.format(logging.getLevelName(level)))
        return log

    def _playbook(self):
        """Include Playbook Module

        .. Note:: Playbook methods can be accessed using ``tcex.playbook.<method>``.
        """
        try:
            from tcex_playbook import TcExPlaybook
            self.playbook = TcExPlaybook(self)
        except ImportError as e:
            warn = 'Required playbook python dependency is not installed ({}).'.format(e)
            self.log.warn(warn)

    def _resources(self):
        """Initialize the resource module.

        This method will make a request to the ThreatConnect API to dynamically
        build classes to support custom Indicators.  All other resources are available
        via this class.

        .. Note:: Resource Classes can be accessed using ``tcex.resources.<Class>``.
        """
        self.resources = type('resources', (object,), {})

        import tcex_resources as Resources
        for name, obj in inspect.getmembers(Resources):
            if inspect.isclass(obj):
                setattr(self.resources, name, getattr(Resources, name))

        # Dynamically create custom indicator class
        r = self.request
        r.authorization_method(self.authorization)
        if self._args.tc_proxy_tc:
            self.log.info('Using proxy server {}:{}.'.format(
                self._args.tc_proxy_host, self._args.tc_proxy_port))
            r.proxies = self.proxies
        r.url = '{}/v2/types/indicatorTypes'.format(self._args.tc_api_path)
        response = r.send()

        # check for bad status code and response that is not JSON
        if (int(response.status_code) != 200
                or response.headers.get('content-type') != 'application/json'):
            warn = 'Custom Indicators are not supported.'
            self.log.warn(warn)
            return

        # validate succcessful API results
        data = response.json()
        if data.get('status') != 'Success':
            warn = 'Bad Status: Custom Indicators are not supported.'
            self.log.warn(warn)
            return

        try:
            data = response.json()['data']['indicatorType']
            for entry in data:
                name = self.safe_rt(entry['name'])
                self.indicator_types.append(str(entry['name']))

                if entry['custom'] == 'true':
                    value_fields = []
                    if entry.get('value1Label') is not None and entry.get('value1Label') != '':
                        value_fields.append(entry['value1Label'])
                    if entry.get('value2Label') is not None and entry.get('value2Label') != '':
                        value_fields.append(entry['value2Label'])
                    if entry.get('value3Label') is not None and entry.get('value3Label') != '':
                        value_fields.append(entry['value3Label'])

                    i = self.resources.Indicator(self)
                    custom = {
                        '_api_branch': entry['apiBranch'],
                        '_api_entity': entry['apiEntity'],
                        '_api_uri': '{}/{}'.format(i.api_branch, entry['apiBranch']),
                        '_name': name,
                        '_request_entity': entry['apiEntity'],
                        '_request_uri': '{}/{}'.format(i.api_branch, entry['apiBranch']),
                        '_status_codes': {
                            'DELETE': [200],
                            'GET': [200],
                            'POST': [200],
                            'PUT': [200]
                        },
                        '_value_fields': value_fields
                    }
                    setattr(self.resources, name, Resources.ClassFactory(
                        name, self.resources.Indicator, custom))
        except:
            err = 'Failed retrieving indicator types from API. ({})'.format(sys.exc_info()[0])
            self.log.error(err)
            raise RuntimeError(err)

    def _unknown_args(self, args):
        """Log argparser unknown arguments.

        Args:
            args (list): List of unknown arguments
        """
        for u in args:
            self.log.debug('Unsupported arg found ({0!s}).'.format(u))

    @property
    def args(self):
        """The parsed args from argparser

        Returns:
            (namespace): ArgParser parsed arguments
        """

        if not self._parsed:
            self._args, unknown = self._parser.parse_known_args()
            self._parsed = True

            # log unknown arguments only once
            self._unknown_args(unknown)

        return self._args

    def authorization(self, request_prepped):
        """A method to handle the different methods of authenticating to the ThreatConnect API.

        **Token Based Authorization**::

            {'Authorization': authorization}

        **HMAC Based Authorization**::

            {
                'Authorization': authorization,
                'Timestamp': <unix timestamp>
            }

        Returns:
            (dictionary): An dictionary containing the header values for authorization to ThreatConnect.
        """
        authorization = None

        if self._tc_token is not None:
            authorization = 'TC-Token {0}'.format(self._tc_token)
            if self._tc_token_expires is not None:
                authorization = self._authorization_token_renew()
        elif self._args.api_access_id is not None and self._args.api_secret_key is not None:
            authorization = self.authorization_hmac(request_prepped)

        return authorization

    def authorization_hmac(self, request_prepped):
        """Method for handling HMAC authorization to ThreatConnect API.

        Returns:
            (dictionary): An dictionary containing the header values for authorization to ThreatConnect.
        """
        if request_prepped is not None:
            timestamp = int(time.time())
            signature = "{0}:{1}:{2}".format(request_prepped.path_url, request_prepped.method, timestamp)
            hmac_signature = hmac.new(
                self._args.api_secret_key.strip('\'').encode(), signature.encode(), digestmod=hashlib.sha256).digest()
            authorization = 'TC {0}:{1}'.format(
                self._args.api_access_id, base64.b64encode(hmac_signature).decode())
        else:
            err = 'HMAC authorization requires a PreparedRequest Object'
            self.log.error(err)
            raise RuntimeError(err)

        return {
            'Authorization': authorization,
            'Timestamp': str(timestamp)
        }

    def bulk_enabled(self, owner=None, api_path=None, authorization=None):
        """Check if bulk indicators is enabled for owner

        Using the TC API validate that bulk indicator download is enabled and
        has successfully run for the provided owner.

        Args:
            owner (Optional [string]): Owner name to check.
            api_path (Optional [string]): The url to the ThreatConnect API.
            authorization (Optional [string]): The authorization header value.

        Returns:
            (boolean): True if bulk indicator download is enabled and has run
        """

        if api_path is None:
            api_path = self._args.tc_api_path

        # Dynamically create custom indicator class
        r = self.request
        if authorization is not None:
            r.authorization = authorization
        # r.authorization = self.authorization()
        if owner is not None:
            r.owner = owner
        r.url = '{}/v2/indicators/bulk'.format(self._args.tc_api_path)

        results = r.send()
        try:
            if data.headers['content-type'] == 'application/json':
                data = results.json()

                if data['status'] == 'Success':
                    if (data['data']['bulkStatus']['jsonEnabled'] and
                            data['data']['bulkStatus']['lastRun'] is not None):
                        return True
        except:
            err = 'Failed api request for bulk enabled check. ({})'.format(
                sys.exc_info()[0])
            self.log.error(err)
            raise RuntimeError(err)

        return False

    def exit(self, code=None):
        """Application exit method with proper exit code

        The method will run the Python standard sys.exit() with the exit code
        previously defined via :py:meth:`~tcex.tcex.TcEx.exit_code` or provided
        during the call of this method.

        Args:
            code (Optional [integer]): The exit code value for the app.
        """
        if self._args.tc_token is not None and self._args.tc_log_to_api:
            if self.log is not None and len(self.log.handlers) > 0:
                for handler in self.log.handlers:
                    if handler.get_name() == 'api':
                        handler.log_to_api()

        if code is None:
            self.log.info('exit_code: {}'.format(self._exit_code))
            sys.exit(self._exit_code)
        elif code in [0, 1, 3]:
            self.log.info('exit_code: {}'.format(code))
            sys.exit(code)
        else:
            self.log.error('Invalid exit code')
            sys.exit(1)  # exit with error

    def exit_code(self, code):
        """Set the app exit code

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
            self.log.error('Invalid exit code')

    def expand_indicators(self, indicator, first_indicator=True):
        """Process indicators expanding file hashes/custom indicators into multiple entries

        Args:
            indicator (string): " : " delimeted string
            first_indicator (boolean): Indicate whether to only include the first
                matched indicator.
        """
        indicator_list = []
        for i in indicator.split(' : '):
            indicator_list.append(i)

            if first_indicator:
                break

        return indicator_list

    def message_tc(self, message):
        """Write data to message_tc file in TcEX specified directory.

        This method is used to set and exit message in the ThreatConnect Platform.
        ThreatConnect only supports files of max_message_length.  Any data exceeding
        this limit will be truncated by this method.

        Args:
            message (string): The message to add to message_tc file
        """
        if os.access(self._args.tc_out_path, os.W_OK):
            message_file = '{0!s}/message.tc'.format(self._args.tc_out_path)
        else:
            message_file = 'message.tc'

        message = '{0!s}\n'.format(message)
        if self._max_message_length - len(message) > 0:
            with open(message_file, 'a') as mh:
                mh.write(message)
        elif self._max_message_length > 0:
            with open(message_file, 'a') as mh:
                mh.write(message[:self._max_message_length])

        self._max_message_length -= len(message)

    @property
    def parser(self):
        """The ArgParser parser object

        Returns:
            (ArgumentParser): TcEX instance of ArgParser
        """
        return self._parser

    @property
    def proxies(self):
        """Formats proxy configuration into required format for Python Requests module.

        Generates a dictionary for use with the Python Requests module format
        proxying remote connections.

        **Example Response**
        ::

            {"http": "http://user:pass@10.10.1.10:3128/"}

        Returns:
           (dictionary): Dictionary of proxy settings
        """
        proxies = {}
        if (self._args.tc_proxy_host is not None and
                    self._args.tc_proxy_port is not None):

            if (self._args.tc_proxy_username is not None and
                        self._args.tc_proxy_password is not None):

                proxies ={
                    'http': 'http://{0!s}:{1!s}@{2!s}:{3!s}'.format(
                        self._args.tc_proxy_username, self._args.tc_proxy_password,
                        self._args.tc_proxy_host, self._args.tc_proxy_port),
                    'https': 'https://{0!s}:{1!s}@{2!s}:{3!s}'.format(
                        self._args.tc_proxy_username, self._args.tc_proxy_password,
                        self._args.tc_proxy_host, self._args.tc_proxy_port)
                }
            else:
                proxies = {
                    'http': 'http://{0!s}:{1!s}'.format(
                        self._args.tc_proxy_host, self._args.tc_proxy_port),
                    'https': 'https://{0!s}:{1!s}'.format(
                        self._args.tc_proxy_host, self._args.tc_proxy_port)
                }

        return proxies

    @property
    def request(self):
        """Return an instance of the Request Class

        A wrapper on the Python Request Module specifically for interacting with the
        ThreatConnect API.  However, this can also be used for connecting to other
        API endpoints.

        Returns:
            (instance): An instance of Request Class
        """
        try:
            from tcex_request import TcExRequest
            return TcExRequest(self)
        except ImportError as e:
            err = 'Required Module is not installed ({}).'.format(e)
            self.log.error(err)
            self.message_tc(err)
            self.exit(1)

    def results_tc(self, key, value):
        """Write data to results_tc file in TcEX specified directory

        The TcEx platform support persistent values between executions of the App.  This
        method will store the values for TC to read and put into the Database.

        Args:
            key (string): The data key to be stored
            value (string): The data value to be stored
        """
        if os.access(self._args.tc_out_path, os.W_OK):
            result_file = '{0!s}/results.tc'.format(self._args.tc_out_path)
        else:
            result_file = 'results.tc'

        results = '{0!s} = {1!s}\n'.format(key, value)
        with open(result_file, 'a') as rh:
            rh.write(results)

    @property
    def results_tc_args(self):
        """Read data from results_tc file from previous run of app.

        This method is only required when not running from the with the
        TcEX platform and is only intended for testing apps locally.

        Returns:
            (dictionary): A dictionary of values written to results_tc.
        """
        args = {}
        results = []
        if os.access(self._args.tc_out_path, os.W_OK):
            result_file = '{0!s}/results.tc'.format(self._args.tc_out_path)
        else:
            result_file = 'results.tc'

        if os.path.isfile(result_file):
            with open(result_file, 'r') as rh:
                results = rh.read().strip().split('\n')
            os.remove(result_file)

        for line in results:
            key, value = line.split(' = ')
            args[key] = value

        return args

    @staticmethod
    def safe_rt(resource_type, lower=False):
        """Format Resource Type

        Takes Custom Indicator types with a space characer and return a *safe* string.

        (e.g. *User Agent* is coverted to User_Agent or user_agent.)

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
        return str(resource_type)

    @staticmethod
    def safetag(tag):
        """Truncate tag to match limit (35 characters) of ThreatConnect API.

        .. Attention:: Once ThreatConnect 5.0 is released this will need to be increased to new limit.

        Args:
           tag (string): The tag to be truncated

        Returns:
            (string): The truncated tag
        """
        if len(tag) > 35:
            return TcEx.uni(tag[:35])
        return TcEx.uni(tag)

    @staticmethod
    def safeurl(data):
        """URL encode value for safe HTTP request

        Args:
            data (string): String to URL Encode

        Returns:
            (string): The urlencoded string
        """
        return urllib.quote(TcEx.uni(data), safe='~')

    @staticmethod
    def uni(data):
        """Re-encode poorly encoded unicode data

        Args:
            data (any): Data to ve validated and re-encoded

        Returns:
            (any): Return validate or encoded data

        """
        if data is None or not isinstance(data, types.StringTypes):
            return data
        elif isinstance(data, unicode):
            return unicode(data.encode('utf-8').strip(), errors='ignore')  # re-encode poorly encoded unicode
        elif not isinstance(data, unicode):
            return unicode(data, 'utf-8', errors='ignore')

    ## def proxy_external(self, force_proxy=False):
    ##     """
    ##     """
    ##     session = Session()
    ##     if force_proxy or self._args.tc_proxy_external:
    ##         session.proxies = self.proxies()
    ##
    ##     return session

    ## def use_bulk(self, owner, last_bulk_run):
    ##     """Determine if bulk indicator should be used.
    ##
    ##     Calculate if bulk should be used to download indicators.
    ##
    ##     Args:
    ##         owner (string): Owner name to check.
    ##         last_bulk_run (integer): Seconds since last bulk run.
    ##
    ##     Returns:
    ##         (boolean): True if bulk indicator download is enabled and has run over 86400 seconds ago.
    ##     """
    ##     bulk_run_period = (86400 - 15)  # standard time period for bulk run with 15 second padding
    ##
    ##     if self.bulk_enabled(owner):
    ##         if float(last_bulk_run) == 0.0:
    ##             return True
    ##
    ##         if time.time() - float(last_bulk_run) >= bulk_run_period:
    ##             return True
    ##
    ##     return False