# -*- coding: utf-8 -*-
"""TcEx Framework InstallJson Object."""
# standard library
import json
import logging
import os
import uuid
from collections import OrderedDict


class AppFeatureAdvanceRequest:
    """AdvancedRequest Module"""

    def __init__(self, ij, json_data, prefix):
        """Initialize Class properties."""
        self.ij = ij
        self.json_data = json_data
        self._prefix = prefix

    @staticmethod
    def get_index(params, key, value):
        """Return the index of a dict from a list of dicts."""
        for index, data in enumerate(params):
            if data.get(key) == value:
                return index
        return None

    @property
    def inputs(self):
        """Return Advanced Request Inputs."""
        return [
            {
                'label': 'API Endpoint/Path',
                'name': 'tc_adv_req_path',
                'note': 'The API Path request.',
                'playbookDataType': ['String'],
                'required': True,
                'sequence': 100,
                'type': 'String',
                'validValues': ['${TEXT}'],
            },
            {
                'default': 'GET',
                'encrypt': False,
                'label': 'HTTP Method',
                'name': 'tc_adv_req_http_method',
                'note': 'HTTP method to use.',
                'required': True,
                'sequence': 101,
                'type': 'Choice',
                'validValues': ['GET', 'POST', 'DELETE', 'PUT', 'HEAD', 'PATCH', 'OPTIONS'],
            },
            {
                'label': 'Query Parameters',
                'name': 'tc_adv_req_params',
                'note': (
                    'Query parameters to append to the URL. For sensitive information like API '
                    'keys, using variables is recommended to ensure that the Playbook will not '
                    'export sensitive data.'
                ),
                'playbookDataType': ['String', 'StringArray'],
                'required': False,
                'sequence': 102,
                'type': 'KeyValueList',
                'validValues': ['${KEYCHAIN}', '${TEXT}'],
            },
            {
                'default': False,
                'label': 'Exclude Empty/Null Parameters',
                'name': 'tc_adv_req_exclude_null_params',
                'note': (
                    'Some API endpoint don\'t handle null/empty query parameters properly '
                    '(e.g., ?name=&type=String). If selected this options will exclude any '
                    'query parameters that has a null/empty value.'
                ),
                'required': False,
                'sequence': 103,
                'type': 'Boolean',
            },
            {
                'label': 'Headers',
                'name': 'tc_adv_req_headers',
                'note': (
                    'Headers to include in the request. When using Multi-part Form/File data, do '
                    '**not** add a **Content-Type** header. For sensitive information like API '
                    'keys, using variables is recommended to ensure that the Playbook will not '
                    'export sensitive data.'
                ),
                'playbookDataType': ['String'],
                'required': False,
                'sequence': 104,
                'type': 'KeyValueList',
                'validValues': ['${KEYCHAIN}', '${TEXT}'],
            },
            {
                'label': 'Body',
                'name': 'tc_adv_req_body',
                'note': 'Content of the HTTP request.',
                'playbookDataType': ['String', 'Binary'],
                'required': False,
                'sequence': 105,
                'type': 'String',
                'validValues': ['${KEYCHAIN}', '${TEXT}'],
                'viewRows': 4,
            },
            {
                'label': 'URL Encode JSON Body',
                'name': 'tc_adv_req_urlencode_body',
                'note': (
                    'URL encode a JSON-formatted body. Typically used for '
                    '\'x-www-form-urlencoded\' data, where the data can be configured '
                    'in the body as a JSON string.'
                ),
                'required': False,
                'sequence': 106,
                'type': 'Boolean',
            },
            {
                'default': True,
                'label': 'Fail for Status',
                'name': 'tc_adv_req_fail_on_error',
                'note': 'Fail if the response status code is 4XX - 5XX.',
                'sequence': 107,
                'type': 'Boolean',
            },
        ]

    @property
    def outputs(self):
        """Return Advanced Request Outputs."""
        return [
            {'name': f'{self.prefix}.request.content', 'type': 'String'},
            {'name': f'{self.prefix}.request.content.binary', 'type': 'Binary'},
            {'name': f'{self.prefix}.request.headers', 'type': 'String'},
            {'name': f'{self.prefix}.request.ok', 'type': 'String'},
            {'name': f'{self.prefix}.request.reason', 'type': 'String'},
            {'name': f'{self.prefix}.request.status_code', 'type': 'String'},
            {'name': f'{self.prefix}.request.url', 'type': 'String'},
        ]

    @property
    def prefix(self):
        """Return prefix for output variables."""
        if self._prefix is None:
            self._prefix = 'unknown'
            for o in self.ij.output_variables:
                self._prefix = o.get('name').split('.')[0]
        return self._prefix

    def update(self):
        """Update the install.json inputs and outputs."""
        self.update_inputs()
        self.update_outputs()

        for p in self.json_data['params']:
            if p.get('name') == 'tc_action':
                if 'Advanced Request' not in p['validValues']:
                    p['validValues'].append('Advanced Request')

    def update_inputs(self):
        """Update install.json param inputs."""
        for i in self.inputs:
            # check to see if input was previously added
            if i.get('name') in self.ij.params_dict:
                # replace existing data
                index = self.get_index(self.json_data['params'], 'name', i.get('name'))
                self.json_data['params'][index] = i
            else:
                # append input
                self.json_data['params'].append(i)

    def update_outputs(self):
        """Update install.json param inputs."""
        for o in self.outputs:
            # check to see if output was previously added
            if o.get('name') in self.ij.output_dict:
                # replace existing data
                index = self.get_index(
                    self.json_data['playbook']['outputVariables'], 'name', o.get('name')
                )
                self.json_data['playbook']['outputVariables'][index] = o
            else:
                # append input
                self.json_data['playbook']['outputVariables'].append(o)


