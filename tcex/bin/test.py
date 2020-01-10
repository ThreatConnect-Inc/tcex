#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework Profile Generation Module."""
import json
import os
import re
import sys
from random import randint

import colorama as c
import requests

from .bin import Bin

try:
    from mako.template import Template
except ImportError:
    pass  # mako is only required for local testing


BASE_URL = 'https://raw.githubusercontent.com/ThreatConnect-Inc/tcex'


class CustomTemplates:
    """Custom method Template Class"""

    def __init__(self, base_dir, branch='master'):
        """Initialize class properties."""
        self.branch = branch
        self.base_dir = base_dir

    @property
    def feature_template(self):
        """Return the feature template file for custom methods"""
        url = f"{BASE_URL}/{self.branch}/app_init/tests/{'custom_feature.py.tpl'}"
        r = requests.get(url, allow_redirects=True)
        if not r.ok:
            raise RuntimeError('Could not download template file.')
        return r.content

    @property
    def parent_template(self):
        """Return the parent template file for custom methods"""
        url = f"{BASE_URL}/{self.branch}/app_init/tests/{'custom.py.tpl'}"
        r = requests.get(url, allow_redirects=True)
        if not r.ok:
            raise RuntimeError('Could not download template file.')
        return r.content

    def render_templates(self, feature, app_type):
        """Render the templates and write to disk conditionally."""
        variables = {'app_type': app_type}

        parent_file = os.path.join(self.base_dir, 'custom.py')
        if not os.path.isfile(parent_file):
            template = Template(self.parent_template)
            rendered_template = template.render(**variables)
            with open(parent_file, 'a') as f:
                f.write(rendered_template)

        feature_file = os.path.join(self.base_dir, feature, 'custom_feature.py')
        if not os.path.isfile(feature_file):
            template = Template(self.feature_template)
            rendered_template = template.render(**variables)
            with open(feature_file, 'a') as f:
                f.write(rendered_template)


class Profiles:
    """Profile Class

    Raises:
        NotImplementedError: The delete method is not currently implemented.
        NotImplementedError: The update method is not currently implemented.
    """

    def __init__(self, profile_dir):
        """Initialize class properties."""
        self.profile_dir = profile_dir

        # properties
        self._profiles = None

    def add(self, profile_name, profile_data, sort_keys=True):
        """Add a profile."""
        profile_filename = os.path.join(self.profile_dir, f'{profile_name}.json')
        if os.path.isfile(profile_filename):
            print(
                f'{c.Style.BRIGHT}{c.Fore.RED}A profile with the name '
                f'({profile_name}) already exists.'
            )
            sys.exit(1)

        profile = {
            'exit_codes': profile_data.get('exit_codes', [0]),
            'exit_message': None,
            'outputs': profile_data.get('outputs'),
            'stage': profile_data.get('stage', {'redis': {}, 'threatconnect': {}}),
        }
        if profile_data.get('runtime_level').lower() == 'triggerservice':
            profile['configs'] = profile_data.get('configs')
            profile['trigger'] = profile_data.get('trigger')
        elif profile_data.get('runtime_level').lower() == 'webhooktriggerservice':
            profile['configs'] = profile_data.get('configs')
            profile['webhook_event'] = profile_data.get('webhook_event')
        else:
            profile['inputs'] = profile_data.get('inputs')

        if profile_data.get('output_variables'):
            # add a list of output variable for the current permutation
            profile['permutation_output_variables'] = profile_data.get('output_variables')

        if profile_data.get('runtime_level').lower() == 'organization':
            profile['validation_criteria'] = profile_data.get('validation_criteria', {'percent': 5})
            profile.pop('outputs')

        with open(profile_filename, 'w') as fh:
            json.dump(profile, fh, indent=2, sort_keys=sort_keys)

    def delete(self, profile_name):
        """Delete an existing profile."""
        raise NotImplementedError('The delete method is not currently implemented.')

    def update(self, profile_name):
        """Update an existing profile."""
        raise NotImplementedError('The update method is not currently implemented.')


class TestProfileTemplates:
    """TestProfile Template Class"""

    def __init__(self, base_dir, branch='master'):
        """Initialize class properties."""
        self.branch = branch
        self.base_dir = base_dir

        # map of app_type to class
        self.app_type_to_class = {
            'organization': 'TestCaseJob',
            'playbook': 'TestCasePlaybook',
            'triggerservice': 'TestCaseTriggerService',
            'webhooktriggerservice': 'TestCaseWebhookTriggerService',
        }

    def render_template(self, feature, app_type):
        """Render the templates and write to disk conditionally."""
        variables = {'app_type': app_type, 'class_name': self.app_type_to_class.get(app_type)}

        test_profiles_file = os.path.join(self.base_dir, feature, 'test_profiles.py')
        template = Template(self.test_profiles_template)
        rendered_template = template.render(**variables)
        with open(test_profiles_file, 'w') as f:
            f.write(rendered_template)

    @property
    def test_profiles_template(self):
        """Return template file"""
        url = f"{BASE_URL}/{self.branch}/app_init/tests/{'test_profiles.py.tpl'}"
        r = requests.get(url, allow_redirects=True)
        if not r.ok:
            raise RuntimeError('Could not download template file.')
        return r.content


