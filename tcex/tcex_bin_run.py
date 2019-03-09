#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework App Testing Module."""
import base64
import binascii
import collections
import difflib
import hashlib
import json
import logging
import operator
import os
import re
import signal
import subprocess
import sys
from datetime import datetime

from six import string_types
import colorama as c


from tcex import TcEx
from .tcex_bin import TcExBin


class TcExRun(TcExBin):
    """Run profiles for ThreatConnect Job or Playbook Apps.

    Args:
        _args (namespace): The argparser args Namespace.
    """

    def __init__(self, _args):
        """Initialize Class properties.

        Args:
            _args (namespace): The argparser args Namespace.
        """
        super(TcExRun, self).__init__(_args)

        # properties
        self._signal_handler_init()
        self._config = None
        self._profile = {}
        self._staging_data = None
        self.container = None
        self.reports = Reports()
        self.tcex = None
        self.docker_image = 'tcintegrations/tci-dev:latest'

        # logger
        self.log = self._logger()

        self._clear_redis_tracker = []
        self.json_report = {}
        self.max_diff = 10
        self.sleep = 0
        # data from install.json
        self.display_name = None
        self.program_main = None
        self.program_version = None
        self.runtime_level = None

        self.shell = False
        # removing this value as it appears to cause an issue with some characters in args
        # if platform.system() == 'Windows':
        #    self.shell = True

    def _create_tc_dirs(self):
        """Create app directories for logs and data files."""
        tc_log_path = self.profile.get('args', {}).get('tc_log_path')
        if tc_log_path is not None and not os.path.isdir(tc_log_path):
            os.makedirs(tc_log_path)
        tc_out_path = self.profile.get('args', {}).get('tc_out_path')
        if tc_out_path is not None and not os.path.isdir(tc_out_path):
            os.makedirs(tc_out_path)
        tc_tmp_path = self.profile.get('args', {}).get('tc_tmp_path')
        if tc_tmp_path is not None and not os.path.isdir(tc_tmp_path):
            os.makedirs(tc_tmp_path)

    def _load_config_include(self, include_directory):
        """Load included configuration files.

        Args:
            include_directory (str): The name of the config include directory.

        Returns:
            list: A list of all profiles for the current App.
        """
        include_directory = os.path.join(self.app_path, include_directory)
        if not os.path.isdir(include_directory):
            msg = 'Provided include directory does not exist ({}).'.format(include_directory)
            sys.exit(msg)

        profiles = []
        for filename in sorted(os.listdir(include_directory)):
            if filename.endswith('.json'):
                self.log.info('Loading config: {}'.format(filename))
                print('Include File: {}{}{}'.format(c.Style.BRIGHT, c.Fore.MAGENTA, filename))
                config_file = os.path.join(include_directory, filename)
                with open(config_file) as data_file:
                    try:
                        profiles.extend(json.load(data_file))
                    except ValueError as e:
                        print('Invalid JSON file: {}{}{}'.format(c.Style.BRIGHT, c.Fore.RED, e))
                        sys.exit(1)
        return profiles

    def _logger(self):
        """Create logger instance.

        Returns:
            logger: An instance of logging
        """
        log_level = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL,
        }
        level = log_level.get(self.args.logging_level.lower())

        # Formatter
        tx_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s '
        tx_format += '(%(funcName)s:%(lineno)d)'
        formatter = logging.Formatter(tx_format)

        # Logger
        log = logging.getLogger('tcrun')

        # # Stream Handler
        # sh = logging.StreamHandler()
        # sh.set_name('sh')
        # sh.setLevel(level)
        # sh.setFormatter(formatter)
        # log.addHandler(sh)

        # File Handler
        if not os.access('log', os.W_OK):
            os.makedirs('log')
        logfile = os.path.join('log', 'run.log')
        fh = logging.FileHandler(logfile)
        fh.set_name('fh')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        log.addHandler(fh)

        log.setLevel(level)
        log.info('Logging Level: {}'.format(logging.getLevelName(level)))
        return log

    def _signal_handler_init(self):
        """Catch interupt signals."""
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signal_interupt, frame):  # pylint: disable=W0613
        """Handle singal interrupt.

        Args:
            signal_interupt ([type]): [Description]
            frame ([type]): [Description]
        """
        if self.container is not None:
            print('{}{}Stopping docker container.'.format(c.Style.BRIGHT, c.Fore.YELLOW))
            self.container.stop()
        print('{}{}Interrupt signal received.'.format(c.Style.BRIGHT, c.Fore.RED))
        self.log.error('tcrun received an interrupt signal and will now exit.')
        sys.exit(1)

    @property
    def _tcex_required_args(self):
        """Get just the args required for data services."""
        return [
            'api_access_id',
            'api_secret_key',
            # 'tc_log_level',
            'tc_api_path',
            'tc_log_file',
            'tc_log_path',
            'tc_out_path',
            'tc_playbook_db_context',
            'tc_playbook_db_path',
            'tc_playbook_db_port',
            'tc_playbook_db_type',
            'tc_proxy_external',
            'tc_proxy_host',
            'tc_proxy_port',
            'tc_proxy_password',
            'tc_proxy_tc',
            'tc_proxy_username',
            'tc_temp_path',
        ]

    @property
    def _vars_match(self):
        """Regular expression to match playbook variable."""
        return re.compile(
            r'#([A-Za-z]+)'  # match literal (#App) at beginning of String
            r':([\d]+)'  # app id (:7979)
            r':([A-Za-z0-9_\.\-\[\]]+)'  # variable name (:variable_name)
            r'!(StringArray|BinaryArray|KeyValueArray'  # variable type (array)
            r'|TCEntityArray|TCEnhancedEntityArray'  # variable type (array)
            r'|String|Binary|KeyValue|TCEntity|TCEnhancedEntity'  # variable type
            r'|(?:(?!String)(?!Binary)(?!KeyValue)'  # non matching for custom
            r'(?!TCEntity)(?!TCEnhancedEntity)'  # non matching for custom
            r'[A-Za-z0-9_-]+))'  # variable type (custom)
        )

    def autoclear(self):
        """Clear Redis and ThreatConnect data from staging data."""
        for sd in self.staging_data:
            data_type = sd.get('data_type', 'redis')
            if data_type == 'redis':
                self.clear_redis(sd.get('variable'), 'auto-clear')
            elif data_type == 'redis-array':
                self.clear_redis(sd.get('variable'), 'auto-clear')
                for variables in sd.get('data', {}).get('variables') or []:
                    self.clear_redis(variables.get('value'), 'auto-clear')
            elif data_type == 'threatconnect':
                # self.clear_tc(sd.get('data_owner'), sd.get('data', {}), 'auto-clear')
                # self.clear_redis(sd.get('variable'), 'auto-clear')
                pass
            elif data_type == 'threatconnect-association':
                # assuming these have already been cleared
                pass
            elif data_type == 'threatconnect-batch':
                for group in sd.get('data', {}).get('group') or []:
                    self.clear_tc(sd.get('data_owner'), group, 'auto-clear')
                    self.clear_redis(group.get('variable'), 'auto-clear')
                for indicator in sd.get('data', {}).get('indicator') or []:
                    self.clear_tc(sd.get('data_owner'), indicator, 'auto-clear')
                    self.clear_redis(indicator.get('variable'), 'auto-clear')
        for vd in self.profile.get('validations') or []:
            data_type = vd.get('data_type', 'redis')
            variable = vd.get('variable')
            if data_type == 'redis':
                self.clear_redis(variable, 'auto-clear')

    def clear(self):
        """Clear Redis and ThreatConnect data defined in profile.

        Redis Data:

        .. code-block:: javascript

            {
              "data_type": "redis",
              "variable": "#App:4768:tc.adversary!TCEntity"
            }

        ThreatConnect Data:

        .. code-block:: javascript

            {
              "data_type": "threatconnect",
              "owner": "TCI",
              "type": "Address",
              "value": "1.1.1.1"
            }
        """
        for clear_data in self.profile.get('clear') or []:
            if clear_data.get('data_type') == 'redis':
                self.clear_redis(clear_data.get('variable'), 'clear')
            elif clear_data.get('data_type') == 'threatconnect':
                self.clear_tc(clear_data.get('owner'), clear_data, 'clear')

    def clear_redis(self, variable, clear_type):
        """Delete Redis data for provided variable.

        Args:
            variable (str): The Redis variable to delete.
            clear_type (str): The type of clear action.
        """
        if variable is None:
            return
        if variable in self._clear_redis_tracker:
            return
        if not re.match(self._vars_match, variable):
            return
        self.log.info('[{}] Deleting redis variable: {}.'.format(clear_type, variable))
        print('Clearing Variables: {}{}{}'.format(c.Style.BRIGHT, c.Fore.MAGENTA, variable))
        self.tcex.playbook.delete(variable)
        self._clear_redis_tracker.append(variable)

    def clear_tc(self, owner, data, clear_type):
        """Delete threat intel from ThreatConnect platform.

        Args:
            owner (str): The ThreatConnect owner.
            data (dict): The data for the threat intel to clear.
            clear_type (str): The type of clear action.
        """
        batch = self.tcex.batch(owner, action='Delete')
        tc_type = data.get('type')
        path = data.get('path')
        if tc_type in self.tcex.group_types:
            name = self.tcex.playbook.read(data.get('name'))
            name = self.path_data(name, path)
            if name is not None:
                print(
                    'Deleting ThreatConnect Group: {}{}{}'.format(
                        c.Style.BRIGHT, c.Fore.MAGENTA, name
                    )
                )
                self.log.info(
                    '[{}] Deleting ThreatConnect {} with name: {}.'.format(
                        clear_type, tc_type, name
                    )
                )
                batch.group(tc_type, name)
        elif tc_type in self.tcex.indicator_types:
            if data.get('summary') is not None:
                summary = self.tcex.playbook.read(data.get('summary'))
            else:
                resource = self.tcex.resource(tc_type)
                summary = resource.summary(data)
            summary = self.path_data(summary, path)
            if summary is not None:
                print(
                    'Deleting ThreatConnect Indicator: {}{}{}'.format(
                        c.Style.BRIGHT, c.Fore.MAGENTA, summary
                    )
                )
                self.log.info(
                    '[{}] Deleting ThreatConnect {} with value: {}.'.format(
                        clear_type, tc_type, summary
                    )
                )
                batch.indicator(tc_type, summary)
        batch_results = batch.submit()
        self.log.debug('[{}] Batch Results: {}'.format(clear_type, batch_results))
        for error in batch_results.get('errors') or []:
            self.log.error('[{}] Batch Error: {}'.format(clear_type, error))

    @staticmethod
    def data_endswith(db_data, user_data):
        """Validate data ends with user data.

        Args:
            db_data (str): The data store in Redis.
            user_data (str): The user provided data.

        Returns:
            bool: True if the data passed validation.
        """
        if db_data is not None and db_data.endswith(user_data):
            return True
        return False

    @staticmethod
    def data_in_db(db_data, user_data):
        """Validate db data in user data.

        Args:
            db_data (str): The data store in Redis.
            user_data (list): The user provided data.

        Returns:
            bool: True if the data passed validation.
        """
        if isinstance(user_data, list):
            if db_data in user_data:
                return True
        return False

    @staticmethod
    def data_in_user(db_data, user_data):
        """Validate user data in db data.

        Args:
            db_data (list): The data store in Redis.
            user_data (str): The user provided data.

        Returns:
            bool: True if the data passed validation.
        """
        if user_data in db_data:
            return True
        return False

    @staticmethod
    def data_it(db_data, user_type):
        """Validate data is type.

        Args:
            db_data (dict|str|list): The data store in Redis.
            user_data (str): The user provided data.

        Returns:
            bool: True if the data passed validation.
        """
        data_type = {
            'array': (list),
            # 'binary': (string_types),
            # 'bytes': (string_types),
            'dict': (dict),
            'entity': (dict),
            'list': (list),
            'str': (string_types),
            'string': (string_types),
        }
        # user_type_tuple = tuple([data_type[t] for t in user_types])
        # if isinstance(db_data, user_type_tuple):
        if user_type is None:
            if db_data is None:
                return True
        elif user_type.lower() in ['null', 'none']:
            if db_data is None:
                return True
        elif user_type.lower() in 'binary':
            # this test is not 100%, but should be good enough
            try:
                base64.b64decode(db_data)
                return True
            except Exception:
                return False
        elif data_type.get(user_type.lower()) is not None:
            if isinstance(db_data, data_type.get(user_type.lower())):
                return True
        return False

    @staticmethod
    def data_kva_compare(db_data, user_data):
        """Validate key/value data in KeyValueArray.

        Args:
            db_data (list): The data store in Redis.
            user_data (dict): The user provided data.

        Returns:
            bool: True if the data passed validation.
        """
        for kv_data in db_data:
            if kv_data.get('key') == user_data.get('key'):
                if kv_data.get('value') == user_data.get('value'):
                    return True
        return False

    @staticmethod
    def data_not_in(db_data, user_data):
        """Validate data not in user data.

        Args:
            db_data (str): The data store in Redis.
            user_data (list): The user provided data.

        Returns:
            bool: True if the data passed validation.
        """
        if isinstance(user_data, list):
            if db_data not in user_data:
                return True
        return False

    @staticmethod
    def data_startswith(db_data, user_data):
        """Validate data starts with user data.

        Args:
            db_data (str): The data store in Redis.
            user_data (str): The user provided data.

        Returns:
            bool: True if the data passed validation.
        """
        if db_data is not None and db_data.startswith(user_data):
            return True
        return False

    @staticmethod
    def data_string_compare(db_data, user_data):
        """Validate string removing all white space before comparison.

        Args:
            db_data (str): The data store in Redis.
            user_data (str): The user provided data.

        Returns:
            bool: True if the data passed validation.
        """
        db_data = ''.join(db_data.split())
        user_data = ''.join(user_data.split())
        if operator.eq(db_data, user_data):
            return True
        return False

    def deep_diff(self, db_data, user_data):
        """Validate data in user data.

        Args:
            db_data (dict|str|list): The data store in Redis.
            user_data (dict|str|list): The user provided data.

        Returns:
            bool: True if the data passed validation.
        """
        # NOTE: tcex does include the deepdiff library as a dependencies since it is only
        # required for local testing.
        try:
            from deepdiff import DeepDiff
        except ImportError:
            print('Could not import DeepDiff module (try "pip install deepdiff").')
            sys.exit(1)

        try:
            ddiff = DeepDiff(db_data, user_data, ignore_order=True)
        except KeyError:
            return False
        except NameError:
            return False
        if ddiff:
            self.tcex.log.info(u'[validate] Diff      : {}'.format(ddiff))
            return False
        return True

    @property
    def included_profiles(self):
        """Load all profiles."""
        profiles = []
        for directory in self.tcex_json.get('profile_include_dirs') or []:
            profiles.extend(self._load_config_include(directory))
        return profiles

    def json_compare(self, db_data, user_data):
        """Validate data in user data.

        Args:
            db_data (str): The data store in Redis.
            user_data (str): The user provided data.

        Returns:
            bool: True if the data passed validation.
        """
        if isinstance(db_data, (string_types)):
            db_data = json.loads(db_data)
        if isinstance(user_data, (string_types)):
            user_data = json.loads(user_data)
        return self.deep_diff(db_data, user_data)

    def load_tcex(self):
        """Inject required TcEx CLI Args."""
        for arg, value in self.profile.get('profile_args', {}).data.items():
            if arg not in self._tcex_required_args:
                continue

            # add new log file name and level
            sys.argv.extend(['--tc_log_file', 'tcex.log'])
            sys.argv.extend(['--tc_log_level', 'error'])
            # format key
            arg = '--{}'.format(arg)
            if isinstance(value, (bool)):
                # handle bool values as flags (e.g., --flag) with no value
                if value:
                    sys.argv.append(arg)
            else:
                sys.argv.append(arg)
                sys.argv.append('{}'.format(value))

        self.tcex = TcEx()

        # reset singal handlers
        self._signal_handler_init()

    @property
    def operators(self):
        """Return dict of Validation Operators.

        + deep-diff (dd): This operator can compare any object that can be represented as JSON.
        + eq: This operator does a equal to comparison for String and StringArray variables.
        + ends-with (ew): This operator compares the end of a String with a user provided value.
        + ge: This operator does a greater than or equal to comparison for String variables.
        + gt: This operator does a greater than comparison for String variables.
        + json-compare (jc): This operator will convert a String output variable to a JSON object
          (dict) and compare to user provided data.
        + key-value-compare (kva): This operator will validate that key/value data is in
          KeyValueArray.
        + in: This operator will check to see if a String output variable is in an user provided
          array.
        + in-user-data: This operator will validate that user provided String value is in output
          StringArray variable.
        + not-in (ni): This operator will check to see if a String variable is **not** in an user
          provided array.
        + is-type (it): This operator will check to see if the variable "type" is equal to the user
          provided "type".
        + le: This operator does a less than or equal to comparison for String variables.
        + lt: This operator does a less than comparison for String variables.
        + ne: This operator does a **not** equal to comparison for String and StringArray variables.
        + string-compare (se):
        + starts-with (sw): This operator compares the start of a String with a user provided value.
        """
        return {
            'dd': self.deep_diff,
            'deep-diff': self.deep_diff,
            'eq': operator.eq,
            'ew': self.data_endswith,
            'ends-with': self.data_endswith,
            'ge': operator.ge,
            'gt': operator.gt,
            'jc': self.json_compare,
            'json-compare': self.json_compare,
            'kva': self.data_kva_compare,
            'key-value-compare': self.data_kva_compare,
            'in': self.data_in_db,
            'in-db-data': self.data_in_db,
            'in-user-data': self.data_in_user,
            'ni': self.data_not_in,
            'not-in': self.data_not_in,
            'it': self.data_it,  # is type
            'is-type': self.data_it,
            'lt': operator.lt,
            'le': operator.le,
            'ne': operator.ne,
            'se': self.data_string_compare,
            'string-compare': self.data_string_compare,
            'sw': self.data_startswith,
            'starts-with': self.data_startswith,
        }

    def path_data(self, variable_data, path):
        """Return JMESPath data.

        Args:
            variable_data (str): The JSON data to run path expression.
            path (str): The JMESPath expression.

        Returns:
            dict: The resulting data from JMESPath.
        """
        # NOTE: tcex does include the jmespath library as a dependencies since it is only
        # required for local testing.
        try:
            import jmespath
        except ImportError:
            print('Could not import jmespath module (try "pip install jmespath").')
            sys.exit(1)

        if isinstance(variable_data, string_types):
            # try to convert string into list/dict before using expression
            try:
                variable_data = json.loads(variable_data)
            except Exception:
                self.log.debug('String value ({}) could not JSON serialized.'.format(variable_data))
        if path is not None and isinstance(variable_data, (dict, list)):
            expression = jmespath.compile(path)
            variable_data = expression.search(
                variable_data, jmespath.Options(dict_cls=collections.OrderedDict)
            )
        return variable_data

    @property
    def profile(self):
        """Return the current profile."""
        return self._profile

    @profile.setter
    def profile(self, profile):
        """Set the current profile.

        Args:
            profile (dict): The profile data.
        """
        # clear staging data
        self._staging_data = None
        # retrieve language from install.json or assume Python
        lang = profile.get('install_json', {}).get('programLanguage', 'PYTHON')
        # load instance of ArgBuilder
        profile_args = ArgBuilder(lang, self.profile_args(profile.get('args')))
        # set current profile
        self._profile = profile
        # attach instance to current profile
        self._profile['profile_args'] = profile_args
        # load tcex module after current profile is set
        self.load_tcex()
        # select report for current profile
        self.reports.profile(profile.get('profile_name'))
        # create required directories for tcrun to function
        self._create_tc_dirs()

    @staticmethod
    def profile_args(_args):
        """Return args for v1, v2, or v3 structure.

        Args:
            _args (dict): The args section from the profile.

        Returns:
            dict: A collapsed version of the args dict.
        """
        # TODO: clean this up in a way that works for both py2/3
        if (
            _args.get('app', {}).get('optional') is not None
            or _args.get('app', {}).get('required') is not None
        ):
            # detect v3 schema
            app_args_optional = _args.get('app', {}).get('optional', {})
            app_args_required = _args.get('app', {}).get('required', {})
            default_args = _args.get('default', {})
            _args = {}
            _args.update(app_args_optional)
            _args.update(app_args_required)
            _args.update(default_args)
        elif _args.get('app') is not None and _args.get('default') is not None:
            # detect v2 schema
            app_args = _args.get('app', {})
            default_args = _args.get('default', {})
            _args = {}
            _args.update(app_args)
            _args.update(default_args)

        return _args

    @property
    def profiles(self):
        """Return all selected profiles."""
        selected_profiles = []
        for config in self.included_profiles:
            profile_selected = False
            profile_name = config.get('profile_name')

            if profile_name == self.args.profile:
                profile_selected = True
            elif config.get('group') is not None and config.get('group') == self.args.group:
                profile_selected = True
            elif self.args.group in config.get('groups', []):
                profile_selected = True

            if profile_selected:
                install_json_filename = config.get('install_json')
                ij = {}
                if install_json_filename is not None:
                    ij = self.load_install_json(install_json_filename)
                config['install_json'] = ij
                selected_profiles.append(config)

            self.reports.add_profile(config, profile_selected)

        if not selected_profiles:
            print('{}{}No profiles selected to run.'.format(c.Style.BRIGHT, c.Fore.YELLOW))

        return selected_profiles

    def report(self):
        """Format and output report data to screen."""
        print('\n{}{}{}'.format(c.Style.BRIGHT, c.Fore.CYAN, 'Report:'))
        # report headers
        print('{!s:<85}{!s:<20}'.format('', 'Validations'))
        print(
            '{!s:<60}{!s:<25}{!s:<10}{!s:<10}'.format(
                'Profile:', 'Execution:', 'Passed:', 'Failed:'
            )
        )
        for r in self.reports:
            d = r.data
            if not d.get('selected'):
                continue

            # execution
            execution_color = c.Fore.RED
            execution_text = 'Failed'
            if d.get('execution_success'):
                execution_color = c.Fore.GREEN
                execution_text = 'Passed'

            # pass count
            pass_count_color = c.Fore.GREEN
            pass_count = d.get('validation_pass_count', 0)
            # fail count
            fail_count = d.get('validation_fail_count', 0)
            fail_count_color = c.Fore.GREEN
            if fail_count > 0:
                fail_count_color = c.Fore.RED

            # report row
            print(
                '{!s:<60}{}{!s:<25}{}{!s:<10}{}{!s:<10}'.format(
                    d.get('name'),
                    execution_color,
                    execution_text,
                    pass_count_color,
                    pass_count,
                    fail_count_color,
                    fail_count,
                )
            )

        # write report to disk
        if self.args.report:
            with open(self.args.report, 'w') as outfile:
                outfile.write(str(self.reports))

    def run(self):
        """Run the App using the current profile.

        The current profile has the install_json and args pre-loaded.
        """
        install_json = self.profile.get('install_json')
        program_language = self.profile.get('install_json').get('programLanguage', 'python').lower()

        print('{}{}'.format(c.Style.BRIGHT, '-' * 100))

        if install_json.get('programMain') is not None:
            program_main = install_json.get('programMain').replace('.py', '')
        elif self.profile.get('script') is not None:
            # TODO: remove this option on version 1.0.0
            program_main = self.profile.get('script').replace('.py', '')
        else:
            print('{}{}No Program Main or Script defined.'.format(c.Style.BRIGHT, c.Fore.RED))
            sys.exit(1)

        self.run_display_profile(program_main)
        self.run_display_description()
        self.run_validate_program_main(program_main)

        # get the commands
        commands = self.run_commands(program_language, program_main)
        self.log.info('[run] Running command {}'.format(commands.get('print_command')))

        # output command
        print(
            'Executing: {}{}{}'.format(c.Style.BRIGHT, c.Fore.GREEN, commands.get('print_command'))
        )

        if self.args.docker:
            return self.run_docker(commands)

        return self.run_local(commands)

    def run_commands(self, program_language, program_main):
        """Return the run Print Command.

        Args:
            program_language (str): The language of the current App/Project.
            program_main (str): The executable name.

        Returns:
            dict: A dictionary containing the run command and a printable version of the command.
        """
        # build the command
        if program_language == 'python':
            python_exe = sys.executable
            ptvsd_host = 'localhost'
            if self.args.docker:
                # use the default python command in the container
                python_exe = 'python'
                ptvsd_host = '0.0.0.0'

            if self.args.vscd:
                self.update_environment()  # update PYTHONPATH for local testing
                command = [
                    python_exe,
                    '-m',
                    'ptvsd',
                    '--host',
                    ptvsd_host,
                    '--port',
                    self.args.vscd_port,
                    '--wait',
                    '{}.py'.format(program_main),
                ]
            else:
                command = [python_exe, '.', program_main]

            # exe command
            cli_command = [str(s) for s in command + self.profile.get('profile_args').standard]

            # print command
            # print_command = ' '.join(command + self.profile.get('profile_args').masked)
            print_command = ' '.join(
                str(s) for s in command + self.profile.get('profile_args').masked
            )
            if self.args.unmask:
                # print_command = ' '.join(command + self.profile.get('profile_args').quoted)
                print_command = ' '.join(
                    str(s) for s in command + self.profile.get('profile_args').quoted
                )

        elif program_language == 'java':
            if self.args.docker:
                command = ['java', '-cp', self.tcex_json.get('class_path', './target/*')]
            else:
                command = [
                    self.tcex_json.get('java_path', program_language),
                    '-cp',
                    self.tcex_json.get('class_path', './target/*'),
                ]

            # exe command
            cli_command = command + self.profile.get('profile_args').standard + [program_main]

            # print command
            print_command = ' '.join(
                command + self.profile.get('profile_args').masked + [program_main]
            )
            if self.args.unmask:
                print_command = ' '.join(
                    command + self.profile.get('profile_args').quoted + [program_main]
                )
        return {'cli_command': cli_command, 'print_command': print_command}

    def run_local(self, commands):
        """Run the App on local system.

        Args:
            commands (dict): A dictionary of the CLI commands.

        Returns:
            int: The exit code of the subprocess command.
        """
        process = subprocess.Popen(
            commands.get('cli_command'),
            shell=self.shell,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        out, err = process.communicate()

        # display app output
        self.run_display_app_output(out)
        self.run_display_app_errors(err)

        # Exit Code
        return self.run_exit_code(process.returncode)

    def run_docker(self, commands):
        """Run App in Docker Container.

        Args:
            commands (dict): A dictionary of the CLI commands.

        Returns:
            int: The exit code of the subprocess command.
        """
        try:
            import docker
        except ImportError:
            print(
                '{}{}Could not import docker module (try "pip install docker").'.format(
                    c.Style.BRIGHT, c.Fore.RED
                )
            )
            sys.exit(1)

        # app_args = self.profile.get('profile_args').standard
        app_args_data = self.profile.get('profile_args').data
        install_json = self.profile.get('install_json')

        # client
        client = docker.from_env()

        # app data
        app_dir = os.getcwd()
        # app_path = '{}/{}'.format(app_dir, program_main)

        # ports
        ports = {}
        if self.args.vscd:
            ports = {'{}/tcp'.format(self.args.vscd_port): self.args.vscd_port}

        # volumes
        volumes = {}
        in_path = '{}/{}'.format(app_dir, app_args_data.get('tc_in_path'))
        if app_args_data.get('tc_in_path') is not None:
            volumes[in_path] = {'bind': in_path}
        log_path = '{}/{}'.format(app_dir, app_args_data.get('tc_log_path'))
        if app_args_data.get('tc_log_path') is not None:
            volumes[log_path] = {'bind': log_path}
        out_path = '{}/{}'.format(app_dir, app_args_data.get('tc_out_path'))
        if app_args_data.get('tc_out_path') is not None:
            volumes[out_path] = {'bind': out_path}
        temp_path = '{}/{}'.format(app_dir, app_args_data.get('tc_temp_path'))
        if app_args_data.get('tc_temp_path') is not None:
            volumes[temp_path] = {'bind': temp_path}
        volumes[app_dir] = {'bind': app_dir}

        if self.args.docker_image is not None:
            # user docker image from cli as an override.
            docker_image = self.args.docker_image
        else:
            # docker image from install.json can be overridden by docker image in profile. if no
            # image is defined in either file use the default image define as self.docker_image.
            docker_image = self.profile.get(
                'dockerImage', install_json.get('dockerImage', self.docker_image)
            )

        status_code = 1
        try:
            self.container = client.containers.run(
                docker_image,
                entrypoint=commands.get('cli_command'),
                environment=['PYTHONPATH={}/lib_latest'.format(app_dir)],
                detach=True,
                # network_mode=install_json.get('docker_host', 'host'),
                ports=ports,
                remove=True,
                volumes=volumes,
                working_dir=app_dir,
            )
            results = self.container.wait()
            status_code = results.get('StatusCode')
            error = results.get('Error')
            if error:
                print('{}{}{}'.format(c.Style.BRIGHT, c.Fore.RED, error))
        except Exception as e:
            print('{}{}{}'.format(c.Style.BRIGHT, c.Fore.RED, e))
            sys.exit()

        # Exit Code
        return self.run_exit_code(status_code)

    def run_display_app_errors(self, err):
        """Handle the exit code for the current run.

        Args:
            err (str): One or more lines of errors messages.
        """
        if err is not None and err:
            for e_ in err.decode('utf-8').split('\n'):
                print('{}{}{}'.format(c.Style.BRIGHT, c.Fore.RED, e_))
                self.log.error('[tcrun] App error: {}'.format(e_))

    def run_display_app_output(self, out):
        """Print any App output.

        Args:
            out (str): One or more lines of output messages.
        """
        if not self.profile.get('quiet') and not self.args.quiet:
            print('App Output:')
            for o in out.decode('utf-8').split('\n'):
                print('  {}{}{}'.format(c.Style.BRIGHT, c.Fore.CYAN, o))
                self.log.debug('[tcrun] App output: {}'.format(o))

    def run_display_description(self):
        """Print profile name with programMain."""
        # display description if available
        if self.profile.get('description'):
            print(
                'Description: {}{}{}'.format(
                    c.Style.BRIGHT, c.Fore.MAGENTA, self.profile.get('description')
                )
            )

    def run_display_profile(self, program_main):
        """Print profile name with programMain.

        Args:
            program_main (str): The executable name.
        """
        install_json = self.profile.get('install_json')

        output = 'Profile: '
        output += '{}{}{}{} '.format(
            c.Style.BRIGHT, c.Fore.CYAN, self.profile.get('profile_name'), c.Style.RESET_ALL
        )
        output += '[{}{}{}{}'.format(
            c.Style.BRIGHT, c.Fore.MAGENTA, program_main, c.Style.RESET_ALL
        )
        if install_json.get('programVersion') is not None:
            output += '{}:{}'.format(c.Style.BRIGHT, c.Style.RESET_ALL)
            output += '{}{}{}{}'.format(
                c.Style.BRIGHT,
                c.Fore.MAGENTA,
                install_json.get('programVersion'),
                c.Style.RESET_ALL,
            )
        output += ']'
        print(output)

    def run_exit_code(self, returncode):
        """Handle the exit code for the current run.

        Args:
            returncode (int): The return exit code.

        Raises:
            RuntimeError: Raise on invalid exit code if halt_on_fail is True.

        Returns:
            bool: True if exit code is a valid exit code, else False.
        """
        exit_status = False
        self.log.info('[run] Exit Code {}'.format(returncode))

        self.reports.increment_total()  # increment report execution total
        valid_exit_codes = self.profile.get('exit_codes', [0])
        self.reports.exit_code(returncode)

        if returncode in valid_exit_codes:
            exit_status = True
            self.reports.profile_execution(True)
            print('App Exit Code: {}{}{}'.format(c.Style.BRIGHT, c.Fore.GREEN, returncode))
        else:
            print(
                'App Exit Code: {}{}{}{} (Valid Exit Codes: {})'.format(
                    c.Style.BRIGHT,
                    c.Fore.RED,
                    returncode,
                    c.Fore.RESET,
                    self.profile.get('exit_codes', [0]),
                )
            )

            self.reports.profile_execution(False)
            self.exit_code = 1
            if self.args.halt_on_fail:
                raise RuntimeError('App exited with invalid exit code {}'.format(returncode))
        return exit_status

    def run_validate_program_main(self, program_main):
        """Validate the program main file exists.

        Args:
            program_main (str): The executable name.
        """
        program_language = self.profile.get('install_json').get('programLanguage', 'python').lower()
        if program_language == 'python' and not os.path.isfile('{}.py'.format(program_main)):
            print(
                '{}{}Could not find program main file ({}).'.format(
                    c.Style.BRIGHT, c.Fore.RED, program_main
                )
            )
            sys.exit(1)

    def stage(self):
        """Stage Redis and ThreatConnect data defined in profile.

        Redis Data:

        .. code-block:: javascript

            {
                "data": [
                    "This is an example Source #1",
                    "This is an example Source #2"
                ],
                "variable": "#App:1234:source!StringArray"
            }

        Redis Array:

        .. code-block:: javascript

            {
                "data": {
                    "variables": [{
                        "value": "#App:4768:tc.adversary!TCEntity",
                    }, {
                        "value": "#App:4768:tc.threat!TCEntity",
                    }]
                },
                "data_type": "redis_array",
                "variable": "#App:4768:groups!TCEntityArray"
            },
            {
                "data": {
                    "variables": [{
                        "value": "#App:4768:tc.adversary!TCEntity",
                        "path": ".name"
                    }, {
                        "value": "#App:4768:tc.threat!TCEntity",
                        "path": ".name"
                    }]
                },
                "data_type": "redis_array",
                "variable": "#App:4768:groups!StringArray"
            }

        ThreatConnect Data:

        .. code-block:: javascript

            {
                "data": {
                    "group": [{
                        "firstSeen": "2008-12-12T12:00:00Z",
                        "name": "campaign-002",
                        "type": "Campaign",
                        "xid": "camp-0002",
                        "attribute": [{
                            "displayed": True,
                            "type": "Description",
                            "value": "Campaign Example Description"
                        }],
                        "tag": [{
                            "name": "SafeToDelete"
                        }],
                        "variable": "#App:4768:tc.campaign!TCEntity"
                    }],
                    "indicator": [{
                        "associatedGroups": [
                            {
                                "groupXid": "campaign-002"
                            }
                        ],
                        "confidence": 100,
                        "fileOccurrence": [
                            {
                                "date": "2017-02-02T01:02:03Z",
                                "fileName": "drop1.exe",
                                "path": "C:\\\\test\\\\"
                            }
                        ],
                        "rating": 5.0,
                        "summary": "43c3609411c83f363e051d455ade78a6",
                        "tag": [
                            {
                                "name": "SafeToDelete"
                            }
                        ],
                        "type": "File",
                        "xid": "55ee19565db5b16a0f511791a3b2a7ef0ccddf4d9d64e7008561329419cb675b",
                        "variable": "#App:4768:tc.file!TCEntity"
                    }]
                },
                "data_owner": "TCI",
                "data_type": "threatconnect"
            }
        """
        for sd in self.staging_data:
            if not isinstance(sd, dict):
                # reported issue from qa where staging data is invalid
                msg = 'Invalid staging data provided ({}).'.format(sd)
                sys.exit(msg)
            data_type = sd.get('data_type', 'redis')
            if data_type == 'redis':
                self.log.debug('Stage Redis Data')
                self.stage_redis(sd.get('variable'), sd.get('data'))
            elif data_type in ['redis-array', 'redis_array']:
                self.log.debug('Stage Redis Array')
                out_variable = sd.get('variable')
                # build array
                redis_array = []
                for var in sd.get('data', {}).get('variables') or []:
                    variable = var.get('value')
                    if variable.endswith('Binary'):
                        data = self.tcex.playbook.read_binary(variable, False, False)
                    elif variable.endswith('BinaryArray'):
                        data = self.tcex.playbook.read_binary_array(variable, False, False)
                    else:
                        data = self.path_data(self.tcex.playbook.read(variable), var.get('path'))
                    # TODO: should None value be appended?
                    redis_array.append(data)
                self.stage_redis(out_variable, redis_array)
                # print(redis_array)
            elif data_type == 'threatconnect':
                self.log.debug('Stage ThreatConnect Data')
                self.stage_tc(sd.get('data_owner'), sd.get('data', {}), sd.get('variable'))
            elif data_type == 'threatconnect-association':
                self.log.debug('Stage ThreatConnect Association Data')
                data = sd.get('data')
                self.stage_tc_associations(data.get('entity1'), data.get('entity2'))
            elif data_type == 'threatconnect-batch':
                self.log.debug('Stage ThreatConnect Batch Data')
                self.stage_tc_batch(sd.get('data_owner'), sd.get('data', {}))

    @property
    def staging_data(self):
        """Read data files and return all staging data for current profile."""
        if self._staging_data is None:
            staging_data = []
            for staging_file in self.profile.get('data_files') or []:
                if os.path.isfile(staging_file):
                    print(
                        'Staging Data: {}{}{}'.format(c.Style.BRIGHT, c.Fore.MAGENTA, staging_file)
                    )
                    self.log.info('[stage] Staging data file: {}'.format(staging_file))
                    f = open(staging_file, 'r')
                    staging_data.extend(json.load(f))
                    f.close()
                else:
                    print(
                        '{}{}Could not find file {}.'.format(
                            c.Style.BRIGHT, c.Fore.RED, staging_file
                        )
                    )
            self._staging_data = staging_data
        return self._staging_data

    def stage_redis(self, variable, data):
        """Stage data in Redis.

        Args:
            variable (str): The Redis variable name.
            data (dict|list|str): The data to store in Redis.
        """
        if isinstance(data, int):
            data = str(data)
        # handle binary
        if variable.endswith('Binary'):
            try:
                data = base64.b64decode(data)
            except binascii.Error:
                msg = 'The Binary staging data for variable {} is not properly base64 encoded.'
                msg = msg.format(variable)
                sys.exit(msg)
        elif variable.endswith('BinaryArray'):
            if isinstance(data, string_types):
                data = json.loads(data)

            try:
                # loop through each entry
                decoded_data = []
                for d in data:
                    d_decoded = base64.b64decode(d)
                    decoded_data.append(d_decoded)
                data = decoded_data
            except binascii.Error:
                msg = 'The BinaryArray staging data for variable {} is not properly base64 encoded.'
                msg = msg.format(variable)
                sys.exit(msg)
        self.log.info(u'[stage] Creating variable {}'.format(variable))
        self.tcex.playbook.create(variable, data)

    def stage_tc(self, owner, staging_data, variable):
        """Stage data using ThreatConnect API.

        .. code-block:: javascript

            [{
              "data": {
                "id": 116,
                "value": "adversary001-build-testing",
                "type": "Adversary",
                "ownerName": "qa-build",
                "dateAdded": "2017-08-16T18:35:07-04:00",
                "webLink": "https://app.tci.ninja/auth/adversary/adversary.xhtml?adversary=116"
              },
              "data_type": "redis",
              "variable": "#App:0822:adversary!TCEntity"
            }]

        Args:
            owner (str): The ThreatConnect owner name.
            staging_data (dict): A dict containing the ThreatConnect threat intel.
            variable (str): A variable name to write to Redis.
        """
        # parse resource_data
        resource_type = staging_data.pop('type')

        if resource_type in self.tcex.indicator_types or resource_type in self.tcex.group_types:
            try:
                attributes = staging_data.pop('attribute')
            except KeyError:
                attributes = []
            try:
                security_labels = staging_data.pop('security_label')
            except KeyError:
                security_labels = []
            try:
                tags = staging_data.pop('tag')
            except KeyError:
                tags = []

            resource = self.tcex.resource(resource_type)
            resource.http_method = 'POST'
            resource.owner = owner

            # special case for Email Group Type
            if resource_type == 'Email':
                resource.add_payload('option', 'createVictims')

            self.log.debug('body: {}'.format(staging_data))
            resource.body = json.dumps(staging_data)

            response = resource.request()
            if response.get('status') == 'Success':
                # add resource id
                if resource_type in self.tcex.indicator_types:
                    resource_id = resource.summary(response.get('data'))
                    self.log.info(
                        '[stage] Creating resource {}:{}'.format(resource_type, resource_id)
                    )
                elif resource_type in self.tcex.group_types:
                    self.log.info(
                        '[stage] Creating resource {}:{}'.format(
                            resource_type, response.get('data', {}).get('name')
                        )
                    )
                    resource_id = response.get('data', {}).get('id')
                self.log.debug('[stage] resource_id: {}'.format(resource_id))
                resource.resource_id(resource_id)

                entity = self.tcex.playbook.json_to_entity(
                    response.get('data'), resource.value_fields, resource.name, resource.parent
                )
                self.log.debug('[stage] Creating Entity: {} ({})'.format(variable, entity[0]))

                self.stage_redis(variable, entity[0])
                # self.tcex.playbook.create_tc_entity(variable, entity[0])

                # update metadata
                for attribute_data in attributes:
                    self.stage_tc_create_attribute(
                        attribute_data.get('type'), attribute_data.get('value'), resource
                    )
                for label_data in security_labels:
                    self.stage_tc_create_security_label(label_data.get('name'), resource)
                for tag_data in tags:
                    self.stage_tc_create_tag(tag_data.get('name'), resource)
        else:
            self.log.error('[stage] Unsupported resource type {}.'.format(resource_type))

    def stage_tc_create_attribute(self, attribute_type, attribute_value, resource):
        """Add an attribute to a resource.

        Args:
            attribute_type (str): The attribute type (e.g., Description).
            attribute_value (str): The attribute value.
            resource (obj): An instance of tcex resource class.
        """
        attribute_data = {'type': str(attribute_type), 'value': str(attribute_value)}
        # handle default description and source
        if attribute_type in ['Description', 'Source']:
            attribute_data['displayed'] = True

        attrib_resource = resource.attributes()
        attrib_resource.body = json.dumps(attribute_data)
        attrib_resource.http_method = 'POST'

        # add the attribute
        a_response = attrib_resource.request()
        if a_response.get('status') != 'Success':
            self.log.warning(
                '[stage] Failed adding attribute type "{}":"{}" ({}).'.format(
                    attribute_type, attribute_value, a_response.get('response').text
                )
            )

    def stage_tc_create_security_label(self, label, resource):
        """Add a security label to a resource.

        Args:
            label (str): The security label (must exit in ThreatConnect).
            resource (obj): An instance of tcex resource class.
        """
        sl_resource = resource.security_labels(label)
        sl_resource.http_method = 'POST'
        sl_response = sl_resource.request()
        if sl_response.get('status') != 'Success':
            self.log.warning(
                '[tcex] Failed adding security label "{}" ({}).'.format(
                    label, sl_response.get('response').text
                )
            )

    def stage_tc_create_tag(self, tag, resource):
        """Add a tag to a resource.

        Args:
            tag (str): The tag to be added to the resource.
            resource (obj): An instance of tcex resource class.
        """
        tag_resource = resource.tags(self.tcex.safetag(tag))
        tag_resource.http_method = 'POST'
        t_response = tag_resource.request()
        if t_response.get('status') != 'Success':
            self.log.warning(
                '[tcex] Failed adding tag "{}" ({}).'.format(tag, t_response.get('response').text)
            )

    def stage_tc_associations(self, entity1, entity2):
        """Add an attribute to a resource.

        Args:
            entity1 (str): A Redis variable containing a TCEntity.
            entity2 (str): A Redis variable containing a TCEntity.
        """
        # resource 1
        entity1 = self.tcex.playbook.read(entity1)
        entity1_id = entity1.get('id')
        entity1_owner = entity1.get('ownerName')
        entity1_type = entity1.get('type')
        if entity1.get('type') in self.tcex.indicator_types:
            entity1_id = entity1.get('value')

        # resource 2
        entity2 = self.tcex.playbook.read(entity2)
        entity2_id = entity2.get('id')
        entity2_owner = entity1.get('ownerName')
        entity2_type = entity2.get('type')
        if entity2.get('type') in self.tcex.indicator_types:
            entity2_id = entity2.get('value')

        if entity1_owner != entity2_owner:
            self.log.error('[stage] Can not associate resource across owners.')
            return

        resource1 = self.tcex.resource(entity1_type)
        resource1.http_method = 'POST'
        resource1.owner = entity1_owner
        resource1.resource_id(entity1_id)

        resource2 = self.tcex.resource(entity2_type)
        resource2.resource_id(entity2_id)

        a_resource = resource1.associations(resource2)
        response = a_resource.request()
        if response.get('status') != 'Success':
            self.log.warning(
                '[stage] Failed associating "{}:{}" with "{}:{}" ({}).'.format(
                    entity1_type,
                    entity1_id,
                    entity2_type,
                    entity2_id,
                    response.get('response').text,
                )
            )

    def stage_tc_batch(self, owner, staging_data):
        """Stage data in ThreatConnect Platform using batch API.

        Args:
            owner (str): The ThreatConnect owner to submit batch job.
            staging_data (dict): A dict of ThreatConnect batch data.
        """
        batch = self.tcex.batch(owner)
        for group in staging_data.get('group') or []:
            # add to redis
            variable = group.pop('variable', None)
            path = group.pop('path', None)
            data = self.path_data(group, path)
            # update group data
            if group.get('xid') is None:
                # add xid if one doesn't exist
                group['xid'] = self.stage_tc_batch_xid(group.get('type'), group.get('name'), owner)
            # add owner name
            group['ownerName'] = owner
            # add to batch
            batch.add_group(group)
            # create tcentity
            if variable is not None and data is not None:
                self.stage_redis(variable, self.stage_tc_group_entity(data))
        for indicator in staging_data.get('indicator') or []:
            # add to redis
            variable = indicator.pop('variable', None)
            path = indicator.pop('path', None)
            if indicator.get('xid') is None:
                indicator['xid'] = self.stage_tc_batch_xid(
                    indicator.get('type'), indicator.get('summary'), owner
                )
            indicator['ownerName'] = owner
            # add to batch after extra data has been popped
            batch.add_indicator(indicator)
            data = self.path_data(dict(indicator), path)
            if variable is not None and data is not None:
                # if isinstance(data, (dict)):
                # tcentity uses value as the name
                #     data['value'] = data.pop('summary')
                self.stage_redis(variable, self.stage_tc_indicator_entity(data))
        # submit batch
        batch_results = batch.submit()
        self.log.debug('[stage] Batch Results: {}'.format(batch_results))
        for error in batch_results.get('errors') or []:
            self.log.error('[stage] {}'.format(error))

    @staticmethod
    def stage_tc_batch_xid(xid_type, xid_value, owner):
        """Create an xid for a batch job.

        Args:
            xid_type (str): [description]
            xid_value (str): [description]
            owner (str): [description]

        Returns:
            [type]: [description]
        """
        xid_string = '{}-{}-{}'.format(xid_type, xid_value, owner)
        hash_object = hashlib.sha256(xid_string.encode('utf-8'))
        return hash_object.hexdigest()

    def stage_tc_group_entity(self, group_data):
        """Convert JSON data to TCEntity.

        Args:
            group_data (str): [description]

        Returns:
            [type]: [description]
        """
        path = '@.{name: name, type: type, ownerName: ownerName}'
        return self.path_data(group_data, path)

    def stage_tc_indicator_entity(self, indicator_data):
        """Convert JSON data to TCEntity.

        Args:
            indicator_data (str): [description]

        Returns:
            [type]: [description]
        """
        path = '@.{value: summary, '
        path += 'type: type, '
        path += 'ownerName: ownerName, '
        path += 'confidence: confidence || `0`, '
        path += 'rating: rating || `0`}'
        return self.path_data(indicator_data, path)

    @staticmethod
    def update_environment():
        """Run the App as a subprocess."""
        lib_path = os.path.join(os.getcwd(), 'lib_latest')
        if 'PYTHONPATH' in os.environ:
            os.environ['PYTHONPATH'] = '{}{}{}'.format(
                lib_path, os.pathsep, os.environ['PYTHONPATH']
            )
        else:
            os.environ['PYTHONPATH'] = '{}'.format(lib_path)

    def validate(self):
        """Validate data in Redis."""
        passed = True
        for data in self.profile.get('validations') or []:
            data_type = data.get('data_type', 'redis')  # default to redis for older data files
            if data_type == 'redis':
                user_data = data.get('data')
                user_data_path = data.get('data_path')  # jmespath expression
                if isinstance(user_data, string_types) and re.match(self._vars_match, user_data):
                    # if user_data reference a redis variable retrieve the data
                    if user_data.endswith('Binary'):
                        # call specific method and do not decode data
                        user_data = self.tcex.playbook.read_binary(user_data, False, False)
                    elif user_data.endswith('BinaryArray'):
                        # call specific method and do not decode data
                        user_data = self.tcex.playbook.read_binary_array(user_data, False, False)
                    else:
                        user_data = self.tcex.playbook.read(user_data)

                if user_data_path is not None:
                    user_data = self.path_data(user_data, user_data_path)

                # get db variable/data
                variable = data.get('variable')
                if variable.endswith('Binary'):
                    # call specific method and do not decode data
                    db_data = self.tcex.playbook.read_binary(variable, False, False)
                elif variable.endswith('BinaryArray'):
                    # call specific method and do not decode data
                    db_data = self.tcex.playbook.read_binary_array(variable, False, False)
                else:
                    db_data = self.tcex.playbook.read(variable)
                db_data_path = data.get('variable_path')
                if db_data_path is not None:
                    db_data = self.path_data(db_data, db_data_path)

                # operator
                oper = data.get('operator', 'eq')

                # validate if possible
                sep = '-' * 10
                self.log.info('{0} {1} {0}'.format(sep, variable))
                # self.log.info('[validate] Variable  : {}'.format(variable))
                if not self.validate_redis(db_data, user_data, oper):
                    passed = False
                    self.exit_code = 1  # if any validation fails everything fails
        return passed

    def validate_redis(self, db_data, user_data, oper):
        """Validate data in Redis.

        Args:
            db_data (str): The data store in Redis.
            user_data (str): The user provided data.
            oper (str): The comparison operator.

        Returns:
            bool: True if the data passed validation.
        """
        passed = True
        # convert any int to string since playbooks don't support int values
        if isinstance(db_data, int):
            db_data = str(db_data)
        if isinstance(user_data, int):
            user_data = str(user_data)

        # try to sort list of strings for simple comparisons
        # if list has a more complex data structure the sort will fail
        if isinstance(db_data, (list)):
            try:
                db_data = sorted(db_data)
            except TypeError:
                # self.log.debug('[validate] could not sort list')
                pass
        if isinstance(user_data, (list)):
            try:
                user_data = sorted(user_data)
            except TypeError:
                # self.log.debug('[validate] could not sort list')
                pass

        if oper not in self.operators:
            self.log.error('Invalid operator provided ({})'.format(oper))
            return False

        # compare the data
        if self.operators.get(oper)(db_data, user_data):
            self.reports.profile_validation(True)
        else:
            self.reports.profile_validation(False)
            passed = False

        # log validation data in a readable format
        self.validate_log_output(passed, db_data, user_data, oper)

        return passed

    def validate_log_output(self, passed, db_data, user_data, oper):
        """Format the validation log output to be easier to read.

        Args:
            passed (bool): The results of the validation test.
            db_data (str): The data store in Redis.
            user_data (str): The user provided data.
            oper (str): The comparison operator.

        Raises:
            RuntimeError: Raise error on validation failure if halt_on_fail is True.
        """
        truncate = self.args.truncate
        if db_data is not None and passed:
            if isinstance(db_data, (string_types)) and len(db_data) > truncate:
                db_data = db_data[:truncate]
            elif isinstance(db_data, (list)):
                db_data_truncated = []
                for d in db_data:
                    if d is not None and isinstance(d, string_types) and len(d) > truncate:
                        db_data_truncated.append('{} ...'.format(d[: self.args.truncate]))
                    else:
                        db_data_truncated.append(d)
                db_data = db_data_truncated

        if user_data is not None and passed:
            if isinstance(user_data, (string_types)) and len(user_data) > truncate:
                user_data = user_data[: self.args.truncate]
            elif isinstance(user_data, (list)):
                user_data_truncated = []
                for u in user_data:
                    if isinstance(db_data, (string_types)) and len(u) > truncate:
                        user_data_truncated.append('{} ...'.format(u[: self.args.truncate]))
                    else:
                        user_data_truncated.append(u)
                user_data = user_data_truncated

        self.log.info('[validate] DB Data   : ({}), Type: [{}]'.format(db_data, type(db_data)))
        self.log.info('[validate] Operator  : ({})'.format(oper))
        self.log.info('[validate] User Data : ({}), Type: [{}]'.format(user_data, type(user_data)))

        if passed:
            self.log.info('[validate] Results   : Passed')
        else:
            self.log.error('[validate] Results  : Failed')
            if db_data is not None and user_data is not None and oper in ['eq', 'ne']:
                try:
                    diff_count = 0
                    for i, diff in enumerate(difflib.ndiff(db_data, user_data)):
                        if diff[0] == ' ':  # no difference
                            continue
                        elif diff[0] == '-':
                            self.log.info(
                                '[validate] Diff      : Missing data at index {}'.format(i)
                            )
                        elif diff[0] == '+':
                            self.log.info('[validate] Diff      : Extra data at index {}'.format(i))
                        if diff_count > self.max_diff:
                            # don't spam the logs if string are vastly different
                            self.log.info('Max number of differences reached.')
                            break
                        diff_count += 1
                except TypeError:
                    pass
                except KeyError:
                    pass

            # halt all further actions
            if self.args.halt_on_fail:
                raise RuntimeError('Failed validating data.')


class ArgBuilder(object):
    """Object container for CLI Args."""

    def __init__(self, lang, _args):
        """Initialize Class properties."""
        self.lang = lang.lower()
        self._data = {}
        self._args = []
        self._args_masked = []
        self._args_quoted = []
        # Build arg data
        self.load(_args)

    @property
    def data(self):
        """Return all data formatted for the provided language."""
        return self._data

    @property
    def masked(self):
        """Return all args formatted for the provided language with sensitive data masked."""
        return self._args_masked

    @property
    def quoted(self):
        """Return all args formatted for the provided language with appropriate args quoted."""
        return self._args_quoted

    @property
    def standard(self):
        """Return all args formatted for the provided language."""
        return self._args

    def _add_arg_python(self, key, value=None, mask=False):
        """Add CLI Arg formatted specifically for Python.

        Args:
            key (string): The CLI Args key (e.g., --name).
            value (string): The CLI Args value (e.g., bob).
            mask (boolean, default:False): Indicates whether no mask value.
        """
        self._data[key] = value
        if not value:
            # both false boolean values (flags) and empty values should not be added.
            pass
        elif value is True:
            # true boolean values are flags and should not contain a value
            self._args.append('--{}'.format(key))
            self._args_quoted.append('--{}'.format(key))
            self._args_masked.append('--{}'.format(key))
        else:
            self._args.append('--{}={}'.format(key, value))
            if mask:
                # mask sensitive values
                value = 'x' * len(str(value))
            else:
                # quote all values that would get displayed
                value = self.quote(value)
            self._args_quoted.append('--{}={}'.format(key, value))
            self._args_masked.append('--{}={}'.format(key, value))

    def _add_arg_java(self, key, value, mask=False):
        """Add CLI Arg formatted specifically for Java.

        Args:
            key (string): The CLI Args key (e.g., --name).
            value (string): The CLI Args value (e.g., bob).
            mask (boolean, default:False): Indicates whether no mask value.
        """
        if isinstance(value, bool):
            value = int(value)
        self._data[key] = value
        self._args.append('{}{}={}'.format('-D', key, value))
        self._args_quoted.append(self.quote('{}{}={}'.format('-D', key, value)))
        if mask:
            value = 'x' * len(str(value))
        self._args_masked.append('{}{}={}'.format('-D', key, value))

    def _add_arg(self, key, value, mask=False):
        """Add CLI Arg for the correct language.

        Args:
            key (string): The CLI Args key (e.g., --name).
            value (string): The CLI Args value (e.g., bob).
            mask (boolean, default:False): Indicates whether no mask value.
        """
        if self.lang == 'python':
            self._add_arg_python(key, value, mask)
        elif self.lang == 'java':
            self._add_arg_java(key, value, mask)

    def add(self, key, value):
        """Add CLI Arg to lists value.

        Args:
            key (string): The CLI Args key (e.g., --name).
            value (string): The CLI Args value (e.g., bob).
        """
        if isinstance(value, list):
            # TODO: support env vars in list w/masked values
            for val in value:
                self._add_arg_python(key, val)
        elif isinstance(value, dict):
            err = 'Dictionary types are not currently supported for field.'
            print('{}{}{}'.format(c.Style.BRIGHT, c.Fore.RED, err))
        else:
            mask = False
            env_var = re.compile(r'^\$env\.(.*)$')
            envs_var = re.compile(r'^\$envs\.(.*)$')

            if env_var.match(str(value)):
                # read value from environment variable
                env_key = env_var.match(str(value)).groups()[0]
                value = os.environ.get(env_key, value)
            elif envs_var.match(str(value)):
                # read secure value from environment variable
                env_key = envs_var.match(str(value)).groups()[0]
                value = os.environ.get(env_key, value)
                mask = True
            self._add_arg(key, value, mask)

    def quote(self, data):
        """Quote any parameters that contain spaces or special character.

        Returns:
            (string): String containing parameters wrapped in double quotes

        """
        if self.lang == 'python':
            quote_char = "'"
        elif self.lang == 'java':
            quote_char = "'"

        if re.findall(r'[!\-\=\s\$\&]{1,}', str(data)):
            data = '{0}{1}{0}'.format(quote_char, data)
        return data

    def load(self, profile_args):
        """Load provided CLI Args.

        Args:
            args (dict): Dictionary of args in key/value format.
        """
        for key, value in profile_args.items():
            self.add(key, value)


class Report(object):
    """Report Object for a single profile."""

    def __init__(self, profile):
        """Initialize class properties."""
        self._data = {
            'description': profile.get('description'),
            'groups': profile.get('groups'),
            'name': profile.get('profile_name'),
            'selected': False,
            'valid_exit_codes': profile.get('exit_codes'),
        }

    @property
    def data(self):
        """Return the report data."""
        return self._data

    @property
    def execution_success(self):
        """Return the profile/report execution_success."""
        return self._data.get('execution_success')

    @execution_success.setter
    def execution_success(self, execution_success):
        """Set the profile/report execution_success."""
        self._data['execution_success'] = execution_success

    @property
    def exit_code(self):
        """Return the profile/report exit_code."""
        return self._data.get('exit_code')

    @exit_code.setter
    def exit_code(self, exit_code):
        """Set the profile/report exit_code."""
        self._data['exit_code'] = exit_code

    @property
    def name(self):
        """Return the profile/report name."""
        return self._data.get('name')

    @property
    def selected(self):
        """Return the profile/report name."""
        return self._data.get('selected')

    @selected.setter
    def selected(self, selected):
        """Return the profile/report name."""
        self._data['selected'] = selected

    def __str__(self):
        """Return report as a string."""
        return json.dumps(self._data, indent=2, sort_keys=True)


class Reports(object):
    """Object to hold the run report."""

    def __init__(self):
        """Initialize class properties."""
        python_version = '{}.{}.{}'.format(
            sys.version_info.major, sys.version_info.minor, sys.version_info.micro
        )
        self.report = {
            'profiles': {'selected': [], 'unselected': []},
            'results': {
                'executions': {'fail': 0, 'pass': 0},
                'failed_profiles': [],
                'total': 0,
                'validations': {'fail': 0, 'pass': 0},
            },
            'settings': {
                'date': datetime.now().isoformat(),
                'provided_group': 'qa-build',
                'provided_profile': 'default',
                'python_version': python_version,
                'selected_profiles': [],
                'selected_profile_count': 0,
                'tcex_version': __import__('tcex').__version__,
                'total_profile_count': 0,
            },
        }
        self.profiles = {}
        self.selected_profile = None

    def add_profile(self, profile, selected):
        """Add profile to report."""
        report = Report(profile)
        report.selected = selected
        if selected:
            self.report['settings']['selected_profiles'].append(report.name)
            self.report['settings']['selected_profile_count'] += 1
        self.report['settings']['total_profile_count'] += 1
        self.profiles.setdefault(report.name, report)
        return report

    def exit_code(self, code):
        """Set the exit code on the selected profile."""
        self.selected_profile.data['exit_code'] = code

    def increment_total(self):
        """Return run total value."""
        self.report['results']['total'] += 1

    def profile(self, name):
        """Return a specific profile."""
        self.selected_profile = self.profiles.get(name)
        return self.profiles.get(name)

    def profile_execution(self, status):
        """Return run total value."""
        self.selected_profile.data['execution_success'] = status
        if status:
            self.report['results']['executions']['pass'] += 1
        else:
            self.report['results']['executions']['fail'] += 1
            if self.selected_profile.name not in self.report['results']['failed_profiles']:
                self.report['results']['failed_profiles'].append(self.selected_profile.name)

    def profile_validation(self, status):
        """Return run total value."""
        self.selected_profile.data.setdefault('validation_pass_count', 0)
        self.selected_profile.data.setdefault('validation_fail_count', 0)
        if status:
            self.selected_profile.data['validation_pass_count'] += 1
        else:
            self.selected_profile.data['validation_fail_count'] += 1

    def report_validation(self, status):
        """Return run total value."""
        # only one fail/pass count per profile
        if status:
            self.report['results']['validations']['pass'] += 1
        else:
            self.report['results']['validations']['fail'] += 1
            if self.selected_profile.name not in self.report['results']['failed_profiles']:
                self.report['results']['failed_profiles'].append(self.selected_profile.name)

    def __iter__(self):
        """Interate over all report profiles."""
        for profile in self.profiles.values():
            yield profile

    def __str__(self):
        """Return reports as a string."""
        report = self.report
        for profile in self.profiles.values():
            if profile.data.get('selected'):
                selected = 'selected'
            else:
                selected = 'unselected'
            del profile.data['selected']
            report['profiles'][selected].append(profile.data)
        return json.dumps(report, indent=2, sort_keys=True)
