#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework Profile Generation Module."""
import json
import os
import re
import sys
from random import randint

try:
    from mako.template import Template
except ImportError:
    pass  # mako is only required for local testing
import requests
import colorama as c

from .tcex_bin import TcExBin

BASE_URL = 'https://raw.githubusercontent.com/ThreatConnect-Inc/tcex'


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
        profile_filename = os.path.join(self.profile_dir, '{}.json'.format(profile_name))
        if os.path.isfile(profile_filename):
            print(
                '{}{}A profile with the name ({}) already exists.'.format(
                    c.Style.BRIGHT, c.Fore.RED, profile_name
                )
            )
            sys.exit(1)

        profile = {
            'exit_codes': profile_data.get('exit_codes', [0]),
            'outputs': profile_data.get('outputs'),
            'stage': profile_data.get('stage', {'redis': {}, 'threatconnect': {}}),
        }
        if profile_data.get('runtime_level').lower() == 'triggerservice':
            profile['configs'] = profile_data.get('configs')
            profile['trigger'] = profile_data.get('trigger')
        else:
            profile['inputs'] = profile_data.get('inputs')

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


class Validation:
    """Validation Class

    Raises:
        NotImplementedError: The delete method is not currently implemented.
        NotImplementedError: The update method is not currently implemented.
    """

    def __init__(self, base_dir, branch='master'):
        """Initialize class properties."""
        self.branch = branch
        self.base_dir = base_dir
        self._variable_match = re.compile(r'^{}$'.format(self._variable_pattern))
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
                method_name = '{}_{}'.format(variable_name, variable_type)
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

    def generate(self, output_variables):
        """If not currently exist, generates the validation file."""
        validation_file = os.path.join(self.base_dir, 'validate.py')
        if not os.path.isfile(validation_file):
            template = Template(self.validation_template)
            output_data = self.output_data(output_variables)
            template_data = {'output_data': output_data}
            rendered_template = template.render(**template_data)
            with open(validation_file, 'a') as f:
                f.write(rendered_template)

    def generate_test_template(self, variables, feature, file_):
        """If not currently exist, generates the test file file."""
        validation_file = os.path.join(self.base_dir, feature, file_)
        if not os.path.isfile(validation_file):
            template = Template(self.test_template)
            rendered_template = template.render(**variables)
            with open(validation_file, 'a') as f:
                f.write(rendered_template)

    def generate_feature(self, feature, file_):
        """If not currently exist, generates the validation file."""
        validation_file = os.path.join(self.base_dir, feature, 'validate_feature.py')
        if not os.path.isfile(validation_file):
            template = Template(self.validation_feature_template)
            template_data = {'feature': feature, 'file': file_}
            rendered_template = template.render(**template_data)
            with open(validation_file, 'a') as f:
                f.write(rendered_template)

    def output_data(self, output_variables):
        """Return formatted output data.

        #App:9876:http.content!Binary
        """
        output_data = []
        for ov in output_variables:
            output_data.append({'method': self._method_name(ov), 'variable': ov})
        return output_data

    @property
    def validation_template(self):
        """Return template file"""
        url = '{}/{}/app_init/tests/{}'.format(BASE_URL, self.branch, 'validate.py.tpl')
        r = requests.get(url, allow_redirects=True)
        if not r.ok:
            raise RuntimeError('Could not download template file.')
        return r.content

    @property
    def validation_feature_template(self):
        """Return template file"""
        url = '{}/{}/app_init/tests/{}'.format(BASE_URL, self.branch, 'validate_feature.py.tpl')
        r = requests.get(url, allow_redirects=True)
        if not r.ok:
            raise RuntimeError('Could not download template file.')
        return r.content

    @property
    def test_template(self):
        """Return template file"""
        url = '{}/{}/app_init/tests/{}'.format(BASE_URL, self.branch, 'test_template.py.tpl')
        r = requests.get(url, allow_redirects=True)
        if not r.ok:
            raise RuntimeError('Could not download template file.')
        return r.content


