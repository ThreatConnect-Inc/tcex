# -*- coding: utf-8 -*-
"""TcEx Framework"""
import json
import os
from argparse import Namespace
from .argument_parser import TcArgumentParser


class Args(object):
    """Module for handling args passed to App from CLI, SecureParams, and AOT"""

    def __init__(self, tcex):
        """Initialize Class Properties.

        Args:
            tcex (tcex.TcEx): Instance of TcEx class.
        """
        self.tcex = tcex

        # track optional arg input to only parse once
        self._loaded_aot = False
        self._loaded_secure_params = False

        self._parsed = False
        self._parsed_resolved = False

        # parser and arg properties
        self.parser = TcArgumentParser()
        self._default_args, self._unknown_args = self.parser.parse_known_args()
        self.register_token()  # register token as soon as possible
        self._default_args_resolved = Namespace()
        self.parser.namespace = self._default_args

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
        # Retrieve secure params
        r = self.tcex.session.get('/internal/job/execution/parameters')

        # check for bad status code and response that is not JSON
        if not r.ok:
            err = r.text or r.reason
            raise RuntimeError('Error retrieving secure params from API ({}).'.format(err))

        secure_params = {}
        try:
            secure_params = r.json()['inputs']
        except (AttributeError, KeyError, TypeError, ValueError):  # pragma: no cover
            err = r.text or r.reason
            raise RuntimeError('Error retrieving secure params from API ({}).'.format(err))

        return secure_params

    def _results_tc_args(self):  # pragma: no cover
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

    def args(self):
        """Parse args if they have not already been parsed and return the Namespace for args.

        .. Note:: Accessing args should only be done directly in the App.

        Returns:
            (namespace): ArgParser parsed arguments.
        """
        if not self._parsed:  # only resolve once
            self.init_default_args()

            # initialize default args
            args, self._unknown_args = self.parser.parse_known_args(namespace=self._default_args)
            self.config(args.__dict__)

            # when running locally retrieve any args from the results.tc file.  when running in
            # platform this is done automatically.
            self._results_tc_args()

            # add api handler
            if self._default_args.tc_token is not None and self._default_args.tc_log_to_api:
                self.tcex.logger.add_api_handler()

            # set parsed bool to ensure args are only parsed once
            self._parsed = True

        return self._default_args

    def config(self, config_data, complete=True, replace=False):
        """Add configuration data to update default_args.

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
        if isinstance(config_data, dict):
            if replace:
                # start with fresh args for pytest cases
                self._default_args, self._unknown_args = self.parser.parse_known_args()
                self._parsed = False

            # update the arg Namespace via dict
            self._default_args.__dict__.update(config_data)
            self.register_token()  # register token as soon as possible

            if complete:
                # mark arg parsing as done
                self.parsing_complete()

    def config_file(self, filename):
        """Load configuration data from provided file and update default_args.

        Args:
            config (str): The configuration file name.
        """
        if filename is not None:
            if os.path.isfile(filename):
                with open(filename, 'r') as fh:
                    self.config(json.load(fh))
            else:
                self.tcex.log.error('Could not load configuration file "{}".'.format(filename))

    @property
    def default_args(self):
        """Parse args and return default args."""
        return self._default_args

    def parsing_complete(self):
        """Mark args as parsed."""
        # add rotating log handler
        self.tcex.logger.add_rotating_file_handler(
            name='rfh',
            filename=self.default_args.tc_log_file,
            path=self.default_args.tc_log_path,
            backup_count=self.default_args.tc_log_backup_count,
            max_bytes=self.default_args.tc_log_max_bytes,
        )

        # replay cached log events
        self.tcex.logger.replay_cached_events(handler_name='cache')

        # remove cache handler
        self.tcex.logger.remove_handler_by_name('cache')

        # log unknown arguments only once
        self.unknown_args()

    def register_token(self):
        """Register token if provided in args (non-service Apps)"""
        # TODO: swap MainThread with threading.current_thread().name ?
        if self._default_args.tc_token is not None:
            self.tcex.default_args = self._default_args
            self.tcex.token.register_token(
                'MainThread', self._default_args.tc_token, self._default_args.tc_token_expires
            )

    def resolved_args(self):
        """Return namespace of args that have all PB variable automatically resolved.

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

    def init_default_args(self):
        """Parse args and return default args."""
        # log system and App data
        self.tcex.logger.log_info(self._default_args)

        if self._default_args.tc_aot_enabled and not self._loaded_aot:
            # update default_args with AOT params
            params = self.tcex.playbook.aot_blpop()
            updated_params = self.update_params(params)
            self.config(updated_params, False)
            self._loaded_aot = True  # only load once
        elif self._default_args.tc_secure_params and not self._loaded_secure_params:
            # update default_args with secure params from API
            params = self._load_secure_params()
            updated_params = self.update_params(params)
            self.config(updated_params, False)
            self._loaded_secure_params = True  # only load once

    @property
    def tc_bool_args(self):
        """Return a list of default ThreatConnect Args that are booleans."""
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
        """Return a list of *all* ThreatConnect reserved arg values."""
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

    def unknown_args(self):
        """Log argparser unknown arguments.

        Args:
            args (list): List of unknown arguments
        """
        for u in self._unknown_args:
            self.tcex.log.warning(u'Unsupported arg found ({}).'.format(u))

    def update_params(self, params):
        """Update params provided by AOT and Secure Params to be of the proper value

        Args:
            params (dict): A dictionary containing params to update default_args
        """
        updated_params = {}
        for arg, value in params.items():
            # ThreatConnect secure/AOT params could be updated in the future to proper JSON format.
            # MultiChoice data should be represented as JSON array and Boolean values should be a
            # JSON boolean and not a string.
            param_data = self.tcex.ij.params_dict.get(arg) or {}
            param_type = param_data.get('type', '').lower()
            param_allow_multiple = self.tcex.utils.to_bool(param_data.get('allowMultiple', False))

            if param_type == 'multichoice' or param_allow_multiple:
                # update delimited value to an array for params that have type of MultiChoice.
                if not isinstance(value, dict):
                    value = value.split(self.tcex.ij.list_delimiter)
            elif param_type == 'boolean':
                # convert boolean input that are passed in as a string ("true" -> True)
                value = self.tcex.utils.to_bool(value)
            elif arg in self.tc_bool_args:
                # convert default boolean args that are passed in as a string ("true" -> True)
                value = self.tcex.utils.to_bool(value)

            # add args and updated value to dict
            updated_params[arg] = value

        # update args
        return updated_params
