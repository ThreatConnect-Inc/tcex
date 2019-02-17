#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework Bin Command Base Module."""
import json
import os
import sqlite3
import sys

import colorama as c
import redis


class TcExBin(object):
    """Create profiles for App."""

    def __init__(self, _args):
        """Init Class properties."""
        self.args = _args

        # properties
        self._db_conn = None
        self._install_json = None
        self._install_json_params = None
        self._layout_json = None
        self._layout_json_names = None
        self._layout_json_params = None
        self._redis = None
        self.app_path = os.getcwd()
        self.input_table = 'inputs'
        # self.output_table = 'outputs'

    @property
    def db_conn(self):
        """Create a temporary in memory DB and return the connection."""
        if self._db_conn is None:
            try:
                self._db_conn = sqlite3.connect(':memory:')
            except sqlite3.Error as e:
                sys.exit(1, e)
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
        # print('create_table_sql', create_table_sql)
        try:
            cr = self.db_conn.cursor()
            cr.execute(create_table_sql)
        except sqlite3.Error as e:
            sys.exit(1, e)

    def db_insert_record(self, table, fields):
        """Insert records into DB."""
        bindings = ('?,' * len(fields)).strip(',')
        values = [None] * len(fields)
        # print('len(fields)', len(fields))
        # print('len(values)', len(values))
        sql = 'INSERT INTO {} ({}) VALUES ({})'.format(table, ', '.join(fields), bindings)
        # print('sql', sql)
        # print('value', values)
        cur = self.db_conn.cursor()
        cur.execute(sql, values)

        # print('lastrowid', cur.lastrowid)
        # return cur.lastrowid

    def db_update_record(self, table, field, value):
        """Insert records into DB."""
        # row_id = 1
        # sql = 'UPDATE {} SET {} = {} WHERE row_id = {}'.format(
        #     table, field, value, row_id
        # )
        sql = 'UPDATE {} SET {} = \'{}\''.format(table, field, value)
        # print('sql', sql)
        cur = self.db_conn.cursor()
        cur.execute(sql)

    @staticmethod
    def handle_error(err, halt=True):
        """Print errors message and optionally exit."""
        print('{}{}{}'.format(c.Style.BRIGHT, c.Fore.RED, err))
        if halt:
            sys.exit(1)

    @property
    def install_json(self):
        """Return install.json contents."""
        install_json_filename = 'install.json'
        if self._install_json is None and os.path.isfile(install_json_filename):
            load_output = 'Load install.json: {}{}{}{}'.format(
                c.Style.BRIGHT, c.Fore.CYAN, install_json_filename, c.Style.RESET_ALL
            )
            with open(install_json_filename, 'r') as fh:
                self._install_json = json.load(fh)
            load_output += ' {}{}(Loaded){}'.format(c.Style.BRIGHT, c.Fore.GREEN, c.Style.RESET_ALL)
        return self._install_json

    @property
    def install_json_params(self):
        """Return install.json params in a dict with name param as key."""
        if self._install_json_params is None:
            self._install_json_params = {}
            # TODO: support for projects with multiple install.json files is not supported
            ij = self.load_install_json('install.json')
            for p in ij.get('params') or []:
                self._install_json_params.setdefault(p.get('name'), p)
        return self._install_json_params

    @property
    def layout_json(self):
        """Return layout.json contents."""
        layout_json_filename = 'layout.json'
        if self._layout_json is None and os.path.isfile(layout_json_filename):
            load_output = 'Load layout.json: {}{}{}{}'.format(
                c.Style.BRIGHT, c.Fore.CYAN, layout_json_filename, c.Style.RESET_ALL
            )
            with open(layout_json_filename, 'r') as fh:
                self._layout_json = json.load(fh)
            load_output += ' {}{}(Loaded){}'.format(c.Style.BRIGHT, c.Fore.GREEN, c.Style.RESET_ALL)
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
        """Return layout.json params in a flattened dict with name param as key."""
        if self._layout_json_names is None:
            self._layout_json_names = []
            for name in self.layout_json_params:
                self._layout_json_names.append(name)
        return self._layout_json_names

    @staticmethod
    def load_install_json(filename):
        """Return install.json data."""
        install_json = None
        load_output = 'Load install.json: {}{}{}{}'.format(
            c.Style.BRIGHT, c.Fore.CYAN, filename, c.Style.RESET_ALL
        )
        if filename is not None and os.path.isfile(filename):
            with open(filename) as config_data:
                install_json = json.load(config_data)
            load_output += ' {}{}(Loaded){}'.format(c.Style.BRIGHT, c.Fore.GREEN, c.Style.RESET_ALL)
        else:
            load_output += ' {}{}(Not Found){}'.format(
                c.Style.BRIGHT, c.Fore.YELLOW, c.Style.RESET_ALL
            )
            sys.exit(1)
        return install_json

    @property
    def redis(self):
        """Return instance of Redis."""
        if self._redis is None:
            self._redis = redis.StrictRedis(host=self.args.redis_host, port=self.args.redis_port)
        return self._redis
