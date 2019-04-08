# -*- coding: utf-8 -*-
"""TcEx Framework"""
import json
import os
import sys
from argparse import Namespace

from .tcex_argparser import TcExArgParser


class TcExArgs(object):
    """Module for handling args passed to App from CLI, SecureParams, and AOT"""

    def __init__(self, tcex):
        """Initialize Class Properties.

        Args:
            tcex (tcex.TcEx): Instance of TcEx class.
        """

        self.tcex = tcex
        self._config_data = {}
        self._default_args = None
        self._default_args_resolved = None
        self._parsed = False
        self._parsed_resolved = False
        self.parser = TcExArgParser()

        # NOTE: odd issue where args is not updating properly
        # if self.default_args.tc_token is not None:
        #     self._tc_token = self.default_args.tc_token
        # if self.default_args.tc_token_expires is not None:
        #     self._tc_token_expires = self.default_args.tc_token_expires

    def _load_secure_params(self):
        """Load secure params from the API.

        # API Response:

        .. code-block:: javascript
            :linenos:
            :lineno-start: 1

            {
                "inputs":
                    {
                        "tc_playbook_db_type": "Redis",
                        "fail_on_error": true,
                        "api_default_org": "TCI"
                    }
            }

        Returns:
            dict: Parameters ("inputs") from the TC API.
        """
        self.tcex.log.info('Loading secure params.')
        # Retrieve secure params and inject them into sys.argv
        r = self.tcex.session.get('/internal/job/execution/parameters')

        # check for bad status code and response that is not JSON
        if not r.ok or r.headers.get('content-type') != 'application/json':
            err = r.text or r.reason
            self.tcex.exit(1, 'Error retrieving secure params from API ({}).'.format(err))

        # return secure params
        return r.json().get('inputs', {})

    def _results_tc_args(self):
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
            if not line or ' = ' not in line:
                continue
            key, value = line.split(' = ')
            if value == 'true':
                value = True
            elif value == 'false':
                value = False
            elif not value:
                value = None
            setattr(self._default_args, key, value)

    def _unknown_args(self, args):
        """Log argparser unknown arguments.

        Args:
            args (list): List of unknown arguments
        """
        for u in args:
            self.tcex.log.warning(u'Unsupported arg found ({}).'.format(u))

    def args(self):
        """Parse args if they have not already been parsed and return the Namespace for args.

        .. Note:: Accessing args should only be done directly in the App.

        Returns:
            (namespace): ArgParser parsed arguments.
        """
        if not self._parsed:  # only resolve once
            self._default_args, unknown = self.parser.parse_known_args()

            # when running locally retrieve any args from the results.tc file.  when running in
            # platform this is done automatically.
            self._results_tc_args()

            # log unknown arguments only once
            self._unknown_args(unknown)

            # set parsed bool to ensure args are only parsed once
            self._parsed = True

            # update args with value from config data or configuration file
            self.args_update()

        return self._default_args

    def args_update(self):
        """Update the argparser namespace with any data from configuration file."""
        for key, value in self._config_data.items():
            setattr(self._default_args, key, value)

    def config(self, config_data):
        """Add configuration data to be injected into sys.argv.

        Below are the default args that the TcEx frameworks supports. Any App specific args
        should be included in the provided data.

        .. code-block:: javascript

            {
              "api_access_id": "$env.API_ACCESS_ID",
              "api_default_org": "$env.API_DEFAULT_ORG",
              "api_secret_key": "$envs.API_SECRET_KEY",
              "tc_api_path": "$env.TC_API_PATH",
              "tc_log_level": "debug",
              "tc_log_path": "log",
              "tc_owner": "MyOwner",
              "tc_proxy_host": "$env.TC_PROXY_HOST",
              "tc_proxy_password": "$envs.TC_PROXY_PASSWORD",
              "tc_proxy_port": "$env.TC_PROXY_PORT",
              "tc_proxy_tc": false,
              "tc_proxy_username": "$env.TC_PROXY_USERNAME"
            }

        Args:
            config (dict): A dictionary of configuration values.
        """
        self._config_data = config_data

    def config_file(self, filename):
        """Load configuration data from provided file and inject values into sys.argv.

        Args:
            config (str): The configuration file name.
        """
        if os.path.isfile(filename):
            with open(filename, 'r') as fh:
                self._config_data = json.load(fh)
        else:
            self.tcex.log.error('Could not load configuration file "{}".'.format(filename))

    @property
    def default_args(self):
        """Parse args and return default args."""
        if self._default_args is None:
            self._default_args, unknown = self.parser.parse_known_args()  # pylint: disable=W0612
            # reinitialize logger with new log level and api settings
            self.tcex._logger()
            if self._default_args.tc_aot_enabled:
                # block for AOT message and get params
                params = self.tcex.playbook.aot_blpop()
                self.inject_params(params)
            elif self._default_args.tc_secure_params:
                # inject secure params from API
                params = self._load_secure_params()
                self.inject_params(params)
        return self._default_args

    def inject_params(self, params):
        """Inject params into sys.argv from secureParams API, AOT, or user provided.

        Args:
            params (dict): A dictionary containing all parameters that need to be injected as args.
        """

        for arg, value in params.items():
            cli_arg = '--{}'.format(arg)
            if cli_arg in sys.argv:
                # arg already passed on the command line
                self.tcex.log.debug('skipping existing arg: {}'.format(cli_arg))
                continue

            # ThreatConnect secure/AOT params should be updated in the future to proper JSON format.
            # MultiChoice data should be represented as JSON array and Boolean values should be a
            # JSON boolean and not a string.
            param_data = self.tcex.install_json_params.get(arg) or {}
            if param_data.get('type', '').lower() == 'multichoice':
                # update "|" delimited value to a proper array for params that have type of
                # MultiChoice.
                value = value.split('|')
            elif param_data.get('type', '').lower() == 'boolean':
                # update value to be a boolean instead of string "true"/"false".
                value = self.tcex.utils.to_bool(value)
            elif arg in self.tc_bool_args:
                value = self.tcex.utils.to_bool(value)

            if isinstance(value, (bool)):
                # handle bool values as flags (e.g., --flag) with no value
                if value is True:
                    sys.argv.append(cli_arg)
            elif isinstance(value, (list)):
                for mcv in value:
                    sys.argv.append('{}={}'.format(cli_arg, mcv))
            else:
                sys.argv.append('{}={}'.format(cli_arg, value))

        # reset default_args now that values have been injected into sys.argv
        self._default_args, unknown = self.parser.parse_known_args()  # pylint: disable=W0612

        # reinitialize logger with new log level and api settings
        self.tcex._logger()

    def resolved_args(self):
        """Parse args if they have not already been parsed and return the Namespace for args.

        .. Note:: Accessing args should only be done directly in the App.

        Returns:
            (namespace): ArgParser parsed arguments with Playbook variables automatically resolved.
        """

        if not self._parsed_resolved:  # only resolve once
            self.args()

            # create new args Namespace for resolved args
            self._default_args_resolved = Namespace()

            # iterate over args and resolve any playbook variables
            for arg in vars(self._default_args):
                arg_val = getattr(self._default_args, arg)
                if arg not in self.tc_reserved_args:
                    if isinstance(arg_val, (str)):
                        arg_val = self.tcex.playbook.read(arg_val)
                setattr(self._default_args_resolved, arg, arg_val)

            # set parsed bool to ensure args are only parsed once
            self._parsed_resolved = True

        return self._default_args_resolved

    @property
    def tc_bool_args(self):
        """A list of default ThreatConnect Args that are booleans."""
        return [
            'apply_proxy_external',
            'apply_proxy_ext',
            'apply_proxy_tc',
            'batch_halt_on_error',
            'tc_aot_enabled',
            'tc_log_to_api',
            'tc_proxy_external',
            'tc_proxy_tc',
            'tc_secure_params',
            'tc_verify',
        ]

    @property
    def tc_reserved_args(self):
        """A list of *all* ThreatConnect reserved arg values."""
        return [
            'tc_token',
            'tc_token_expires',
            'api_access_id',
            'api_secret_key',
            'batch_action',
            'batch_chunk',
            'batch_halt_on_error',
            'batch_poll_interval',
            'batch_interval_max',
            'batch_write_type',
            'tc_playbook_db_type',
            'tc_playbook_db_context',
            'tc_playbook_db_path',
            'tc_playbook_db_port',
            'tc_playbook_out_variables',
            'api_default_org',
            'tc_api_path',
            'tc_in_path',
            'tc_log_file',
            'tc_log_path',
            'tc_out_path',
            'tc_secure_params',
            'tc_temp_path',
            'tc_user_id',
            'tc_proxy_host',
            'tc_proxy_port',
            'tc_proxy_username',
            'tc_proxy_password',
            'tc_proxy_external',
            'tc_proxy_tc',
            'tc_log_to_api',
            'tc_log_level',
            'logging',
        ]
