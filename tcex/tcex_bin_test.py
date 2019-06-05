#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework Profile Generation Module."""
import json
import os
import pprint

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
        self.base_dir = 'tests'
        self.feature_dir = os.path.join(self.base_dir, self.args.feature)
        self.profile_file = os.path.join(self.base_dir, self.args.feature, 'profiles.json')
        self.validation_file = os.path.join(self.base_dir, self.args.feature, 'validation.py')
        self.test_file = os.path.join(self.base_dir, self.args.feature, self.args.file)
        self.profiles = {}
        self._app_path = os.getcwd()
        self._current_test = None
        self._output_variables = None
        self._input_params = None
        self._install_json = None

    def _create_dirs(self):
        """Create tcex.d directory and sub directories."""

        dirs = [self.base_dir, self.feature_dir]
        for d in dirs:
            if not os.path.isdir(d):
                os.makedirs(d)

        files = [self.profile_file, self.validation_file]
        for file in files:
            if not os.path.isfile(file):
                os.makedirs(file)

    def profile_file_exists(self):
        """Checks to see if the profile file exists"""
        if os.path.isfile(self.profile_file):
            return True
        return False

    def generate_profile(self):
        """If the profile file doesnt exist, it is created."""
        if not os.path.isfile(self.profile_file):
            with open(self.profile_file, 'a'):
                os.utime(self.profile_file, None)

    def permutation_file_exists(self):
        """Checks to see if the permutations file exists"""
        if os.path.isfile(self.args.permutation_file):
            return True
        return False

    def profile_exists(self):
        """Checks to see if the profile exists"""
        profile_data = self.profile_data
        if not profile_data:
            return False

        return self.args.profile_name in profile_data.keys()

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
            json.dump(profile_data, outfile)

    def update_profile(self, attribute, default=None, action='create'):
        """Updates the desired profile to create/delete input/output variables"""
        raise NotImplementedError('Not implemented at this moment, might be a nice to have')

    def get_permutation_by_id(self):
        """Gets the permutation dict based on id"""
        if not self.permutation_file_exists():
            return None

        permutation_data = None
        with open(self.args.permutation_file, 'r+') as permutation_file:
            data = json.load(permutation_file)
            for permutation in data.items():
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

        with open('tests/validation.py', 'a') as fh:
            fh.write('from tcex.testing import TestCasePlaybook\n')
            fh.write('\n\n')
            fh.write('class Validation(TestCasePlaybook):\n')
            fh.write('    """Validation for {}"""'.format(self._current_test))
            fh.write('\n\n')
            fh.write('    def validation(self):\n')
            variables = {}
            asserts = ''
            for variable in self.output_variables:
                # variable_type = self.playbook.variable_type(variable)
                # data = self.playbook.read(variable)
                #
                # clean/format String data
                # if data is not None:
                #     if variable_type == 'String':
                # data = '\'{}\''.format(data.replace('\n', '\\n'))
                # data = '{}'.format(data.replace('\n', '\\n'))
                # if len(data) >= max_len:
                #     data = self._split_string(data)

                variables[variable] = 'Dummy_data'

                # write output to file
                asserts += '        assert self.validator.redis.eq(\n'
                asserts += '            \'{}\',\n'.format(variable)
                asserts += '            output_variables.get(\'{}\', None)\n'.format(variable)
                asserts += '        )\n'
            fh.write(
                '        output_variables = {{\n {}\n        }}\n\n'.format(
                    pprint.pformat(variables, indent=12)[1:-1]
                )
            )
            fh.write(asserts)

    def update_validation(self, attribute, default=None, action='create'):
        """Updates the validation file to create/delete asserts"""
        raise NotImplementedError('Not implemented at this moment, might be a nice to have')

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
