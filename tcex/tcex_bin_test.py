#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework Profile Generation Module."""
import json
import os
import sys
import requests
import colorama as c

from .tcex_bin import TcExBin

try:
    import sqlite3
except ModuleNotFoundError:
    # this module is only required for certain CLI commands
    pass


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
        self.base_dir = os.path.join(self._app_path, 'tests')
        self.feature_dir = os.path.join(self.base_dir, self.args.feature)
        self.profile_file = os.path.join(self.base_dir, self.args.feature, 'profiles.json')
        self.validation_file = os.path.join(self.base_dir, self.args.feature, 'validation.py')
        self.permutation_file = os.path.join(self.base_dir, 'permutations.json')
        self.profiles = {}
        self._current_test = None
        self._output_variables = None
        self._input_params = None
        self._install_json = None
        self.test_file = None
        self.base_url = (
            'https://raw.githubusercontent.com/ThreatConnect-Inc/tcex/{}/test_init/'
        ).format(self.args.branch)

        if self.args.file:
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
                self.generate_init(d)

    @staticmethod
    def generate_init(directory):
        """Creates the __init__.py file under dir """
        with open(os.path.join(directory, '__init__.py'), 'a'):
            os.utime(os.path.join(directory, '__init__.py'), None)

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
        if not self.args.permutation_id:
            return

        if self.profile_exists():
            return

        inputs = self.get_inputs_by_id()

        profile_data = self.profile_data
        profile = {'inputs': inputs, 'outputs': None, 'stage': {'redis': {}, 'threatconnect': {}}}

        profile_data[self.args.profile_name] = profile

        with open(self.profile_file, 'w') as outfile:
            json.dump(profile_data, outfile, indent=4)

    def update_profile(self, attribute, default=None, action='create'):
        """Updates the desired profile to create/delete input/output variables"""
        raise NotImplementedError('Not implemented at this moment, might be a nice to have')

    def get_inputs_by_id(self):
        """Return args based on layout.json and conditional rendering.

                Args:
                    required (bool): If True only required args will be returned.

                Returns:
                    dict: Dictionary of required or optional App args.
                """

        inputs = {'required': {}, 'optional': {}}
        self.db_create_table(self.input_table, list(self.install_json_params().keys()))
        self.db_insert_record(self.input_table, list(self.install_json_params().keys()))
        self.gen_permutations()
        try:
            for pn in self._input_permutations[self.args.permutation_id]:
                p = self.install_json_params().get(pn.get('name'))
                argument = p.get('name')
                value = ''
                if p.get('type').lower() == 'boolean' or p.get('type').lower() == 'choice':
                    value = pn.get('value')
                elif p.get('name') in ['api_access_id', 'api_secret_key']:
                    # leave these parameters set to the value defined in defaults
                    pass
                else:
                    # add type stub for values
                    types = '|'.join(p.get('playbookDataType', []))
                    value = p.get('default', '')
                    if types:
                        value = '<{}>'.format(types)
                if p.get('required', False):
                    inputs['required'][argument] = value
                else:
                    inputs['optional'][argument] = value
        except IndexError:
            self.handle_error('Invalid permutation index provided.')
        return inputs

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
                asserts += (
                    '            output_variable_data = output_variables.get('
                    '\'{}\')\n'.format(variable)
                )
                asserts += '            assert self.validator.redis.data(\n'
                asserts += '                \'{}\',\n'.format(variable)
                asserts += '                output_variable_data.get(\'expected_output\', None),\n'
                asserts += '                output_variable_data.get(\'op\', \'=\'),\n'
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
        local_filename = self.test_file
        if os.path.isfile(local_filename):
            self.handle_error(
                'Error downloading file: {}. File already exists'.format(local_filename), False
            )
            return
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
            (
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
        response = eval(input(message))  # noqa: F821, pylint: disable=E0602, W0123
        response = response.lower()

        if response in ['y', 'yes']:
            return True
        return False

    def permutations(self):
        """Process layout.json names/display to get all permutations of args."""
        if 'sqlite3' not in sys.modules:
            print('The sqlite3 module needs to be build-in to Python for this feature.')
            sys.exit(1)

        self.db_create_table(self.input_table, list(self.install_json_params().keys()))
        self.db_insert_record(self.input_table, list(self.install_json_params().keys()))
        self.gen_permutations()
        self.print_permutations()

    def gen_permutations(self, index=0, args=None):
        """Iterate recursively over layout.json parameter names.

        Args:
            index (int, optional): The current index position in the layout names list.
            args (list, optional): Defaults to None. The current list of args.
        """
        if args is None:
            args = []
        try:
            name = self.layout_json_names[index]
            display = self.layout_json_params.get(name, {}).get('display')
            input_type = self.install_json_params().get(name, {}).get('type')
            if self.validate_layout_display(self.input_table, display):
                if input_type.lower() == 'boolean':
                    for val in [True, False]:
                        args.append({'name': name, 'value': val})
                        self.db_update_record(self.input_table, name, val)
                        self.gen_permutations(index + 1, list(args))
                        # remove the previous arg before next iteration
                        args.pop()
                elif input_type.lower() == 'choice':
                    valid_values = self.expand_valid_values(
                        self.install_json_params().get(name, {}).get('validValues', [])
                    )
                    for val in valid_values:
                        args.append({'name': name, 'value': val})
                        self.db_update_record(self.input_table, name, val)
                        self.gen_permutations(index + 1, list(args))
                        # remove the previous arg before next iteration
                        args.pop()
                else:
                    args.append({'name': name, 'value': None})
                    self.gen_permutations(index + 1, list(args))
            else:
                self.gen_permutations(index + 1, list(args))

        except IndexError:
            # when IndexError is reached all data has been processed.
            self._input_permutations.append(args)
            outputs = []

            for o_name in self.install_json_output_variables():
                if self.layout_json_outputs.get(o_name) is not None:
                    display = self.layout_json_outputs.get(o_name, {}).get('display')
                    valid = self.validate_layout_display(self.input_table, display)
                    if display is None or not valid:
                        continue
                for ov in self.install_json_output_variables().get(o_name):
                    outputs.append(ov)
            self._output_permutations.append(outputs)

    def validate_layout_display(self, table, display_condition):
        """Check to see if the display condition passes.

        Args:
            table (str): The name of the DB table which hold the App data.
            display_condition (str): The "where" clause of the DB SQL statement.

        Returns:
            bool: True if the row count is greater than 0.
        """
        display = False
        if display_condition is None:
            display = True
        else:
            display_query = 'select count(*) from {} where {}'.format(table, display_condition)
            try:
                cur = self.db_conn.cursor()
                cur.execute(display_query.replace('"', ''))
                rows = cur.fetchall()
                if rows[0][0] > 0:
                    display = True
            except sqlite3.Error as e:
                print(('"{}" query returned an error: ({}).'.format(display_query, e)))
                sys.exit(1)
        return display

    @staticmethod
    def expand_valid_values(valid_values):
        """Expand supported playbook variables to their full list.

        Args:
            valid_values (list): The list of valid values for Choice or MultiChoice inputs.

        Returns:
            List: An expanded list of valid values for Choice or MultiChoice inputs.
        """

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
            valid_values.append('')
        elif '${USERS}' in valid_values:
            valid_values.remove('${USERS}')
            valid_values.append('')
        return valid_values

    def print_permutations(self):
        """Print all valid permutations."""
        index = 0
        permutations = []
        for p in self._input_permutations:
            permutations.append({'index': index, 'args': p})
            index += 1
        with open('permutations.json', 'w') as fh:
            json.dump(permutations, fh, indent=2)
        print('All permutations written to the "permutations.json" file.')

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
