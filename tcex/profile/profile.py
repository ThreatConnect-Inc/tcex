# -*- coding: utf-8 -*-
"""TcEx testing profile Class."""
# standard library
import json
import logging
import os
import re
import sys
from collections import OrderedDict
from random import randint

# third-party
import colorama as c

from ..app_config_object import InstallJson, LayoutJson, Permutations
from ..env_store import EnvStore
from ..sessions import TcSession
from ..utils import Utils
from .migrate import Migrate
from .populate import Populate
from .rules import Rules
from .session_manager import SessionManager

# autoreset colorama
c.init(autoreset=True, strip=False)


class Profile:
    """Testing Profile Class.

    Args:
        default_args (dict, optional): The default Args for the profile.
        feature (str, optional): The feature name.
        name (str, optional): The filename of the profile in the profile.d director.
        redis_client (redis.client.Redis, optional): An instance of Redis client.
        pytestconfig (?, optional): Pytest config object.
        monkeypatch (?, optional): Pytest monkeypatch object.
        tcex_testing_context (str, optional): The current context for this profile.
        logger (logging.Logger, optional): An logging instance.
        options (dict, optional): ?
    """

    def __init__(
        self,
        default_args=None,
        feature=None,
        name=None,
        redis_client=None,
        pytestconfig=None,
        monkeypatch=None,
        tcex_testing_context=None,
        logger=None,
        options=None,
    ):
        """Initialize Class properties."""
        self._default_args = default_args or {}
        self._feature = feature
        self._name = name
        self.log = logger or logging.getLogger('profile')
        self.redis_client = redis_client
        self.pytestconfig = pytestconfig
        self.monkeypatch = monkeypatch
        self.tcex_testing_context = tcex_testing_context
        self.test_options = options

        # properties
        self._app_path = os.getcwd()
        self._context_tracker = []
        self._data = None
        self._output_variables = None
        self._pytest_args = None
        self._session_manager = None
        self._session = None
        self.env_store = EnvStore(logger=self.log)
        self.ij = InstallJson(logger=self.log)
        self.lj = LayoutJson(logger=self.log)
        self.permutations = Permutations(logger=self.log)
        self.populate = Populate(self)
        self.rules = Rules(self)
        self.tc_staged_data = {}
        self.utils = Utils()

    @staticmethod
    def _flatten_inputs(inputs):
        """Flatten the inputs dict."""
        inputs_flattened = dict(inputs.get('defaults', {}))
        inputs_flattened.update(inputs.get('optional', {}))
        inputs_flattened.update(inputs.get('required', {}))
        return inputs_flattened

    @staticmethod
    def _sorted(data):
        """Return a sorted dict as an OrderedDict."""
        return json.loads(json.dumps(data, sort_keys=True), object_pairs_hook=OrderedDict)

    @property
    def _test_case_data(self):
        """Return partially parsed test case data."""
        return os.getenv('PYTEST_CURRENT_TEST').split(' ')[0].split('::')

    @property
    def _test_case_name(self):
        """Return partially parsed test case data."""
        return self._test_case_data[-1].replace('/', '-').replace('[', '-').replace(']', '')

    def add(self, profile_data=None, profile_name=None, permutation_id=None):
        """Add a profile.

        Args:
            profile_data (dict, optional): The profile data.
            profile_name (str, optional): The name of the profile.
            permutation_id (int, optional): The index of the permutation id. Defaults to None.
        """
        profile_data = profile_data or {}
        if profile_name is not None:
            # profile_name is only used for profile migrations
            self.name = profile_name

        # get input permutations when a permutation_id is passed
        input_permutations = None
        if permutation_id is not None:
            try:
                input_permutations = self.permutations.input_dict(permutation_id)
            except Exception:
                # catch any error
                print(f'{c.Fore.RED}Invalid permutation id provided.')
                sys.exit(1)

        # this should not hit since tctest also check for duplicates
        if os.path.isfile(self.filename):  # pragma: no cover
            print(f'{c.Fore.RED}A profile with the name already exists.')
            sys.exit(1)

        profile = OrderedDict()
        profile['_comments_'] = []
        profile['environments'] = ['build']
        profile['stage'] = profile_data.get('stage', {'kvstore': {}})
        profile['configs'] = []  # add config here and remove later to ensure proper order
        profile['inputs'] = {}  # add inputs here and remove later to ensure proper order
        profile['trigger'] = {}
        profile['webhook_event'] = {
            'body': '',
            'headers': [],
            'method': 'GET',
            'query_params': [],
            'trigger_id': '',
        }
        profile['validation_criteria'] = {}
        profile['outputs'] = profile_data.get('outputs')
        profile['options'] = profile_data.get(
            'options', {'session': {'enabled': False, 'blur': []}},
        )

        if self.ij.runtime_level.lower() in ['triggerservice', 'webhooktriggerservice']:
            profile['configs'].extend(
                [
                    {
                        'trigger_id': str(randint(1000, 9999)),  # nosec
                        'config': profile_data.get(
                            'inputs',
                            {
                                'optional': self.ij.params_to_args(
                                    input_permutations=input_permutations,
                                    required=False,
                                    service_config=False,
                                ),
                                'required': self.ij.params_to_args(
                                    input_permutations=input_permutations,
                                    required=True,
                                    service_config=False,
                                ),
                            },
                        ),
                    }
                ]
            )
            del profile['inputs']  # inputs are for non service Apps
            del profile['validation_criteria']  # validation_criteria is for job Apps only
        elif self.ij.runtime_level.lower() in ['organization', 'playbook']:
            profile['exit_codes'] = profile_data.get('exit_codes', [0])
            profile['exit_message'] = None
            profile['inputs'].update(
                profile_data.get(
                    'inputs',
                    {
                        'optional': self.ij.params_to_args(
                            required=False, input_permutations=input_permutations
                        ),
                        'required': self.ij.params_to_args(
                            required=True, input_permutations=input_permutations
                        ),
                    },
                )
            )
            del profile['configs']  # inputs are for non service Apps
            del profile['trigger']  # trigger is for service Apps only
            del profile['webhook_event']  # webhook_event is for service Apps only

        if self.ij.runtime_level.lower() == 'organization':
            profile['stage']['threatconnect'] = {}
            profile['validation_criteria'] = profile_data.get('validation_criteria', {'percent': 5})

            del profile['outputs']  # outputs are not used in job Apps
        elif self.ij.runtime_level.lower() == 'playbook':
            del profile['validation_criteria']  # validation_criteria is for job Apps only
        elif self.ij.runtime_level.lower() == 'triggerservice':
            del profile['webhook_event']  # webhook_event is for webhooktriggerservice Apps only
        elif self.ij.runtime_level.lower() == 'webhooktriggerservice':
            del profile['trigger']  # trigger is for triggerservice Apps only

        # write the new profile to disk
        self.write(profile)

    def add_context(self, context):
        """Add a context to the context tracker for this profile.

        Args:
            context (str): The context (session_id) for this profile.
        """
        self._context_tracker.append(context)

    def clear_context(self, context):
        """Clear all context data in redis.

        Args:
            context (str): The context (session_id) to clear in KV store.
        """
        keys = self.redis_client.hkeys(context)
        if keys:
            return self.redis_client.hdel(context, *keys)
        return 0

    @property
    def contents(self):
        """Return mutable copy of profile JSON contents."""
        try:
            with open(self.filename, 'r') as fh:
                return json.load(fh, object_pairs_hook=OrderedDict)
        except (OSError, ValueError):
            print(f'{c.Fore.RED}Could not open/read profile {self.filename}.')

    @property
    def context_tracker(self):
        """Return the current context trackers for Service Apps."""
        if not self._context_tracker:
            if self.tcex_testing_context:
                self._context_tracker = json.loads(
                    self.redis_client.hget(self.tcex_testing_context, '_context_tracker') or '[]'
                )
        return self._context_tracker

    @property
    def data(self):
        """Return single instance copy of current profile."""
        if self._data is None:
            self._data = self.contents
            self.remove_comments(self._data)

        # APP-618 - used in custom test cases
        if self._data:
            self._data['name'] = self.name

        return self._data

    @data.setter
    def data(self, profile_data):
        """Set profile_data dict."""
        self._data = profile_data
        self.remove_comments(self._data)

    def delete(self):
        """Delete an existing profile."""
        raise NotImplementedError('The delete method is not currently implemented.')

    @property
    def directory(self):
        """Return fully qualified profile directory."""
        return os.path.join(self._app_path, 'tests', self.feature, 'profiles.d')

    @property
    def feature(self):
        """Return the current feature."""
        if self._feature is None:
            # when called in testing framework will get the feature from pytest env var.
            self._feature = self._test_case_data[0].split('/')[1].replace('/', '-')
        return self._feature

    @property
    def feature_directory(self):
        """Return fully qualified feature directory."""
        return os.path.join(self._app_path, 'tests', self.feature)

    @property
    def filename(self):
        """Return profile fully qualified filename."""
        return os.path.join(self.directory, f'{self.name}.json')
        # return os.path.join(self.directory, f'{self.name}.json')

    def init(self):
        """Return the Data (dict) from the current profile."""
        if self.data is None:
            self.log.error('Profile init failed; loaded profile data is None')

        # Now can initialize anything that needs initializing
        self.session_manager.init()  # initialize session recording/playback

    def merge_inputs(self):
        """Merge new inputs and remove undefined inputs."""
        if not self.pytest_args.get('merge_inputs'):
            return

        updated_params = []

        # handle non-layout and layout based App appropriately
        for profile_inputs, params in self.profile_inputs_params:
            profile_inputs_flattened = self._flatten_inputs(profile_inputs)

            inputs = {}
            merged_inputs = {
                'optional': {},
                'required': {},
            }
            for name, data in params.items():
                # inputs that are serviceConfig are not applicable for profiles
                if data.get('serviceConfig'):
                    continue

                # each non hidden input will be checked for permutations if the App has layout
                if not data.get('hidden'):
                    if not self.permutations.validate_input_variable(name, inputs):
                        continue

                # get the value from the current profile or use default value from install.json
                value = profile_inputs_flattened.get(name)
                if name not in profile_inputs_flattened and data.get('type').lower() != 'boolean':
                    # set the value to the default in the install.json file unless the type
                    # is boolean. changing a boolean value to True when not there will change
                    # the logic of the test case.
                    value = data.get('default', None)

                # get input type based on install.json required field
                input_type = 'optional'
                if data.get('required'):
                    input_type = 'required'

                # APP-87 - ensure boolean inputs don't have null values
                if data.get('type').lower() == 'boolean':
                    if not isinstance(value, bool):
                        value = False

                # update inputs for next permutation check
                inputs[name] = value

                # store merged/updated inputs for writing back to profile
                merged_inputs[input_type][name] = value

            # ADI-1376 - handle tcex default args (prevent removing)
            if profile_inputs.get('defaults'):
                merged_inputs['defaults'] = profile_inputs.get('defaults')
            updated_params.append(merged_inputs)

        # update the profile with merged config/inputs
        profile_data = self.contents
        if self.ij.runtime_level.lower() in ['triggerservice', 'webhooktriggerservice']:
            for index, config_item in enumerate(profile_data.get('configs', [])):
                config_item['config'] = updated_params[index]
        else:
            profile_data['inputs'] = updated_params[0]

        # write updated profile
        self.write(profile_data)

    def migrate(self):
        """Migration the profile to the latest schema"""
        migrate = Migrate(self)
        self.data = migrate.data

    @property
    def name(self):
        """Return partially parsed test case data."""
        if self._name is None:
            name_pattern = r'^test_[a-zA-Z0-9_]+\[(.+)\]$'
            self._name = re.search(name_pattern, self._test_case_data[-1]).group(1)
        return self._name

    @name.setter
    def name(self, name):
        """Set the profile name"""
        self._name = name

    def order_profile(self, profile_data):
        """Order the profile data properly."""
        comments = profile_data.pop('_comments_', None)
        environments = profile_data.pop('environments', None)
        exit_codes = profile_data.pop('exit_codes', None)
        exit_message = profile_data.pop('exit_message', None)
        configs = profile_data.pop('configs', None)
        inputs = profile_data.pop('inputs', None)
        options = profile_data.pop('options', None)
        outputs = profile_data.pop('outputs', None)
        stage = profile_data.pop('stage', None)
        trigger = profile_data.pop('trigger', None)
        validation_criteria = profile_data.pop('validation_criteria', None)
        webhook_event = profile_data.pop('webhook_event', None)

        profile = OrderedDict()
        if comments is not None:
            profile['_comments_'] = comments
        if environments is not None:
            profile['environments'] = environments
        if stage is not None:
            profile['stage'] = self._sorted(stage)
        if configs is not None:
            profile['configs'] = self._sorted(configs)
        if inputs is not None:
            profile['inputs'] = self._sorted(inputs)
        if trigger is not None:
            profile['trigger'] = self._sorted(trigger)
        if webhook_event is not None:
            profile['webhook_event'] = self._sorted(webhook_event)
        if validation_criteria is not None:
            profile['validation_criteria'] = validation_criteria
        if exit_message is not None:
            profile['exit_message'] = self._sorted(exit_message)
        if outputs is not None:
            profile['outputs'] = self._sorted(outputs)
        if options is not None:
            profile['options'] = self._sorted(options)
        if exit_codes is not None:
            profile['exit_codes'] = self._sorted(exit_codes)

        # add any additional fields not covered above
        for k, v in profile_data.items():
            profile[k] = v

        return profile

    @property
    def profile_inputs(self):
        """Return the appropriate inputs (config) for the current App type.

        Service App use config and others use inputs.

        "inputs": {
            "default": {}
            "optional": {}
            "required": {}
        }
        """
        if self.ij.runtime_level.lower() in ['triggerservice', 'webhooktriggerservice']:
            for config_data in self.configs:
                yield config_data.get('config')
        else:
            yield self.inputs

    @property
    def profile_inputs_params(self):
        """Return params for inputs."""
        # handle non-layout and layout based App appropriately
        for profile_inputs in self.profile_inputs:
            params = self.ij.params_dict  # params section of install.json build as dict
            if self.lj.has_layout:
                # using inputs from layout.json since they are required to be in order
                # (display field can only use inputs previously defined)
                params = {}
                for name in self.lj.params_dict:
                    # get data from install.json based on name
                    params[name] = self.ij.params_dict.get(name)

                # hidden fields will not be in layout.json so they need to be included manually
                params.update(self.ij.filter_params_dict(hidden=True))

            yield profile_inputs, params

    # TODO: BCS - move this
    @property
    def pytest_args(self):
        """Return dict of pytest config args."""
        if self._pytest_args is None:
            self._pytest_args = {}
            if self.pytestconfig:
                args = self.pytestconfig.option  # argparse.Namespace
                self._pytest_args = {
                    'merge_inputs': args.merge_inputs or False,
                    'merge_outputs': args.merge_outputs or False,
                    'replace_exit_message': args.replace_exit_message or False,
                    'replace_outputs': args.replace_outputs or False,
                    'record_session': args.record_session or False,
                    'ignore_session': args.ignore_session or False,
                }

        return self._pytest_args

    def remove_comments(self, data):
        """Iterate through data and remove any dict field with a value of "comments"

        Args:
            data (dict): The profile dictionary.
        """
        data = data or {}
        for _, v in list(data.items()):
            try:
                del data['_comments_']
            except KeyError:
                pass

            if isinstance(v, dict):
                self.remove_comments(v)

    @property
    def session(self):
        """Return a instance of the session manager."""
        if self._session is None:
            self._session = TcSession(
                self.env_store.getenv('/ninja/tc/tci/exchange_admin/api_access_id'),
                self.env_store.getenv('/ninja/tc/tci/exchange_admin/api_secret_key'),
                os.getenv('TC_API_PATH'),
            )
        return self._session

    @property
    def session_manager(self):
        """Return a instance of the session manager."""
        if not self._session_manager:
            self._session_manager = SessionManager(self)

        return self._session_manager

    @property
    def test_directory(self):
        """Return fully qualified test directory."""
        return os.path.join(self._app_path, 'tests')

    def update_exit_message(self):
        """Update validation rules from exit_message section of profile."""
        message_tc = ''
        if os.path.isfile(self.message_tc_filename):
            with open(self.message_tc_filename, 'r') as mh:
                message_tc = mh.read()

        profile_data = self.contents
        if (
            profile_data.get('exit_message') is None
            or isinstance(profile_data.get('exit_message'), str)
            or self.pytest_args.get('replace_exit_message')
        ):
            # update the profile
            profile_data['exit_message'] = {'expected_output': message_tc, 'op': 'eq'}

            self.write(profile_data, 'updating exit message')

    def update_outputs(self):
        """Update the validation rules for outputs section of a profile.

        By default this method will only update if the current value is null. If the
        flag --replace_outputs is passed to pytest (e.g., pytest --replace_outputs)
        the outputs will replaced regardless of their current value. If the flag
        --merge_outputs is passed to pytest (e.g., pytest --merge_outputs) any new
        outputs will be added and any outputs that are not longer valid will be
        removed.
        """
        if self.redis_client is None:
            # redis_client is only available for children of TestCasePlaybookCommon
            print(f'{c.Fore.RED}An instance of redis_client is not set.')
            sys.exit(1)

        outputs = {}
        trigger_id = None
        for context in self.context_tracker:
            # get all current keys in current context
            redis_data = self.redis_client.hgetall(context)
            trigger_id = self.redis_client.hget(context, '_trigger_id')

            # updated outputs with validation data
            self.update_outputs_variables(outputs, redis_data, trigger_id)

            # cleanup redis
            self.clear_context(context)

        if not self.outputs or self.pytest_args.get('replace_outputs'):
            # update profile if current profile is not or user specifies --replace_outputs
            profile_data = self.contents
            profile_data['outputs'] = outputs
            self.write(profile_data)
        elif self.pytest_args.get('merge_outputs'):
            if trigger_id is not None:
                # service Apps have a different structure with id: data
                merged_outputs = {}
                for id_, data in outputs.items():
                    merged_outputs[id_] = {}
                    for key in list(data):
                        if key in self.outputs.get(id_, {}):
                            # use current profile output value if exists
                            merged_outputs[id_][key] = self.outputs[id_][key]
                        else:
                            merged_outputs[id_][key] = outputs[id_][key]
            else:
                # update playbook App profile outputs
                merged_outputs = {}
                for key in list(outputs):
                    if key in self.outputs:
                        # use current profile output value if exists
                        merged_outputs[key] = self.outputs[key]
                    else:
                        merged_outputs[key] = outputs[key]

            profile_data = self.contents
            profile_data['outputs'] = merged_outputs
            self.write(profile_data)

    def update_outputs_variables(self, outputs, redis_data, trigger_id):
        """Return the outputs section of a profile.

        Args:
            outputs (dict): The dict to add outputs.
            redis_data (dict): The data from KV store for this profile.
            trigger_id (str): The current trigger_id (service Apps).
        """
        for variable in self.tc_playbook_out_variables:
            # TODO: investigate moving to output rules validator
            # APP-219 - check for "bad" output variable names
            if 'raw.json' in variable:
                self.log.data(
                    'validate',
                    'Suspect Value',
                    'Output variable matched a suspect value (raw.json).',
                    'warning',
                )

            # get data from redis for current context
            data = redis_data.get(variable.encode('utf-8'))

            # validate redis variables
            if data is None:
                if 1 not in self.exit_codes:
                    # TODO: add feature in testing framework to allow writing null and
                    #       then check if variables exist instead of null value.
                    # log error for missing output data if not a fail test case (exit code of 1)
                    self.log.data(
                        'validate',
                        'Missing Data',
                        f'possible missing KV Store data for variable {variable}',
                        'info',
                    )
            else:
                data = json.loads(data.decode('utf-8'))

            # validate validation variables
            validation_data = (self.outputs or {}).get(variable)
            if trigger_id is None and validation_data is None and self.outputs:
                self.log.error(f'[{self.name}] Missing validations rule: {variable}')

            # make business rules based on data type or content
            output_data = {'expected_output': data, 'op': 'eq'}
            if 1 not in self.exit_codes:
                output_data = self.rules.data(data)

            # get trigger id for service Apps
            if trigger_id is not None:
                if isinstance(trigger_id, bytes):
                    trigger_id = trigger_id.decode('utf-8')
                outputs.setdefault(trigger_id, {})
                outputs[trigger_id][variable] = output_data
            else:
                outputs[variable] = output_data

    def validate_inputs(self):
        """Validate required inputs.

        This method will also merge input if --merge_inputs is passed to pytest.
        """
        errors = []
        status = True

        # handle non-layout and layout based App appropriately
        for profile_inputs, params in self.profile_inputs_params:
            profile_inputs_flattened = self._flatten_inputs(profile_inputs)

            inputs = {}
            for name, data in params.items():
                if data.get('serviceConfig'):
                    # inputs that are serviceConfig are not applicable for profiles
                    continue

                if not data.get('hidden'):
                    # each non hidden input will be checked for permutations if the App has layout
                    if not self.permutations.validate_input_variable(name, inputs):
                        continue

                # get the value from the current profile or use default value from install.json
                value = profile_inputs_flattened.get(name)
                if name not in profile_inputs_flattened:
                    value = data.get('default', None)

                if data.get('required'):
                    if value in [None, '']:  # exclude 0 or False from check
                        # validation step
                        errors.append(f'- Missing/Invalid value for required arg ({name})')
                        status = False

                # APP-87 - ensure boolean inputs don't have null values
                if data.get('type').lower() == 'boolean':
                    if not isinstance(value, bool):
                        # validation step
                        errors.append(f'- Invalid value for boolean arg ({name})')
                        status = False

                # update inputs
                inputs[name] = value

        errors = '\n'.join(errors)  # convert error to string for assert message
        return status, f'\n{errors}'

    def write(self, json_data, reason=None):
        """Write updated profile file.

        Args:
            json_data (dict): The profile data.
            reason (str, default:None): The reason for the update.
        """
        # Permuted test cases set options to a true value, so disable writeback
        if self.test_options:
            return

        # order the profile data appropriately
        json_data = self.order_profile(json_data)

        if reason is not None:
            self.log.data(
                'profile', 'Profile Update', f'writing updated profile for {reason}', 'info'
            )

        with open(self.filename, 'w') as fh:
            json.dump(json_data, fh, indent=2, sort_keys=False)
            fh.write('\n')

    #
    # Properties
    #

    @property
    def args(self):
        """Return combined/flattened args."""
        return self.inputs_flattened

    @property
    def configs(self):
        """Return environments."""
        return list(self.data.get('configs', []))

    @property
    def environments(self):
        """Return environments."""
        return self.data.get('environments', ['build'])

    @property
    def exit_codes(self):
        """Return exit codes."""
        return self.data.get('exit_codes', [])

    @property
    def exit_message(self):
        """Return exit message dict."""
        return self.data.get('exit_message', {})

    @property
    def inputs(self):
        """Return inputs dict."""
        return self.data.get('inputs', {})

    @property
    def inputs_defaults(self):
        """Return required inputs dict."""
        return self.inputs.get('defaults', {})

    @property
    def inputs_flattened(self):
        """Return inputs dict."""
        return self._flatten_inputs(self.inputs)

    @property
    def inputs_optional(self):
        """Return required inputs dict."""
        return self.inputs.get('optional', {})

    @property
    def inputs_required(self):
        """Return required inputs dict."""
        return self.inputs.get('required', {})

    @property
    def message_tc_filename(self):
        """Return the fqpn for message_tc file relative to profile."""
        return os.path.join(
            self._default_args.get('tc_out_path'), self.feature, self._test_case_name, 'message.tc'
        )

    @property
    def options(self):
        """Return options dict."""
        if self.data.get('options') is None:
            self.data['options'] = {}
        return self.data.get('options')

    @property
    def owner(self):
        """Return the owner value."""
        return self.inputs_flattened.get('owner')

    @property
    def outputs(self):
        """Return outputs dict."""
        return self.data.get('outputs')

    @property
    def rargs(self):
        """Return combined/flattened args with value from staging data if required."""
        rargs = {}
        for arg, value in self.args.items():
            if re.match(self.utils.variable_match, value):
                # look for value in staging data
                if self.stage_kvstore.get(value) is not None:
                    value = self.stage_kvstore.get(value)
            rargs[arg] = value
        return rargs

    @property
    def stage(self):
        """Return stage dict."""
        if self.data.get('stage') is None:
            self.data['stage'] = {}
        return self.data.get('stage', {})

    @property
    def stage_kvstore(self):
        """Return stage kv store dict."""
        return self.stage.get('kvstore', {})

    @property
    def stage_threatconnect(self):
        """Return stage threatconnect dict."""
        return self.stage.get('threatconnect', {})

    @property
    def tc_in_path(self):
        """Return fqpn tc_in_path arg relative to profile."""
        if self.ij.runtime_level.lower() in ['triggerservice', 'webhooktriggerservice']:
            tc_in_path = os.path.join(self._default_args.get('tc_in_path'), self.feature)
        else:
            tc_in_path = os.path.join(
                self._default_args.get('tc_in_path'), self.feature, self._test_case_name
            )
        return tc_in_path

    @property
    def tc_log_path(self):
        """Return fqpn tc_log_path arg relative to profile."""
        if self.ij.runtime_level.lower() in ['triggerservice', 'webhooktriggerservice']:
            tc_log_path = os.path.join(self._default_args.get('tc_log_path'), self.feature)
        else:
            tc_log_path = os.path.join(
                self._default_args.get('tc_log_path'), self.feature, self._test_case_name
            )
        return tc_log_path

    @property
    def tc_out_path(self):
        """Return fqpn tc_out_path arg relative to profile."""
        if self.ij.runtime_level.lower() in ['triggerservice', 'webhooktriggerservice']:
            tc_out_path = os.path.join(self._default_args.get('tc_out_path'), self.feature)
        else:
            tc_out_path = os.path.join(
                self._default_args.get('tc_out_path'), self.feature, self._test_case_name
            )
        return tc_out_path

    @property
    def tc_playbook_out_variables(self):
        """Return calculated output variables.

        * iterate over all inputs:
          * if input key has exposePlaybookKeyAs defined
          * if value a variable
            * lookup value in stage.kvstore data
            * for each key add to output variables
        """
        output_variables = self.ij.tc_playbook_out_variables
        if self.lj.has_layout:
            # if layout based App get valid outputs
            output_variables = self.ij.create_output_variables(
                self.permutations.outputs_by_inputs(self.inputs_flattened)
            )

        for arg, value in self.inputs_flattened.items():
            # get full input data from install.json
            input_data = self.ij.params_dict.get(arg, {})

            # check to see if it support dynamic output variables
            if 'exposePlaybookKeyAs' not in input_data:
                continue

            # get the output variable type from install.json input data
            variable_type = input_data.get('exposePlaybookKeyAs')

            # staged data for this dynamic input must be a KeyValueArray
            for data in self.stage_kvstore.get(value, []):
                # create a variable using key value
                variable = self.ij.create_variable(data.get('key'), variable_type, job_id=9876)
                output_variables.append(variable)

        # APP-77 - add _fired for service Apps
        if self.ij.runtime_level.lower() in ['triggerservice', 'webhooktriggerservice']:
            output_variables.append('#Trigger:9876:_fired!String')

        return output_variables

    @property
    def tc_temp_path(self):
        """Return fqpn tc_temp_path arg relative to profile."""
        if self.ij.runtime_level.lower() in ['triggerservice', 'webhooktriggerservice']:
            tc_temp_path = os.path.join(self._default_args.get('tc_temp_path'), self.feature)
        else:
            tc_temp_path = os.path.join(
                self._default_args.get('tc_temp_path'), self.feature, self._test_case_name
            )
        return tc_temp_path

    @property
    def validation_criteria(self):
        """Return the validation_criteria value."""
        return self.data.get('validation_criteria', {})

    @property
    def webhook_event(self):
        """Return webhook event dict."""
        return self.data.get('webhook_event', {})