class InstallJson:
    """Object for install.json file.

    Args:
        filename (str, optional): The config filename. Defaults to install.json.
        path (str, optional): The path to the file. Defaults to os.getcwd().
        logger (logging.Logger, optional): A instance of Logger. Defaults to None.
    """

    def __init__(self, filename=None, path=None, logger=None):
        """Initialize class properties."""
        self._filename = filename or 'install.json'
        self._path = path or os.getcwd()
        self.log = logger or logging.getLogger('install_json')

        # properties
        self._contents = None

    @property
    def _commit_hash(self):
        """Return the current commit hash if available.

        This is not a required task so best effort is fine. In other words this is not guaranteed
        to work 100% of the time.
        """
        commit_hash = None
        branch = None
        branch_file = '.git/HEAD'  # ref: refs/heads/develop

        # get current branch
        if os.path.isfile(branch_file):
            with open(branch_file, 'r') as f:
                try:
                    branch = f.read().strip().split('/')[2]
                except IndexError:
                    pass

            # get commit hash
            if branch:
                hash_file = f'.git/refs/heads/{branch}'
                if os.path.isfile(hash_file):
                    with open(hash_file, 'r') as f:
                        commit_hash = f.read().strip()
        return commit_hash

    @staticmethod
    def _to_bool(value):
        """Convert string value to bool."""
        bool_value = False
        if str(value).lower() in ['1', 'true']:
            bool_value = True
        return bool_value

    @property
    def app_output_var_type(self):
        """Return the appropriate output var type for the current App."""
        if self.runtime_level.lower() in ['triggerservice', 'webhooktriggerservice']:
            return 'Trigger'
        return 'App'

    @property
    def app_prefix(self):
        """Return the appropriate output var type for the current App."""
        if self.runtime_level.lower() == 'organization':
            return 'TC_-_'
        if self.runtime_level.lower() == 'playbook':
            return 'TCPB_-_'
        if self.runtime_level.lower() == 'triggerservice':
            return 'TCVC_-_'
        if self.runtime_level.lower() == 'webhooktriggerservice':
            return 'TCVW-_'
        return ''

    @property
    def contents(self):
        """Return install.json contents."""
        if self._contents is None:
            try:
                with open(self.filename, 'r') as fh:
                    self._contents = json.load(fh, object_pairs_hook=OrderedDict)
            except OSError:
                self._contents = {'runtimeLevel': 'external'}
        return self._contents

    def create_output_variables(self, output_variables, job_id=9876):
        """Create output variables.

        # "#App:9876:app.data.count!String"
        # "#Trigger:9876:app.data.count!String"

        Args:
            output_variables (dict): A dict of the output variables
            job_id (int): A job id to use in output variable string.
        """
        variables = []
        for p in output_variables:
            variables.append(self.create_variable(p.get('name'), p.get('type'), job_id))
        return variables

    def create_variable(self, var_name, var_type, job_id=1234):
        """Create output variables.

        # "#App:9876:app.data.count!String"
        # "#Trigger:9876:app.data.count!String"

        Args:
            var_name (str): The variable name.
            var_type (str): The variable type.
            job_id (int): A job id to use in output variable string.
        """
        return f'#{self.app_output_var_type}:{job_id}:{var_name}!{var_type}'

    @staticmethod
    def expand_valid_values(valid_values):
        """Expand supported playbook variables to their full list.

        Args:
            valid_values (list): The list of valid values for Choice or MultiChoice inputs.

        Returns:
            list: An expanded list of valid values for Choice or MultiChoice inputs.
        """
        valid_values = list(valid_values)
        if '${GROUP_TYPES}' in valid_values:
            valid_values.remove('${GROUP_TYPES}')
            valid_values.extend(
                [
                    'Adversary',
                    'Campaign',
                    'Document',
                    'Email',
                    'Event',
                    'Incident',
                    'Intrusion Set',
                    'Signature',
                    'Task',
                    'Threat',
                ]
            )
        elif '${OWNERS}' in valid_values:
            valid_values.remove('${OWNERS}')
        elif '${USERS}' in valid_values:
            valid_values.remove('${USERS}')
        return valid_values

    @property
    def filename(self):
        """Return the fqpn for the layout.json file."""
        return os.path.join(self._path, self._filename)

    def filter_params_dict(
        self,
        name=None,
        hidden=None,
        required=None,
        service_config=None,
        _type=None,
        input_permutations=None,
    ):
        """Return params as name/data dict.

        Args:
            name (str, optional): The name of the input to return. Defaults to None.
            hidden (bool, optional): If set the inputs will be filtered based on hidden field.
            required (bool, optional): If set the inputs will be filtered based on required field.
            service_config (bool, optional): If set the inputs will be filtered based on
                serviceConfig field.
            _type (str, optional): The type of input to return. Defaults to None.
            input_permutations (list, optional): A list of valid input names for provided
                permutation.

        Returns:
            dict: All valid inputs for current filter.
        """
        params = {}
        for p in self.params:

            if name is not None:
                if p.get('name') != name:
                    continue

            if hidden is not None:
                if p.get('hidden', False) is not hidden:
                    continue

            if required is not None:
                if p.get('required', False) is not required:
                    continue

            if service_config is not None:
                if p.get('serviceConfig', False) is not service_config:
                    continue

            if _type is not None:
                if p.get('type') != _type:
                    continue

            if input_permutations is not None:
                if p.get('name') not in input_permutations:
                    continue

            params.setdefault(p.get('name'), p)
        return params

    @property
    def optional_params_dict(self):
        """Return params as name/data dict."""
        params = {}
        for p in self.params:
            if p.get('required', False) is False:
                params.setdefault(p.get('name'), p)
        return params

    @property
    def output_dict(self):
        """Return outputs as name/data dict."""
        outputs = {}
        for o in self.output_variables:
            outputs.setdefault(o.get('name'), o)
        return outputs

    @property
    def params_dict(self):
        """Return params as name/data dict."""
        params = {}
        for p in self.params:
            params.setdefault(p.get('name'), p)
        return params

    def params_to_args(
        self,
        name=None,
        hidden=None,
        required=None,
        service_config=None,
        _type=None,
        input_permutations=None,
    ):
        """Return params as cli args.

        Args:
            name (str, optional): The name of the input to return. Defaults to None.
            required (bool, optional): If set the inputs will be filtered based on required field.
            service_config (bool, optional): If set the inputs will be filtered based on
                serviceConfig field.
            _type (str, optional): The type of input to return. Defaults to None.
            input_permutations (list, optional): A list of valid input names for provided
                permutation.

        Returns:
            dict: All valid inputs for current filter.
        """
        args = {}
        for n, p in self.filter_params_dict(
            name, hidden, required, service_config, _type, input_permutations
        ).items():
            if p.get('type').lower() == 'boolean':
                args[n] = self._to_bool(p.get('default', False))
            elif p.get('type').lower() == 'choice':
                # use the value from input_permutations if available or provide valid values
                valid_values = f"[{'|'.join(self.expand_valid_values(p.get('validValues', [])))}]"
                if input_permutations is not None:
                    valid_values = input_permutations.get(n, valid_values)
                args[n] = valid_values
            elif p.get('type').lower() == 'multichoice':
                args[n] = p.get('validValues', [])
            elif p.get('type').lower() == 'keyvaluelist':
                args[n] = '<KeyValueArray>'
            elif n in ['api_access_id', 'api_secret_key']:
                # leave these parameters set to the value defined in defaults
                pass
            else:
                types = '|'.join(p.get('playbookDataType', []))
                if types:
                    args[n] = p.get('default', f'<{types}>')
                else:
                    args[n] = p.get('default', '')
        return args

    @property
    def require_params_dict(self):
        """Return params as name/data dict."""
        params = {}
        for p in self.params:
            if p.get('required') is True:
                params.setdefault(p.get('name'), p)
        return params

    @property
    def service_config_params_dict(self):
        """Return params as name/data dict."""
        params = {}
        for p in self.params:
            if p.get('serviceConfig') is True:
                params.setdefault(p.get('name'), p)
        return params

    @property
    def tc_playbook_out_variables(self):
        """Return playbook output variable name array"""
        return self.create_output_variables(self.output_variables)

    @property
    def tc_playbook_out_variables_csv(self):
        """Return playbook output variables as CSV string"""
        return ','.join(self.tc_playbook_out_variables)

    @property
    def trigger_config_params_dict(self):
        """Return params as name/data dict."""
        params = {}
        for p in self.params:
            if p.get('serviceConfig', False) is False:
                params.setdefault(p.get('name'), p)
        return params

    def update(
        self,
        commit_hash=False,
        features=True,
        migrate=False,
        sequence=True,
        valid_values=True,
        playbook_data_types=True,
    ):
        """Update the profile with all required changes.

        Args:
            commit_hash (bool, optional): If True the commitHash value will be added.
            features (bool, optional): If True the features array will be updated.
            migrate (bool, optional): If True the programMain will be set to "run".
            sequence (bool, optional): If True the sequence numbers will be updated.
            valid_values (bool, optional): If True the valid values will be updated.
            playbook_data_types (bool, optional):  If True the pbDataTypes will be updated.
        """
        with open(self.filename, 'r+') as fh:
            json_data = json.load(fh)

            # update appId field
            json_data = self.update_app_id(json_data)

            # update commitHash field
            if commit_hash is True:
                json_data = self.update_commit_hash(json_data)

            # update displayName field
            json_data = self.update_display_name(json_data)

            # update features array
            if features is True:
                json_data = self.update_features(json_data)

            if migrate is True:
                # update programMain to run
                json_data = self.update_program_main(json_data)

            # update sequence numbers
            if sequence is True:
                json_data = self.update_sequence_numbers(json_data)

            # update valid values
            if valid_values is True:
                json_data = self.update_valid_values(json_data)

            # update playbook data types
            if playbook_data_types is True:
                json_data = self.update_playbook_data_types(json_data)

            # app feature - update install.json for Advanced Request
            if 'advancedRequest' in self.features and self.output_prefix is not None:
                afar = AppFeatureAdvanceRequest(self, json_data, self.output_prefix)
                afar.update()

            # write updated profile
            fh.seek(0)
            fh.write(f'{json.dumps(json_data, indent=2, sort_keys=True)}\n')
            fh.truncate()

        self._contents = json_data

    @staticmethod
    def update_app_id(json_data):
        """Update to ensure an appId field exists.

        All App should have an appId to uniquely identify the App. this is not intended to be
        used by core to identify an App.  using appId + major Version could be used for unique
        App identification in core in a future release.
        """
        if json_data.get('appId') is None:
            json_data['appId'] = str(
                uuid.uuid5(uuid.NAMESPACE_X500, os.path.basename(os.getcwd()).lower())
            )
        return json_data

    def update_commit_hash(self, json_data):
        """Update to ensure an appId field exists.

        Add/Update the commit hash to the install.json file if possible.
        """
        if self._commit_hash:
            json_data['commitHash'] = self._commit_hash
        return json_data

    def update_display_name(self, json_data):
        """Update the displayName parameter."""
        if not json_data.get('displayName'):
            display_name = os.path.basename(os.getcwd()).replace(self.app_prefix, '')
            display_name = display_name.replace('_', ' ').replace('-', ' ')
            display_name = ' '.join([a.title() for a in display_name.split(' ')])
            json_data['displayName'] = display_name
        return json_data

    def update_features(self, json_data):
        """Update feature set based on App type."""
        features = self.features
        if self.runtime_level.lower() in ['organization']:
            features = ['fileParams', 'secureParams']
        elif self.runtime_level.lower() in ['playbook']:
            features = [
                'aotExecutionEnabled',
                'appBuilderCompliant',
                'fileParams',
                'secureParams',
            ]
        elif self.runtime_level.lower() in [
            'apiservice',
            'triggerservice',
            'webhooktriggerservice',
        ]:
            features = ['appBuilderCompliant', 'fileParams']

        # add layoutEnabledApp if layout.json file exists in project
        if os.path.isfile(os.path.join(self._path, 'layout.json')):
            features.append('layoutEnabledApp')

        # re-add other non-standard (optional) features
        for feature in self.features:
            if feature in ['advancedRequest', 'CALSettings']:
                features.append(feature)

        json_data['features'] = sorted(features)
        return json_data

    def update_program_main(self, json_data):
        """Update program main on App type."""
        if self.program_main:
            if self.runtime_level.lower() in ['playbook']:
                json_data['programMain'] = 'run'
            elif self.runtime_level.lower() in ['triggerservice', 'webhooktriggerservice']:
                json_data['programMain'] = 'run'
        return json_data

    @staticmethod
    def update_sequence_numbers(json_data):
        """Update program main on App type."""
        sequence_number = 1
        for param in json_data.get('params', []):
            param['sequence'] = sequence_number
            sequence_number += 1
        return json_data

    @staticmethod
    def update_valid_values(json_data):
        """Update program main on App type."""
        for param in json_data.get('params', []):
            if param.get('type', None) not in ['String', 'KeyValueList']:
                continue
            if param.get('encrypt', False):
                if '${KEYCHAIN}' not in param.get('validValues', []):
                    param['validValues'] = param.get('validValues') or []
                    param['validValues'].append('${KEYCHAIN}')
            else:
                if '${TEXT}' not in (param.get('validValues') or []):
                    param['validValues'] = param.get('validValues') or []
                    param['validValues'].append('${TEXT}')
        return json_data

    @staticmethod
    def update_playbook_data_types(json_data):
        """Update program main on App type."""
        if json_data.get('runtimeLevel', None) != 'Playbook':
            return json_data

        for param in json_data.get('params', []):
            if param.get('type', None) != 'String':
                continue
            if 'String' not in (param.get('playbookDataType') or []):
                param['playbookDataType'] = param.get('playbookDataType') or []
                param['playbookDataType'].append('String')
        return json_data

    def validate(self):
        """Validate install.json."""

        # check for duplicate input names
        self.validate_duplicate_input_names()

        # check for duplicate input names
        self.validate_duplicate_sequences()

    def validate_duplicate_input_names(self):
        """Check for duplicate input names."""
        duplicates = []
        name_tracker = []
        for p in self.params:
            name = p.get('name')
            if name in name_tracker:
                duplicates.append(name)
            name_tracker.append(name)
        return duplicates

    def validate_duplicate_sequences(self):
        """Check for duplicate sequence numbers."""
        duplicates = []
        sequence_tracker = []
        for p in self.params:
            sequence = p.get('sequence')
            if sequence in sequence_tracker:
                duplicates.append(sequence)
            sequence_tracker.append(sequence)
        return duplicates

    def validate_duplicate_outputs(self):
        """Check for duplicate input names."""
        duplicates = []
        name_type_tracker = []
        for o in self.output_variables:
            name = o.get('name')
            type_ = o.get('type')
            name_type = f'{name}-{type_}'
            if name_type in name_type_tracker:
                duplicates.append(name)
            name_type_tracker.append(name_type)
        return duplicates

    #
    # properties
    #

    @property
    def allow_on_demand(self):
        """Return property."""
        return self.contents.get('allowOnDemand', False)

    @property
    def commit_hash(self):
        """Return property."""
        return self.contents.get('commitHash')

    @property
    def display_name(self):
        """Return property."""
        return self.contents.get('displayName')

    @property
    def features(self):
        """Return property."""
        return self.contents.get('features', [])

    @property
    def feeds(self):
        """Return property."""
        return self.contents.get('feeds', {})

    @property
    def labels(self):
        """Return property."""
        return self.contents.get('labels', [])

    @property
    def language_version(self):
        """Return property."""
        return self.contents.get('languageVersion')

    @property
    def list_delimiter(self):
        """Return property."""
        return self.contents.get('listDelimiter')

    @property
    def min_server_version(self):
        """Return property."""
        return self.contents.get('minServerVersion')

    @property
    def note(self):
        """Return property."""
        return self.contents.get('note')

    @property
    def output_prefix(self):
        """Return output prefix."""
        return self.playbook.get('outputPrefix')

    @property
    def output_variables(self):
        """Return output variables dict."""
        return self.playbook.get('outputVariables', [])

    @property
    def params(self):
        """Return property."""
        return self.contents.get('params', [])

    @property
    def playbook(self):
        """Return property."""
        return self.contents.get('playbook', {})

    @property
    def playbook_type(self):
        """Return property."""
        return self.playbook.get('type')

    @property
    def program_icon(self):
        """Return property."""
        return self.contents.get('programIcon')

    @property
    def program_language(self):
        """Return property."""
        return self.contents.get('programLanguage')

    @property
    def program_main(self):
        """Return property."""
        return self.contents.get('programMain')

    @property
    def program_name(self):
        """Return property."""
        return self.contents.get('programName')

    @property
    def program_version(self):
        """Return property."""
        return self.contents.get('programVersion', '1.0.0')

    @property
    def publish_out_files(self):
        """Return property."""
        return self.contents.get('publishOutFiles')

    @property
    def repeating_minutes(self):
        """Return property."""
        return self.contents.get('repeatingMinutes')

    @property
    def runtime_context(self):
        """Return property."""
        return self.contents.get('runtimeContext')

    @property
    def runtime_level(self):
        """Return property."""
        return self.contents.get('runtimeLevel')