class ValidationTemplates:
    """Validation Template Class

    Raises:
        NotImplementedError: The delete method is not currently implemented.
        NotImplementedError: The update method is not currently implemented.
    """

    def __init__(self, base_dir, branch='master'):
        """Initialize class properties."""
        self.branch = branch
        self.base_dir = base_dir
        self._variable_match = re.compile(fr'^{self._variable_pattern}$')
        self._variable_parse = re.compile(self._variable_pattern)

    def _method_name(self, variable):
        """Convert variable name to a valid method name.

        Args:
            variable (string): The variable name to convert.

        Returns:
            (str): Method name
        """
        method_name = None
        if variable is not None:
            variable = variable.strip()
            if re.match(self._variable_match, variable):
                var = re.search(self._variable_parse, variable)
                variable_name = var.group(3).replace('.', '_').lower()
                variable_type = var.group(4).lower()
                method_name = f'{variable_name}_{variable_type}'
        return method_name

    @property
    def _variable_pattern(self):
        """Regex pattern to match and parse a playbook variable."""
        variable_pattern = r'#([A-Za-z]+)'  # match literal (#App) at beginning of String
        variable_pattern += r':([\d]+)'  # app id (:7979)
        variable_pattern += r':([A-Za-z0-9_\.\-\[\]]+)'  # variable name (:variable_name)
        variable_pattern += r'!(StringArray|BinaryArray|KeyValueArray'  # variable type (array)
        variable_pattern += r'|TCEntityArray|TCEnhancedEntityArray'  # variable type (array)
        variable_pattern += r'|String|Binary|KeyValue|TCEntity|TCEnhancedEntity'  # variable type
        variable_pattern += r'|(?:(?!String)(?!Binary)(?!KeyValue)'  # non matching for custom
        variable_pattern += r'(?!TCEntity)(?!TCEnhancedEntity)'  # non matching for custom
        variable_pattern += r'[A-Za-z0-9_-]+))'  # variable type (custom)
        return variable_pattern

    @property
    def custom_template(self):
        """Return template file"""
        url = f"{BASE_URL}/{self.branch}/app_init/tests/{'validate_custom.py.tpl'}"
        r = requests.get(url, allow_redirects=True)
        if not r.ok:
            raise RuntimeError('Could not download template file.')
        return r.content

    @property
    def feature_template(self):
        """Return template file"""
        url = f"{BASE_URL}/{self.branch}/app_init/tests/{'validate_feature.py.tpl'}"
        r = requests.get(url, allow_redirects=True)
        if not r.ok:
            raise RuntimeError('Could not download template file.')
        return r.content

    def output_data(self, output_variables):
        """Return formatted output data.

        #App:9876:http.content!Binary
        """
        output_data = []
        for ov in output_variables:
            output_data.append({'method': self._method_name(ov), 'variable': ov})
        return sorted(output_data, key=lambda i: i['method'])

    @property
    def parent_template(self):
        """Return template file"""
        url = f"{BASE_URL}/{self.branch}/app_init/tests/{'validate.py.tpl'}"
        r = requests.get(url, allow_redirects=True)
        if not r.ok:
            raise RuntimeError('Could not download template file.')
        return r.content

    def render_templates(self, feature, app_type, output_variables):
        """Render the templates and write to disk conditionally."""
        variables = {
            'app_type': app_type,
            'feature': feature,
            'output_data': self.output_data(output_variables),
        }

        parent_file = os.path.join(self.base_dir, 'validate.py')
        template = Template(self.parent_template)
        rendered_template = template.render(**variables)
        with open(parent_file, 'w') as f:
            f.write(rendered_template)

        custom_file = os.path.join(self.base_dir, 'validate_custom.py')
        if not os.path.isfile(custom_file):
            template = Template(self.custom_template)
            rendered_template = template.render(**variables)
            with open(custom_file, 'w') as f:
                f.write(rendered_template)

        feature_file = os.path.join(self.base_dir, feature, 'validate_feature.py')
        if not os.path.isfile(feature_file):
            template = Template(self.feature_template)
            rendered_template = template.render(**variables)
            with open(feature_file, 'w') as f:
                f.write(rendered_template)


