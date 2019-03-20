#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework Bin Command Base Module."""
import json
import os
import sys

try:
    import sqlite3
except ModuleNotFoundError:
    # this module is only required for certain CLI commands
    pass

import colorama as c
import redis


class TcExBin(object):
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
        self._install_json = None
        self._install_json_params = None
        self._install_json_output_variables = None
        self._layout_json = None
        self._layout_json_names = None
        self._layout_json_params = None
        self._layout_json_outputs = None
        self._redis = None
        self._tcex_json = None
        self.app_path = os.getcwd()
        self.exit_code = 0
        self.input_table = 'inputs'
        self.output = []

        # initialize colorama
        c.init(autoreset=True, strip=False)

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
            formatted_columns += '"{}" text, '.format(col.strip('"').strip('\''))
        formatted_columns = formatted_columns.strip(', ')

        create_table_sql = 'CREATE TABLE IF NOT EXISTS {} ({});'.format(
            table_name, formatted_columns
        )
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
        sql = 'INSERT INTO {} ({}) VALUES ({})'.format(table_name, ', '.join(columns), bindings)
        cur = self.db_conn.cursor()
        cur.execute(sql, values)

    def db_update_record(self, table_name, column, value):
        """Insert records into DB.

        Args:
            table_name (str): The name of the table.
            column (str): The column name in which the value is to be updated.
            value (str): The value to update in the column.
        """
        sql = 'UPDATE {} SET {} = \'{}\''.format(table_name, column, value)
        cur = self.db_conn.cursor()
        cur.execute(sql)

    @staticmethod
    def handle_error(err, halt=True):
        """Print errors message and optionally exit.

        Args:
            err (str): The error message to print.
            halt (bool, optional): Defaults to True. If True the script will exit.
        """
        print('{}{}{}'.format(c.Style.BRIGHT, c.Fore.RED, err))
        if halt:
            sys.exit(1)

    @property
    def install_json(self):
        """Return install.json contents."""
        file_fqpn = os.path.join(self.app_path, 'install.json')
        if self._install_json is None:
            if os.path.isfile(file_fqpn):
                try:
                    with open(file_fqpn, 'r') as fh:
                        self._install_json = json.load(fh)
                except ValueError as e:
                    self.handle_error('Failed to load "{}" file ({}).'.format(file_fqpn, e))
            else:
                self.handle_error('File "{}" could not be found.'.format(file_fqpn))
        return self._install_json

    def install_json_params(self, ij=None):
        """Return install.json params in a dict with name param as key.

        Args:
            ij (dict, optional): Defaults to None. The install.json contents.

        Returns:
            dict: A dictionary containing the install.json input params with name as key.
        """
        if self._install_json_params is None or ij is not None:
            self._install_json_params = {}
            # TODO: support for projects with multiple install.json files is not supported
            if ij is None:
                ij = self.install_json
            for p in ij.get('params') or []:
                self._install_json_params.setdefault(p.get('name'), p)
        return self._install_json_params

    def install_json_output_variables(self, ij=None):
        """Return install.json output variables in a dict with name param as key.

        Args:
            ij (dict, optional): Defaults to None. The install.json contents.

        Returns:
            dict: A dictionary containing the install.json output variables with name as key.
        """
        if self._install_json_output_variables is None or ij is not None:
            self._install_json_output_variables = {}
            # TODO: currently there is no support for projects with multiple install.json files.
            if ij is None:
                ij = self.install_json
            for p in ij.get('playbook', {}).get('outputVariables') or []:
                self._install_json_output_variables.setdefault(p.get('name'), []).append(p)
        return self._install_json_output_variables

    @property
    def layout_json(self):
        """Return layout.json contents."""
        file_fqpn = os.path.join(self.app_path, 'layout.json')
        if self._layout_json is None:
            if os.path.isfile(file_fqpn):
                try:
                    with open(file_fqpn, 'r') as fh:
                        self._layout_json = json.load(fh)
                except ValueError as e:
                    self.handle_error('Failed to load "{}" file ({}).'.format(file_fqpn, e))
            else:
                self.handle_error('File "{}" could not be found.'.format(file_fqpn))
        return self._layout_json

    @property
    def layout_json_params(self):
        """Return layout.json params in a flattened dict with name param as key."""
        if self._layout_json_params is None:
            self._layout_json_params = {}
            for i in self.layout_json.get('inputs', []):
                for p in i.get('parameters', []):
                    self._layout_json_params.setdefault(p.get('name'), p)
        return self._layout_json_params

    @property
    def layout_json_names(self):
        """Return layout.json names."""
        if self._layout_json_names is None:
            self._layout_json_names = self.layout_json_params.keys()
        return self._layout_json_names

    @property
    def layout_json_outputs(self):
        """Return layout.json outputs in a flattened dict with name param as key."""
        if self._layout_json_outputs is None:
            self._layout_json_outputs = {}
            for o in self.layout_json.get('outputs', []):
                self._layout_json_outputs.setdefault(o.get('name'), o)
        return self._layout_json_outputs

    def load_install_json(self, filename=None):
        """Return install.json data.

        Args:
            filename (str, optional): Defaults to None. The install.json filename (for bundled
                Apps).

        Returns:
            dict: The contents of the install.json file.
        """
        if filename is None:
            filename = 'install.json'

        file_fqpn = os.path.join(self.app_path, filename)
        install_json = None
        if os.path.isfile(file_fqpn):
            try:
                with open(file_fqpn, 'r') as fh:
                    install_json = json.load(fh)
            except ValueError as e:
                self.handle_error('Failed to load "{}" file ({}).'.format(file_fqpn, e))
        else:
            self.handle_error('File "{}" could not be found.'.format(file_fqpn))
        return install_json

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
                    self.handle_error('Failed to load "{}" file ({}).'.format(file_fqpn, e))
            else:
                self.handle_error('File "{}" could not be found.'.format(file_fqpn))
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
