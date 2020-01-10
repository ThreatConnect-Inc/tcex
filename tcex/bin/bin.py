#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework Bin Command Base Module."""
import json
import os
import sys

import colorama as c
import redis

from ..app_config_object import InstallJson, LayoutJson

try:
    import sqlite3
except ModuleNotFoundError:
    # this module is only required for certain CLI commands
    pass


class Bin:
    """Base Class for ThreatConnect command line tools.

    Args:
        _args (namespace): The argparser args Namespace.
    """

    def __init__(self, _args):
        """Initialize Class properties.

        Args:
            _args (namespace): The argparser args Namespace.
        """
        self.args = _args

        # properties
        self._db_conn = None
        self._input_permutations = []
        self._output_permutations = []
        self._redis = None
        self._tcex_json = None
        self.app_path = os.getcwd()
        self.exit_code = 0
        self.ij = InstallJson('install.json', self.app_path)
        self.lj = LayoutJson('layout.json', self.app_path)
        self.input_table = 'inputs'
        self.output = []

        # initialize colorama
        c.init(autoreset=True, strip=False)

    @staticmethod
    def _to_bool(value):
        """Convert string value to bool."""
        bool_value = False
        if str(value).lower() in ['1', 'true']:
            bool_value = True
        return bool_value

    @property
    def db_conn(self):
        """Create a temporary in memory DB and return the connection."""
        if self._db_conn is None:
            try:
                self._db_conn = sqlite3.connect(':memory:')
            except sqlite3.Error as e:
                self.handle_error(e)
        return self._db_conn

    def db_create_table(self, table_name, columns):
        """Create a temporary DB table.

        Arguments:
            table_name (str): The name of the table.
            columns (list): List of columns to add to the DB.
        """
        formatted_columns = ''
        for col in set(columns):
            formatted_columns += f""""{col.strip('"').strip("'")}" text, """
        formatted_columns = formatted_columns.strip(', ')

        create_table_sql = f'CREATE TABLE IF NOT EXISTS {table_name} ({formatted_columns});'
        try:
            cr = self.db_conn.cursor()
            cr.execute(create_table_sql)
        except sqlite3.Error as e:
            self.handle_error(e)

    def db_insert_record(self, table_name, columns):
        """Insert records into DB.

        Args:
            table_name (str): The name of the table.
            columns (list): List of columns for insert statement.
        """
        bindings = ('?,' * len(columns)).strip(',')
        values = [None] * len(columns)
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({bindings})"
        cur = self.db_conn.cursor()
        cur.execute(sql, values)

    def db_update_record(self, table_name, column, value):
        """Insert records into DB.

        Args:
            table_name (str): The name of the table.
            column (str): The column name in which the value is to be updated.
            value (str): The value to update in the column.
        """
        sql = f'UPDATE {table_name} SET {column} = \'{value}\''
        cur = self.db_conn.cursor()
        cur.execute(sql)

    def gen_permutations(self, index=0, args=None):
        """Iterate recursively over layout.json parameter names to build permutations.

        .. NOTE:: Permutations are for layout.json based playbook Apps.

        Args:
            index (int, optional): The current index position in the layout names list.
            args (list, optional): Defaults to None. The current list of args.
        """
        if args is None:
            args = []
        try:
            hidden = False
            if self.ij.runtime_level.lower() == 'playbook':
                name = list(self.lj.parameters_names)[index]
                display = self.lj.parameters_dict.get(name, {}).get('display')
                hidden = self.lj.parameters_dict.get(name, {}).get('hidden', False)
            else:
                name = list(self.ij.params_dict.keys())[index]
                display = False

            input_type = self.ij.params_dict.get(name, {}).get('type')
            if input_type is None:
                self.handle_error(f'No value found in install.json for "{name}".')

            if (
                self.ij.runtime_level.lower() == 'organization'
                or self.validate_layout_display(self.input_table, display)
                or hidden
            ):
                if input_type.lower() == 'boolean':
                    for val in [True, False]:
                        args.append({'name': name, 'value': val})
                        self.db_update_record(self.input_table, name, val)
                        self.gen_permutations(index + 1, list(args))
                        # remove the previous arg before next iteration
                        args.pop()
                elif input_type.lower() == 'choice':
                    valid_values = self.ij.expand_valid_values(
                        self.ij.params_dict.get(name, {}).get('validValues', [])
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

            for o_name in self.ij.output_variables_dict():
                if self.lj.outputs_dict.get(o_name) is not None:
                    display = self.lj.outputs_dict.get(o_name, {}).get('display')
                    valid = self.validate_layout_display(self.input_table, display)
                    if display is None or not valid:
                        continue
                outputs.append(self.ij.output_variables_dict().get(o_name))
            self._output_permutations.append(outputs)

    @staticmethod
    def handle_error(err, halt=True):
        """Print errors message and optionally exit.

        Args:
            err (str): The error message to print.
            halt (bool, optional): Defaults to True. If True the script will exit.
        """
        print(f'{c.Style.BRIGHT}{c.Fore.RED}{err}')
        if halt:
            sys.exit(1)

    def permutations(self):
        """Process layout.json names/display to get all permutations of args."""
        if 'sqlite3' not in sys.modules:
            print('The sqlite3 module needs to be build-in to Python for this feature.')
            sys.exit(1)

        # create db for permutations testing
        self.db_create_table(self.input_table, self.ij.params_dict.keys())
        self.db_insert_record(self.input_table, self.ij.params_dict.keys())

        # only gen permutations if none have been generated previously
        if not self._input_permutations and not self._output_permutations:
            self.gen_permutations()

        # output permutations
        self.print_permutations()

    def print_permutations(self):
        """Print all valid permutations."""
        index = 0
        permutations = []
        for p in self._input_permutations:
            permutations.append({'index': index, 'args': p})
            index += 1
        with open('permutations.json', 'w') as fh:
            json.dump(permutations, fh, indent=2, sort_keys=True)
        print('All permutations written to the "permutations.json" file.')

    def profile_settings_args_layout_json(self, required):
        """Return args based on layout.json and conditional rendering.

        Args:
            required (bool): If True only required args will be returned.

        Returns:
            dict: Dictionary of required or optional App args.
        """
        self.db_create_table(self.input_table, self.ij.params_dict.keys())
        self.db_insert_record(self.input_table, self.ij.params_dict.keys())

        # only gen permutations if none have been generated previously
        if not self._input_permutations and not self._output_permutations:
            self.gen_permutations()

        profile_args = {}
        try:
            for pn in self._input_permutations[self.args.permutation_id]:
                p = self.ij.filter_params_dict(required=required).get(pn.get('name'))
                if p is None:
                    continue

                if p.get('type').lower() == 'boolean':
                    # use the value generated in the permutation
                    profile_args[p.get('name')] = pn.get('value')
                elif p.get('type').lower() == 'choice':
                    # use the value generated in the permutation
                    profile_args[p.get('name')] = pn.get('value')
                elif p.get('type').lower() == 'keyvaluelist':
                    profile_args[p.get('name')] = '<KeyValueList>'
                elif p.get('name') in ['api_access_id', 'api_secret_key']:
                    # leave these parameters set to the value defined in defaults
                    pass
                else:
                    # add type stub for values
                    types = '|'.join(p.get('playbookDataType', []))
                    if types:
                        profile_args[p.get('name')] = p.get('default', f'<{types}>')
                    else:
                        profile_args[p.get('name')] = p.get('default', '')
        except IndexError:
            self.handle_error('Invalid permutation index provided.')
        return profile_args

    @property
    def redis(self):
        """Return instance of Redis."""
        if self._redis is None:
            self._redis = redis.StrictRedis(host=self.args.redis_host, port=self.args.redis_port)
        return self._redis

    @property
    def tcex_json(self):
        """Return tcex.json file contents."""
        file_fqpn = os.path.join(self.app_path, 'tcex.json')
        if self._tcex_json is None:
            if os.path.isfile(file_fqpn):
                try:
                    with open(file_fqpn, 'r') as fh:
                        self._tcex_json = json.load(fh)
                except ValueError as e:
                    self.handle_error(f'Failed to load "{file_fqpn}" file ({e}).')
            else:
                # self.handle_error(f'File "{file_fqpn}" could not be found.')
                self._tcex_json = {}
        return self._tcex_json

    @staticmethod
    def update_system_path():
        """Update the system path to ensure project modules and dependencies can be found."""
        cwd = os.getcwd()
        lib_dir = os.path.join(os.getcwd(), 'lib_')
        lib_latest = os.path.join(os.getcwd(), 'lib_latest')

        # insert the lib_latest directory into the system Path if no other lib directory found. This
        # entry will be bumped to index 1 after adding the current working directory.
        if not [p for p in sys.path if lib_dir in p]:
            sys.path.insert(0, lib_latest)

        # insert the current working directory into the system Path for the App, ensuring that it is
        # always the first entry in the list.
        try:
            sys.path.remove(cwd)
        except ValueError:
            pass
        sys.path.insert(0, cwd)

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
            display_query = f'select count(*) from {table} where {display_condition}'
            try:
                cur = self.db_conn.cursor()
                cur.execute(display_query.replace('"', ''))
                rows = cur.fetchall()
                if rows[0][0] > 0:
                    display = True
            except sqlite3.Error as e:
                print(f'"{display_query}" query returned an error: ({e}).')
                sys.exit(1)
        return display