class Test(Bin):
    """Create profiles for ThreatConnect Job or Playbook App.

    Args:
        _args (namespace): The argparser args Namespace.
    """

    def __init__(self, _args):
        """Initialize Class properties.

        Args:
            _args (namespace): The argparser args Namespace.
        """

        super().__init__(_args)

        # properties
        if not self.args.permutations:
            self._output_variables = None

            self.base_dir = os.path.join(self.app_path, 'tests')
            self.feature_dir = os.path.join(self.base_dir, self.args.feature)
            self.feature_profile_dir = os.path.join(self.base_dir, self.args.feature, 'profiles.d')

            self.custom_templates = CustomTemplates(self.base_dir, self.args.branch)
            self.profiles = Profiles(self.profiles_dir)
            self.test_profile_template = TestProfileTemplates(self.base_dir, self.args.branch)
            self.validation_templates = ValidationTemplates(self.base_dir, self.args.branch)

    @staticmethod
    def _print_results(file, status):
        """Print the download results.

        Args:
            file (str): The filename.
            status (str): The file download status.
        """

        file_color = c.Fore.GREEN
        status_color = c.Fore.RED
        if status == 'Success':
            status_color = c.Fore.GREEN
        elif status == 'Skipped':
            status_color = c.Fore.YELLOW
        print(
            f"{c.Fore.CYAN}{'Downloading:'!s:<13}{file_color}{file!s:<50}\n"
            f"{c.Fore.CYAN}{'Status:'!s:<13}{status_color}{status}"
        )

    def add_profile(self):
        """Add the desired profile"""
        sort_keys = True
        if self.args.profile_file:
            sort_keys = False
            data = []
            profile_file = os.path.join(self.app_path, 'tcex.d', 'profiles', self.args.profile_file)
            if os.path.isfile(self.args.profile_file):
                with open(self.args.profile_file, 'r') as fh:
                    data = json.load(fh)
            elif os.path.isfile(profile_file):
                with open(profile_file, 'r') as fh:
                    data = json.load(fh)
            else:
                self.handle_error(f'Error reading in profile file: {self.args.profile_file}', True)

            profile_data = {}
            for d in data:
                profile_data[d.get('profile_name')] = {
                    'exit_codes': d.get('exit_codes'),
                    'inputs': d.get('args', {}).get('app'),
                    'runtime_level': self.ij.runtime_level,
                    'stage': {'redis': self.add_profile_staging(d.get('data_files', []))},
                }

        elif self.args.permutation_id is not None:
            profile_data = {
                self.args.profile_name: {
                    'inputs': {
                        'optional': self.profile_settings_args_layout_json(False),
                        'required': self.profile_settings_args_layout_json(True),
                    },
                    'output_variables': self._output_permutations[self.args.permutation_id],
                    'runtime_level': self.ij.runtime_level,
                }
            }
        elif self.ij.runtime_level.lower() == 'triggerservice':
            profile_data = {
                self.args.profile_name: {
                    'configs': [
                        {
                            'trigger_id': str(randint(1000, 9999)),
                            'config': self.ij.params_to_args(service_config=False),
                        }
                    ],
                    'runtime_level': self.ij.runtime_level,
                    'trigger': {},
                }
            }
        elif self.ij.runtime_level.lower() == 'webhooktriggerservice':
            profile_data = {
                self.args.profile_name: {
                    'configs': [
                        {
                            'trigger_id': str(randint(1000, 9999)),
                            'config': self.ij.params_to_args(service_config=False),
                        }
                    ],
                    'runtime_level': self.ij.runtime_level,
                    'webhook_event': {
                        'body': '',
                        'headers': [],
                        'method': 'GET',
                        'query_params': [],
                        'trigger_id': '',
                    },
                }
            }
        else:
            profile_data = {
                self.args.profile_name: {
                    'inputs': {
                        'optional': self.ij.params_to_args(required=False),
                        'required': self.ij.params_to_args(required=True),
                    },
                    'runtime_level': self.ij.runtime_level,
                }
            }

        # add profiles
        for profile_name, data in profile_data.items():
            self.profiles.add(profile_name, data, sort_keys=sort_keys)

    @staticmethod
    def add_profile_staging(staging_files):
        """Get existing staging data."""
        staging_data = {}
        for sf in staging_files:
            with open(sf, 'r') as fh:
                data = json.load(fh)
            for d in data:
                staging_data[d.get('variable')] = d.get('data')
        return staging_data

    def create_dirs(self):
        """Create tcex.d directory and sub directories."""
        for d in [self.base_dir, self.feature_dir, self.feature_profile_dir]:
            if not os.path.isdir(d):
                os.makedirs(d)

        # create __init__ files
        self.create_dirs_init()

    def create_dirs_init(self):
        """Create the __init__.py file under dir."""
        for d in [self.base_dir, self.feature_dir]:
            if os.path.isdir(d):
                with open(os.path.join(d, '__init__.py'), 'a'):
                    os.utime(os.path.join(d, '__init__.py'), None)

    def download_file(self, remote_filename):
        """Download file from github.

        Args:
            remote_filename (str): The name of the file as defined in git repository.
        """
        # TODO: can this method be merged with tcex_bin_init download_file?
        status = 'Failed'
        local_filename = self.test_file
        if not os.path.isfile(local_filename):
            url = f'{BASE_URL}/{self.args.branch}/app_init/tests/{remote_filename}'
            r = requests.get(url, allow_redirects=True)
            if r.ok:
                open(local_filename, 'wb').write(r.content)
                status = 'Success'
            else:
                self.handle_error(f'Error requesting: {url}', False)

            # print download status
            self._print_results(local_filename, status)

    def download_conftest(self):
        """Download conftest.py file from github."""
        # TODO: combine all download methods
        status = 'Failed'
        local_filename = os.path.join('tests', 'conftest.py')
        if not os.path.isfile(local_filename):
            url = f"{BASE_URL}/{self.args.branch}/app_init/tests/{'conftest.py'}"
            r = requests.get(url, allow_redirects=True)
            if r.ok:
                open(local_filename, 'wb').write(r.content)
                status = 'Success'
            else:
                self.handle_error(f'Error requesting: {url}', False)

            # print download status
            self._print_results(local_filename, status)

    def download_profile(self):
        """Download conftest.py file from github."""
        # TODO: combine all download methods
        status = 'Failed'
        local_filename = os.path.join('tests', 'profiles.py')

        url = f"{BASE_URL}/{self.args.branch}/app_init/tests/{'profiles.py'}"
        r = requests.get(url, allow_redirects=True)
        if r.ok:
            open(local_filename, 'wb').write(r.content)
            status = 'Success'
        else:
            self.handle_error(f'Error requesting: {url}', False)

        # print download status
        self._print_results(local_filename, status)

    def generate_custom_files(self):
        """Generate the custom.py and custom_feature.py files."""
        self.custom_templates.render_templates(self.args.feature, self.ij.runtime_level.lower())

    def generate_test_profile_file(self):
        """Generate the test_profiles.py file."""
        self.test_profile_template.render_template(self.args.feature, self.ij.runtime_level.lower())

    def generate_validation_files(self):
        """Generate the validation.py and validation_feature.py files."""
        self.validation_templates.render_templates(
            self.args.feature, self.ij.runtime_level.lower(), self.output_variables
        )

    @property
    def output_variables(self):
        """Return playbook output variables"""
        if self._output_variables is None:
            self._output_variables = []
            # Currently there is no support for projects with multiple install.json files.
            for p in self.ij.playbook.get('outputVariables') or []:
                var_type = 'App'
                if self.ij.runtime_level.lower() in ['triggerservice', 'webhooktriggerservice']:
                    var_type = 'Trigger'
                # "#App:9876:app.data.count!String"
                # "#Trigger:9876:app.data.count!String"
                self._output_variables.append(f"#{var_type}:{9876}:{p.get('name')}!{p.get('type')}")
        return self._output_variables

    @property
    def permutations_file(self):
        """Return permutations fully qualified filename."""
        return os.path.join(self.base_dir, 'permutations.json')

    def permutation_file_exists(self):
        """Check to see if the permutations file exists"""
        return os.path.isfile(self.permutations_file)

    @property
    def profiles_dir(self):
        """Return profile fully qualified filename."""
        return os.path.join(self.base_dir, self.args.feature, 'profiles.d')

    @property
    def test_file(self):
        """Return generate test filename."""
        test_file = None
        if self.args.file:
            # TODO: add comment on what this does
            if not self.args.file.startswith('test_'):
                self.args.file = 'test_' + self.args.file
            if not self.args.file.endswith('.py'):
                self.args.file = self.args.file + '.py'
            test_file = os.path.join(self.base_dir, self.args.feature, self.args.file)

        return test_file

    @property
    def validation_base_file(self):
        """Return validations fully qualified filename."""
        return os.path.join(self.base_dir, 'validation_base.py')

    @property
    def validation_file(self):
        """Return validations fully qualified filename."""
        return os.path.join(self.base_dir, self.args.feature, 'validation.py')
