#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework Profile Generation Module."""
import json
import os
import requests
import colorama as c

from .tcex_bin import TcExBin


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
        self._input_permutations = []
        self._output_permutations = []
        self._app_path = os.getcwd()
        self.base_dir = 'tests'
        self.feature_dir = os.path.join(self.base_dir, self.args.feature)
        self.profile_file = os.path.join(self.base_dir, self.args.feature, 'profiles.json')
        self.validation_file = os.path.join(self.base_dir, self.args.feature, 'validation.py')
        self.permutation_file = os.path.join(self._app_path, 'permutations.json')
        self.profiles = {}
        self._current_test = None
        self._output_variables = None
        self._input_params = None
        self._install_json = None
        self.base_url = (
            'https://raw.githubusercontent.com/ThreatConnect-Inc/tcex/{}/test_init/'
        ).format(self.args.branch)

        if not self.args.file.startswith('test_'):
            self.args.file = 'test_' + self.args.file
        if not self.args.file.endswith('.py'):
            self.args.file = self.args.file + '.py'

        self.test_file = os.path.join(self.base_dir, self.args.feature, self.args.file)

    def _create_dirs(self):
        """Create tcex.d directory and sub directories."""

        dirs = [self.base_dir, self.feature_dir]
        for d in dirs:
            if not os.path.isdir(d):
                os.makedirs(d)

    def profile_file_exists(self):
        """Checks to see if the profile file exists"""
        if os.path.isfile(self.profile_file):
            return True
        return False

    def generate_profile(self):
        """If the profile file doesnt exist, it is created."""
        if not os.path.isfile(self.profile_file):
            with open(self.profile_file, 'w') as profile_file:
                profile_file.write('{}')

    def permutation_file_exists(self):
        """Checks to see if the permutations file exists"""
        if os.path.isfile(self.permutation_file):
            return True
        return False

    def profile_exists(self):
        """Checks to see if the profile exists"""
        profile_data = self.profile_data
        if not profile_data:
            return False

        return self.args.profile_name in list(profile_data.keys())

    def delete_profile(self):
        """Deletes the desired profile"""
        raise NotImplementedError('Not implemented at this moment, might be a nice to have')

    def add_profile(self):
        """Adds the desired profile"""
        if self.profile_exists():
            return

        permutation = self.get_permutation_by_id()
        inputs = {}

        for arg in permutation.get('args', []):
            inputs[arg.get('name')] = arg.get('value', None)

        profile_data = self.profile_data
        profile = {'inputs': inputs, 'outputs': None, 'stage': {'redis': {}, 'threatconnect': {}}}

        profile_data[self.args.profile_name] = profile

        with open(self.profile_file, 'w') as outfile:
            json.dump(profile_data, outfile, indent=4)

    def update_profile(self, attribute, default=None, action='create'):
        """Updates the desired profile to create/delete input/output variables"""
        raise NotImplementedError('Not implemented at this moment, might be a nice to have')

    def get_permutation_by_id(self):
        """Gets the permutation dict based on id"""
        if not self.permutation_file_exists():
            return None

        permutation_data = None
        with open(self.permutation_file, 'r+') as permutation_file:
            data = json.load(permutation_file)
            for permutation in data:
                if permutation.get('index', None) == self.args.permutation_id:
                    permutation_data = permutation

        return permutation_data

    def validation_file_exists(self):
        """Checks if the validation file exists"""
        if os.path.isfile(self.validation_file):
            return True
        return False

    def generate_validation_file(self):
        """If not currently exist, generates the validation file."""
        if self.validation_file_exists():
            return

        with open(self.validation_file, 'a') as fh:
            fh.write('from tcex.testing import TestCasePlaybook\n\n\n')
            fh.write('class Validation(TestCasePlaybook):\n')
            fh.write(
                '    """Validation for Feature {}, File {}"""\n\n'.format(
                    self.args.feature, self.args.file
                )
            )
            fh.write('    def validation(self, output_variables):\n')
            asserts = ''
            for variable in self.output_variables:
                # write output to file
                asserts += '        if \'{}\' in output_variables.keys():\n'.format(variable)
                asserts += '            assert self.validator.redis.eq(\n'
                asserts += '                \'{}\',\n'.format(variable)
                asserts += '                output_variables.get(\'{}\', None)\n'.format(variable)
                asserts += '            )\n'
            fh.write(asserts)

    def update_validation(self, attribute, default=None, action='create'):
        """Updates the validation file to create/delete asserts"""
        raise NotImplementedError('Not implemented at this moment, might be a nice to have')

    def download_file(self, remote_filename):
        """Download file from github.

        Args:
            remote_filename (str): The name of the file as defined in git repository.
            local_filename (str, optional): Defaults to None. The name of the file as it should be
                be written to local filesystem.
        """
        status = 'Failed'
        local_filename = self.args.file
        if not local_filename.startswith('test_'):
            local_filename = 'test_' + local_filename

        url = '{}{}'.format(self.base_url, remote_filename)
        r = requests.get(url, allow_redirects=True)
        if r.ok:
            open(local_filename, 'wb').write(r.content)
            status = 'Success'
        else:
            self.handle_error('Error requesting: {}'.format(url), False)

        # print download status
        self._print_results(local_filename, status)

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

    @staticmethod
    def _confirm_overwrite(filename):
        """Confirm overwrite of template files.

        Make sure the user would like to continue downloading a file which will overwrite a file
        in the current directory.

        Args:
            filename (str): The name of the file to overwrite.

        Returns:
            bool: True if the user specifies a "yes" response.
        """

        message = '{}Would you like to overwrite the contents of {} (y/[n])? '.format(
            c.Fore.MAGENTA, filename
        )
        # 2to3 fixes this for py3
        response = raw_input(message)  # noqa: F821, pylint: disable=E0602
        response = response.lower()

        if response in ['y', 'yes']:
            return True
        return False

    @property
    def profile_data(self):
        """The profile data"""
        if not self.profile_file_exists():
            return None
        data = None
        with open(self.profile_file, 'r+') as profile_file:
            data = json.load(profile_file)
        return data

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
    def install_json(self):
        """Return install.json contents."""
        file_fqpn = os.path.join(self._app_path, 'install.json')
        if self._install_json is None:
            if os.path.isfile(file_fqpn):
                with open(file_fqpn, 'r') as fh:
                    self._install_json = json.load(fh)
            else:
                print(('File "{}" could not be found.'.format(file_fqpn)))
        return self._install_json
