#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework Profile Generation Module."""
import json
import os
import re

from mako.template import Template
import requests
import colorama as c

from .tcex_bin import TcExBin

BASE_URL = 'https://raw.githubusercontent.com/ThreatConnect-Inc/tcex'


class Profiles:
    """Profile Class

    Args:
        filename (str): The filename for the profile data.

    Raises:
        NotImplementedError: The delete method is not currently implemented.
        NotImplementedError: The update method is not currently implemented.
    """

    def __init__(self, filename):
        """Initialize class properties."""
        self.filename = filename

        # properties
        self._profiles = None

    def add(self, profile_name, inputs, outputs=None, stage=None, sort_keys=True):
        """Add a profile."""
        if not self.exists(profile_name):
            profile = {
                'exit_codes': [0],
                'inputs': inputs,
                'outputs': outputs,
                'stage': stage or {'redis': {}, 'threatconnect': {}},
            }

            self.profiles[profile_name] = profile

            with open(self.filename, 'w') as fh:
                json.dump(self.profiles, fh, indent=2, sort_keys=sort_keys)

    def delete(self, profile_name):
        """Delete an existing profile."""
        raise NotImplementedError('The delete method is not currently implemented.')

    def exists(self, profile_name):
        """Check to see if the profile exists."""
        return profile_name in self.profiles

    @property
    def file_exists(self):
        """Check to see if the profile file exists."""
        return os.path.isfile(self.filename)

    @property
    def profiles(self):
        """Return the profile data."""
        if self._profiles is None:
            if not self.file_exists:
                self._profiles = {}
                with open(self.filename, 'w') as fh:
                    json.dump(self._profiles, fh)
            else:
                with open(self.filename, 'r') as fh:
                    self._profiles = json.load(fh)
        return self._profiles

    def update(self, profile_name):
        """Update an existing profile."""
        raise NotImplementedError('The update method is not currently implemented.')


class Validation:
    """Validation Class

    Args:
        filename (str): The filename for the validation data.

    Raises:
        NotImplementedError: The delete method is not currently implemented.
        NotImplementedError: The update method is not currently implemented.
    """

    def __init__(self, base_dir, branch='master'):
        """Initialize class properties."""
        self.branch = branch
        self.base_dir = base_dir
        self.validation_file = (base_dir, 'validation.py')
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
        if not os.path.isfile(self.validation_file):
            template = Template(self.validation_template)
            template_data = {'output_data': self.output_data(output_variables)}
            rendered_template = template.render(**template_data)
            with open(self.validation_file, 'a') as f:
                f.write(rendered_template)

    def generate_feature(self, feature, file_):
        """If not currently exist, generates the validation file."""
        validation_file = (self.base_dir, feature, 'validation_feature.py')
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
        url = '{}/{}/app_init/tests/{}'.format(BASE_URL, self.branch, 'validation.py.tpl')
        r = requests.get(url, allow_redirects=True)
        if not r.ok:
            raise RuntimeError('Could not download template file.')
        return r.content

    @property
    def validation_feature_template(self):
        """Return template file"""
        url = '{}/{}/app_init/tests/{}'.format(BASE_URL, self.branch, 'validation_feature.py.tpl')
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
        self.base_dir = os.path.join(self.app_path, 'tests')
        self.feature_dir = os.path.join(self.base_dir, self.args.feature)
        self.profiles = Profiles(self.profiles_file)
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
            '{}{!s:<13}{}{!s:<35}{}{!s:<8}{}{}'.format(
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
            if os.path.isfile(self.args.profile_file):
                with open(self.args.profile_file, 'r') as fh:
                    data = json.load(fh)

            profile_data = {}
            for d in data:
                profile_data[d.get('profile_name')] = {
                    'inputs': d.get('args', {}).get('app'),
                    'stage': self.add_profile_staging(d.get('data_files')),
                }

        elif self.args.permutation_id:
            # TODO: fix the profile_settings_args_layout_json to not run permutations twice
            profile_data = {
                self.args.profile_name: {
                    'inputs': {
                        'optional': self.profile_settings_args_layout_json(False),
                        'required': self.profile_settings_args_layout_json(True),
                    }
                }
            }
        else:
            profile_data = {
                self.args.profile_name: {
                    'inputs': {
                        'optional': self.profile_settings_args_install_json(
                            self.install_json, False
                        ),
                        'required': self.profile_settings_args_install_json(
                            self.install_json, True
                        ),
                    }
                }
            }

        # add profiles
        for profile_name, data in profile_data.items():
            self.profiles.add(
                profile_name, data.get('inputs'), stage=data.get('stage'), sort_keys=sort_keys
            )

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
        for d in [self.base_dir, self.feature_dir]:
            if not os.path.isdir(d):
                os.makedirs(d)
                self.generate_init(d)

    def download_file(self, remote_filename):
        """Download file from github.

        Args:
            remote_filename (str): The name of the file as defined in git repository.
            local_filename (str, optional): Defaults to None. The name of the file as it should be
                be written to local filesystem.
        """
        # TODO: can this method be merged with tcex_bin_init download_file?
        status = 'Failed'
        local_filename = self.test_file
        if os.path.isfile(local_filename):
            self.handle_error(
                'Error downloading file: {}. File already exists'.format(local_filename), False
            )
            return

        url = '{}/{}/app_init/tests/{}'.format(BASE_URL, self.args.branch, remote_filename)
        r = requests.get(url, allow_redirects=True)
        if r.ok:
            open(local_filename, 'wb').write(r.content)
            status = 'Success'
        else:
            self.handle_error('Error requesting: {}'.format(url), False)

        # print download status
        self._print_results(local_filename, status)

    @staticmethod
    def generate_init(directory):
        """Create the __init__.py file under dir."""
        with open(os.path.join(directory, '__init__.py'), 'a'):
            os.utime(os.path.join(directory, '__init__.py'), None)

    def generate_validation_file(self):
        """Generate the validation file."""
        self.validation.generate(self.output_variables)
        self.validation.generate_feature(self.args.feature, self.args.file)

    @property
    def output_variables(self):
        """Return playbook output variables"""
        if self._output_variables is None:
            self._output_variables = []
            # Currently there is no support for projects with multiple install.json files.
            for p in self.install_json.get('playbook', {}).get('outputVariables') or []:
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
    def profiles_file(self):
        """Return profile fully qualified filename."""
        return os.path.join(self.base_dir, self.args.feature, 'profiles.json')

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