class TcExTest(TcExBin):
    """Create profiles for ThreatConnect Job or Playbook App.

    Args:
        _args (namespace): The argparser args Namespace.
    """

    def __init__(self, _args):
        """Initialize Class properties.

        Args:
            _args (namespace): The argparser args Namespace.
        """

        super(TcExTest, self).__init__(_args)

        # properties
        if not self.args.permutations:
            self.base_dir = os.path.join(self.app_path, 'tests')
            self.feature_dir = os.path.join(self.base_dir, self.args.feature)
            self.feature_profile_dir = os.path.join(self.base_dir, self.args.feature, 'profiles.d')
            self.profiles = Profiles(self.profiles_dir)
            self.validation = Validation(self.base_dir, self.args.branch)
            self._output_variables = None

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
            '{}{!s:<13}{}{!s:<50}\n{}{!s:<13}{}{}'.format(
                c.Fore.CYAN,
                'Downloading:',
                file_color,
                file,
                c.Fore.CYAN,
                'Status:',
                status_color,
                status,
            )
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
                self.handle_error(
                    'Error reading in profile file: {}'.format(self.args.profile_file), True
                )

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
                    'runtime_level': self.ij.runtime_level,
                }
            }
        elif self.ij.runtime_level.lower() == 'triggerservice':
            profile_data = {
                self.args.profile_name: {
                    'configs': [
                        {
                            'config_id': str(randint(1000, 9999)),
                            'config': self.ij.params_to_args(service_config=False),
                        }
                    ],
                    'runtime_level': self.ij.runtime_level,
                    'trigger': {},
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
            url = '{}/{}/app_init/tests/{}'.format(BASE_URL, self.args.branch, remote_filename)
            r = requests.get(url, allow_redirects=True)
            if r.ok:
                open(local_filename, 'wb').write(r.content)
                status = 'Success'
            else:
                self.handle_error('Error requesting: {}'.format(url), False)

            # print download status
            self._print_results(local_filename, status)

    def download_conftest(self):
        """Download conftest.py file from github."""
        # TODO: combine all download methods
        status = 'Failed'
        local_filename = os.path.join('tests', 'conftest.py')
        if not os.path.isfile(local_filename):
            url = '{}/{}/app_init/tests/{}'.format(BASE_URL, self.args.branch, 'conftest.py')
            r = requests.get(url, allow_redirects=True)
            if r.ok:
                open(local_filename, 'wb').write(r.content)
                status = 'Success'
            else:
                self.handle_error('Error requesting: {}'.format(url), False)

            # print download status
            self._print_results(local_filename, status)

    def download_profile(self):
        """Download conftest.py file from github."""
        # TODO: combine all download methods
        status = 'Failed'
        local_filename = os.path.join('tests', 'profiles.py')
        if not os.path.isfile(local_filename):
            url = '{}/{}/app_init/tests/{}'.format(BASE_URL, self.args.branch, 'profiles.py')
            r = requests.get(url, allow_redirects=True)
            if r.ok:
                open(local_filename, 'wb').write(r.content)
                status = 'Success'
            else:
                self.handle_error('Error requesting: {}'.format(url), False)

            # print download status
            self._print_results(local_filename, status)

    def generate_validation_file(self):
        """Generate the validation file."""
        self.validation.generate(self.output_variables)
        self.validation.generate_feature(self.args.feature, self.args.file)

        test_template_variables = {
            'validate_batch_method': '',
            'parent_class': 'TestCasePlaybook',
            'parent_import': 'from tcex.testing import TestCasePlaybook',
        }
        if self.ij.runtime_level.lower() == 'organization':
            # TODO: remove this after validating
            # test_template_variables = {
            #     'validate_batch_method': 'self.validator.threatconnect.batch('
            #     'self.context, '
            #     'pd.get(\'owner\'),'
            #     'pd.get(\'validation_criteria\', {})'
            #     ')',
            #     'parent_class': 'TestCaseJob',
            #     'parent_import': 'from tcex.testing import TestCaseJob',
            # }
            test_template_variables = {
                'validate_batch_method': (
                    'self.validator.threatconnect.batch(self.context, pd.get(\'owner\'),'
                    'pd.get(\'validation_criteria\', {}))'
                ),
                'parent_class': 'TestCaseJob',
                'parent_import': 'from tcex.testing import TestCaseJob',
            }
        self.validation.generate_test_template(
            test_template_variables, self.args.feature, self.test_file
        )

    @property
    def output_variables(self):
        """Return playbook output variables"""
        if self._output_variables is None:
            self._output_variables = []
            # Currently there is no support for projects with multiple install.json files.
            for p in self.ij.playbook.get('outputVariables') or []:
                # "#App:9876:app.data.count!String"
                self._output_variables.append(
                    '#App:{}:{}!{}'.format(9876, p.get('name'), p.get('type'))
                )
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
