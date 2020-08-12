#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework LayoutJson."""
# standard library
import json
import logging
import os
import random
import sys

try:
    # standard library
    import sqlite3
except ImportError:
    # only required for local development
    pass

from .install_json import InstallJson
from .layout_json import LayoutJson


class Permutations:
    """Permutations Module

    Args:
        logger (logging.Logger, optional): A instance of Logger. Defaults to None.
    """

    def __init__(self, logger=None):
        """Initialize Class properties"""
        self.log = logger or logging.getLogger('permutations')

        # properties
        self._db_conn = None
        self._input_names = None
        self._input_permutations = None
        self._output_permutations = None
        self.app_path = os.getcwd()
        self.ij = InstallJson()
        self.lj = LayoutJson()
        self.input_table = 'inputs'

    def _gen_permutations(self, index=0, args=None):
        """Iterate recursively over layout.json parameter names to build permutations.

        .. NOTE:: Permutations are for layout.json based Apps.

        Args:
            index (int, optional): The current index position in the layout names list.
            args (list, optional): Defaults to None. The current list of args.
        """
        if args is None:
            args = []
        try:
            hidden = False
            if self.ij.runtime_level.lower() in [
                'playbook',
                'triggerservice',
                'webhooktriggerservice',
            ]:
                name = list(self.lj.parameters_names)[index]
                display = self.lj.params_dict.get(name, {}).get('display')
                hidden = self.lj.params_dict.get(name, {}).get('hidden', False)
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
                        self._gen_permutations(index + 1, list(args))
                        # remove the previous arg before next iteration
                        args.pop()
                elif input_type.lower() == 'choice':
                    valid_values = self.ij.expand_valid_values(
                        self.ij.params_dict.get(name, {}).get('validValues', [])
                    )
                    for val in valid_values:
                        args.append({'name': name, 'value': val})
                        self.db_update_record(self.input_table, name, val)
                        self._gen_permutations(index + 1, list(args))
                        # remove the previous arg before next iteration
                        args.pop()
                else:
                    args.append({'name': name, 'value': None})
                    self._gen_permutations(index + 1, list(args))
            else:
                self._gen_permutations(index + 1, list(args))

        except IndexError:
            # when IndexError is reached all data has been processed.
            self._input_permutations.append(args)
            outputs = []

            for output_data in self.ij.output_variables:
                name = output_data.get('name')
                if self.lj.outputs_dict.get(name) is not None:
                    display = self.lj.outputs_dict.get(name, {}).get('display')
                    valid = self.validate_layout_display(self.input_table, display)
                    if display is None or not valid:
                        continue
                outputs.append(output_data)
            self._output_permutations.append(outputs)

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

    def db_drop_table(self, table_name):
        """Drop a DB table.

        Arguments:
            table_name (str): The name of the table.
        """
        create_table_sql = f'DROP TABLE IF EXISTS {table_name};'
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
        try:
            sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({bindings})"
            cur = self.db_conn.cursor()
            cur.execute(sql, values)
        except sqlite3.OperationalError as e:
            raise RuntimeError(f'SQL insert failed - SQL: "{sql}", Error: "{e}"')

    def db_update_record(self, table_name, column, value):
        """Insert records into DB.

        Args:
            table_name (str): The name of the table.
            column (str): The column name in which the value is to be updated.
            value (str): The value to update in the column.
        """
        # escape any single quotes in value
        if isinstance(value, str):
            value = value.replace('\'', '\\')
        elif isinstance(value, bool):
            # core expects true/false so we convert bool value to string and lower
            value = str(value).lower()

        # only column defined in install.json can be updated
        if column in self.ij.params_dict:
            try:
                # value should be wrapped in single quotes to be properly parsed
                sql = f"UPDATE {table_name} SET {column} = '{value}'"
                cur = self.db_conn.cursor()
                cur.execute(sql)
            except sqlite3.OperationalError as e:
                raise RuntimeError(f'SQL update failed - SQL: "{sql}", Error: "{e}"')

    def exists(self):
        """Return True if permutation file exists."""
        return os.path.isfile(self.filename)

    @property
    def filename(self):
        """Return all output permutations for current App."""
        return os.path.join(self.app_path, 'permutations.json')

    @staticmethod
    def handle_error(err, halt=True):
        """Print errors message and optionally exit.

        Args:
            err (str): The error message to print.
            halt (bool, optional): Defaults to True. If True the script will exit.
        """
        print(err)
        if halt:
            sys.exit(1)

    def init_permutations(self):
        """Process layout.json names/display to get all permutations of args."""
        if self._input_permutations is None and self._output_permutations is None:
            self._input_permutations = []
            self._output_permutations = []

            # create db for permutations testing
            self.db_create_table(self.input_table, self.ij.params_dict.keys())
            self.db_insert_record(self.input_table, self.ij.params_dict.keys())

            # only gen permutations if none have been generated previously
            self._gen_permutations()

            # drop database
            self.db_drop_table(self.input_table)

    def input_dict(self, permutation_id):
        """Return all input permutation names for provided permutation id.

        {'tc_action': 'Append', 'input_strings': None, 'append_chars': None}

        Args:
            permutation_id (int): The index of the permutation input array.

        Returns:
            dict: A dict with key / value for each input for the provided permutation id.
        """
        input_dict = {}
        if self.lj.has_layout:
            for permutation in self.input_permutations[permutation_id]:
                input_dict.setdefault(permutation.get('name'), permutation.get('value'))
        return input_dict

    @property
    def input_names(self):
        """Return all input permutation names for current App."""
        if self._input_names is None and self.lj.has_layout:
            self._input_names = []
            for permutation in self.input_permutations:
                self._input_names.append([p.get('name') for p in permutation])
        return self._input_names

    @property
    def input_permutations(self):
        """Return all input permutations for current App.

        self._input_permutations is an array of permutations arrays.
        [[<perm obj #1], [<perm obj #2]]
        """
        if self._input_permutations is None and self.lj.has_layout:
            self.init_permutations()
        return self._input_permutations

    @property
    def output_permutations(self):
        """Return all output permutations for current App."""
        if self._output_permutations is None:
            self.init_permutations()
        return self._output_permutations

    def outputs_by_inputs(self, inputs):
        """Return all output based on provided inputs

        Args:
            inputs (dict): The args/inputs dict.
        """
        table = f'temp_{random.randint(100,999)}'  # nosec
        self.db_create_table(table, self.ij.params_dict.keys())
        self.db_insert_record(table, self.ij.params_dict.keys())

        for name, val in inputs.items():
            self.db_update_record(table, name, val)

        outputs = []
        # loop through all output variables in install.json
        for output_data in self.ij.output_variables:
            name = output_data.get('name')
            if self.lj.outputs_dict.get(name) is None:
                # an output not listed in layout.json should always be shown
                valid = True
            else:
                # all other outputs must be validated
                display = self.lj.outputs_dict.get(name, {}).get('display')
                valid = self.validate_layout_display(table, display)

            if valid:
                # valid outputs get added to array
                outputs.append(output_data)

        # drop database
        self.db_drop_table(table)

        return outputs

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
            self._gen_permutations()

        # output permutations
        self.write_permutations_file()

    def validate_input_variable(self, input_name, inputs):
        """Return True if the provided variables display where clause returns results.

        Args:
            input_name (dict): The input variable name (e.g. tc_action).
            inputs (dict): The current name/value dict.

        Returns:
            bool: True if the display value returns results.
        """
        if not self.lj.has_layout or not inputs:
            # always return try if current App doesn't have a layouts file
            return True

        table = f'temp_{random.randint(100,999)}'  # nosec
        self.db_create_table(table, self.ij.params_dict.keys())
        self.db_insert_record(table, self.ij.params_dict.keys())

        # APP-98 Added to cover the use case of interdependent variables in the layout.json.
        for name, item in self.ij.filter_params_dict(_type='Boolean').items():
            self.db_update_record(table, name, item.get('default', False))

        for name, val in inputs.items():
            self.db_update_record(table, name, val)

        lj_data = self.lj.params_dict.get(input_name)
        if lj_data is None:
            # this shouldn't happen as all ij inputs must be in lj
            raise RuntimeError(f'The provided input {input_name} was not found in layout.json.')
        display = lj_data.get('display')

        # check if provided variable meets display requirements
        valid = self.validate_layout_display(table, display)

        # cleanup temp table
        self.db_drop_table(table)

        return valid

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
            display_query = f'select count(*) from {table} where {display_condition}'  # nosec
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

    def write_permutations_file(self):
        """Print all valid permutations."""
        permutations = []
        for index, p in enumerate(self.input_permutations):
            permutations.append({'index': index, 'args': p})

        with open(self.filename, 'w') as fh:
            json.dump(permutations, fh, indent=2, sort_keys=True)
        print('All permutations written to the "permutations.json" file.')
