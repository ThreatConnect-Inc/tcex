#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework Validate Module."""
# standard library
import ast
import importlib
import json
import os
import sys
import traceback
from collections import deque

# third-party
import colorama as c
from jsonschema import SchemaError, ValidationError, validate
from stdlib_list import stdlib_list

from .bin import Bin

try:
    # third-party
    import pkg_resources
except PermissionError:
    # this module is only required for certain CLI commands
    pass

try:
    # standard library
    import sqlite3
except ModuleNotFoundError:
    # this module is only required for certain CLI commands
    pass


class Validate(Bin):
    """Validate syntax, imports, and schemas.

    * Python and JSON file syntax
    * Python import modules
    * install.json schema
    * layout.json schema

    Args:
        _args (namespace): The argparser args Namespace.
    """

    def __init__(self, _args):
        """Init Class properties.

        Args:
            _args (namespace): The argparser args Namespace.
        """
        super().__init__(_args)

        # class properties
        self._app_packages = []
        self._install_json_schema = None
        self._layout_json_schema = None
        self.config = {}

        if 'pkg_resources' in sys.modules:
            # only set these if pkg_resource module is available
            pkg_path = pkg_resources.resource_filename(__name__, '').rstrip('bin')
            self.install_json_schema_file = os.path.join(
                pkg_path, 'schemas', 'install-json-schema.json'
            )
            self.layout_json_schema_file = os.path.join(
                pkg_path, 'schemas', 'layout-json-schema.json'
            )
        else:
            self.install_json_schema_file = None
            self.layout_json_schema_file = None
        self.validation_data = self._validation_data

    @property
    def _validation_data(self):
        """Return structure for validation data."""
        return {'errors': [], 'fileSyntax': [], 'layouts': [], 'moduleImports': [], 'schema': []}

    def check_imports(self):
        """Check the projects top level directory for missing imports.

        This method will check only files ending in **.py** and does not handle imports validation
        for sub-directories.
        """
        modules = []
        for filename in sorted(os.listdir(self.app_path)):
            if not filename.endswith('.py'):
                continue

            fq_path = os.path.join(self.app_path, filename)
            with open(fq_path, 'rb') as f:
                # TODO: fix this
                code_lines = deque([(f.read(), 1)])

                while code_lines:
                    m_status = True
                    code, lineno = code_lines.popleft()  # pylint: disable=unused-variable
                    try:
                        parsed_code = ast.parse(code)
                        for node in ast.walk(parsed_code):
                            if isinstance(node, ast.Import):
                                for n in node.names:
                                    m = n.name.split('.')[0]
                                    if self.check_import_stdlib(m):
                                        # stdlib module, not need to proceed
                                        continue
                                    m_status = self.check_imported(m)
                                    modules.append(
                                        {'file': filename, 'module': m, 'status': m_status}
                                    )
                            elif isinstance(node, ast.ImportFrom):
                                m = node.module.split('.')[0]
                                if self.check_import_stdlib(m):
                                    # stdlib module, not need to proceed
                                    continue
                                m_status = self.check_imported(m)
                                modules.append({'file': filename, 'module': m, 'status': m_status})
                            else:
                                continue
                    except SyntaxError:
                        pass

        for module_data in modules:
            status = True
            if not module_data.get('status'):
                status = False
                # update validation data errors
                self.validation_data['errors'].append(
                    f"""Module validation failed for {module_data.get('file')} """
                    f"""(module "{module_data.get('module')}" could not be imported)."""
                )
            # update validation data for module
            self.validation_data['moduleImports'].append(
                {
                    'filename': module_data.get('file'),
                    'module': module_data.get('module'),
                    'status': status,
                }
            )

    @staticmethod
    def check_import_stdlib(module):
        """Check if module is in Python stdlib.

        Args:
            module (str): The name of the module to check.

        Returns:
            bool: Returns True if the module is in the stdlib or template.
        """
        if (
            module in stdlib_list('3.6')
            or module in stdlib_list('3.7')
            or module in stdlib_list('3.8')
            or module in ['app', 'args', 'job_app', 'playbook_app', 'run', 'service_app']
        ):
            return True
        return False

    @staticmethod
    def check_imported(module):
        """Check whether the provide module can be imported (package installed).

        Args:
            module (str): The name of the module to check availability.

        Returns:
            bool: True if the module can be imported, False otherwise.
        """
        try:
            del sys.modules[module]
        except (AttributeError, KeyError):
            pass

        # https://docs.python.org/3/library/importlib.html#checking-if-a-module-can-be-imported
        find_spec = importlib.util.find_spec(module)
        found = find_spec is not None
        if found is True:
            # if dist-packages|site-packages in module_path the import doesn't count
            if 'dist-packages' in find_spec.origin:
                found = False
            if 'site-packages' in find_spec.origin:
                found = False
        return found

    def check_install_json(self):
        """Check all install.json files for valid schema."""
        if self.install_json_schema is None:
            return

        contents = os.listdir(self.app_path)
        if self.args.install_json is not None:
            contents = [self.args.install_json]

        for install_json in sorted(contents):
            # skip files that are not install.json files
            if 'install.json' not in install_json:
                continue

            error = None
            status = True

            try:
                # loading explicitly here to keep all error catching in this file
                with open(install_json) as fh:
                    data = json.loads(fh.read())
                validate(data, self.install_json_schema)
            except SchemaError as e:
                status = False
                error = e
            except ValidationError as e:
                status = False
                error = e.message
            except ValueError:
                # any JSON decode error will be caught during syntax validation
                return

            if error:
                # update validation data errors
                self.validation_data['errors'].append(
                    f'Schema validation failed for {install_json} ({error}).'
                )

            # update validation data for module
            self.validation_data['schema'].append({'filename': install_json, 'status': status})

    def check_layout_json(self):
        """Check all layout.json files for valid schema."""
        # the install.json files can't be validates if the schema file is not present
        layout_json_file = 'layout.json'
        if self.layout_json_schema is None or not os.path.isfile(layout_json_file):
            return

        error = None
        status = True
        try:
            # loading explicitly here to keep all error catching in this file
            with open(layout_json_file) as fh:
                data = json.loads(fh.read())
            validate(data, self.layout_json_schema)
        except SchemaError as e:
            status = False
            error = e
        except ValidationError as e:
            status = False
            error = e.message
        except ValueError:
            # any JSON decode error will be caught during syntax validation
            return

        # update validation data for module
        self.validation_data['schema'].append({'filename': layout_json_file, 'status': status})

        if error:
            # update validation data errors
            self.validation_data['errors'].append(
                f'Schema validation failed for {layout_json_file} ({error}).'
            )
        else:
            self.check_layout_params()

    def check_layout_params(self):
        """Check that the layout.json is consistent with install.json.

        The layout.json files references the params.name from the install.json file.  The method
        will validate that no reference appear for inputs in install.json that don't exist.
        """

        # do not track hidden or serviceConfig inputs as they should not be in layouts.json
        ij_input_names = [
            p.get('name')
            for p in self.ij.filter_params_dict(service_config=False, hidden=False).values()
        ]
        ij_output_names = [o.get('name') for o in self.ij.output_variables]

        # Check for duplicate inputs
        for name in self.ij.validate_duplicate_input_names():
            self.validation_data['errors'].append(
                f'Duplicate input name found in install.json ({name})'
            )
            status = False

        # Check for duplicate sequence numbers
        for sequence in self.ij.validate_duplicate_sequences():
            self.validation_data['errors'].append(
                f'Duplicate sequence number found in install.json ({sequence})'
            )
            status = False

        # Check for duplicate outputs variables
        for output in self.ij.validate_duplicate_outputs():
            self.validation_data['errors'].append(
                f'Duplicate output variable name found in install.json ({output})'
            )
            status = False

        if 'sqlite3' in sys.modules:
            # create temporary inputs tables
            self.permutations.db_create_table(self.permutations.input_table, ij_input_names)

        # inputs
        status = True
        for i in self.lj.inputs:
            for p in i.get('parameters'):
                if p.get('name') not in ij_input_names:
                    # update validation data errors
                    self.validation_data['errors'].append(
                        'Layouts input.parameters[].name validations failed '
                        f"""("{p.get('name')}" is defined in layout.json, """
                        'but hidden or not found in install.json).'
                    )
                    status = False
                else:
                    # any item in list afterwards is a problem
                    ij_input_names.remove(p.get('name'))

                if 'sqlite3' in sys.modules:
                    if p.get('display'):
                        display_query = (
                            f'''SELECT * FROM {self.permutations.input_table}'''  # nosec
                            f''' WHERE {p.get('display')}'''
                        )
                        try:
                            self.permutations.db_conn.execute(display_query.replace('"', ''))
                        except sqlite3.Error:
                            self.validation_data['errors'].append(
                                '''Layouts input.parameters[].display validations failed '''
                                f'''("{p.get('display')}" query is an invalid statement).'''
                            )
                            status = False

        # update validation data for module
        self.validation_data['layouts'].append({'params': 'inputs', 'status': status})

        if ij_input_names:
            input_names = ','.join(ij_input_names)
            # update validation data errors
            self.validation_data['errors'].append(
                f'Layouts input.parameters[].name validations failed ("{input_names}" '
                'values from install.json were not included in layout.json.'
            )
            status = False

        # outputs
        status = True
        for o in self.lj.outputs:
            if o.get('name') not in ij_output_names:
                # update validation data errors
                self.validation_data['errors'].append(
                    f'''Layouts output validations failed ({o.get('name')} is defined '''
                    '''in layout.json, but not found in install.json).'''
                )
                status = False

            if 'sqlite3' in sys.modules:
                if o.get('display'):
                    display_query = (
                        f'''SELECT * FROM {self.permutations.input_table} '''  # nosec
                        f'''WHERE {o.get('display')}'''
                    )
                    try:
                        self.permutations.db_conn.execute(display_query.replace('"', ''))
                    except sqlite3.Error:
                        self.validation_data['errors'].append(
                            f"""Layouts outputs.display validations failed ("{o.get('display')}" """
                            f"""query is an invalid statement)."""
                        )
                        status = False

        # update validation data for module
        self.validation_data['layouts'].append({'params': 'outputs', 'status': status})

    def check_syntax(self, app_path=None):
        """Run syntax on each ".py" and ".json" file.

        Args:
            app_path (str, optional): Defaults to None. The path of Python files.
        """
        app_path = app_path or '.'

        for filename in sorted(os.listdir(app_path)):
            error = None
            status = True
            if filename.endswith('.py'):
                try:
                    with open(filename, 'rb') as f:
                        ast.parse(f.read(), filename=filename)
                except SyntaxError:
                    status = False
                    # cleanup output
                    e = []
                    for line in traceback.format_exc().split('\n')[-5:-2]:
                        e.append(line.strip())
                    error = ' '.join(e)

            elif filename.endswith('.json'):
                try:
                    with open(filename, 'r') as fh:
                        json.load(fh)
                except ValueError as e:
                    status = False
                    error = e
            else:
                # skip unsupported file types
                continue

            if error:
                # update validation data errors
                self.validation_data['errors'].append(
                    f'Syntax validation failed for {filename} ({error}).'
                )

            # store status for this file
            self.validation_data['fileSyntax'].append({'filename': filename, 'status': status})

    @property
    def install_json_schema(self):
        """Load install.json schema file."""
        if self._install_json_schema is None and self.install_json_schema_file is not None:
            # remove old schema file
            if os.path.isfile('tcex_json_schema.json'):
                # this file is now part of tcex.
                os.remove('tcex_json_schema.json')

            if os.path.isfile(self.install_json_schema_file):
                with open(self.install_json_schema_file) as fh:
                    self._install_json_schema = json.load(fh)
        return self._install_json_schema

    def interactive(self):
        """Run in interactive mode."""
        while True:
            line = sys.stdin.readline().strip()
            if line == 'quit':
                sys.exit()
            elif line == 'validate':
                self.check_syntax()
                self.check_imports()
                self.check_install_json()
                self.check_layout_json()
                self.print_json()

            # reset validation_data
            self.validation_data = self._validation_data

    @property
    def layout_json_schema(self):
        """Load layout.json schema file."""
        if self._layout_json_schema is None and self.layout_json_schema_file is not None:
            if os.path.isfile(self.layout_json_schema_file):
                with open(self.layout_json_schema_file) as fh:
                    self._layout_json_schema = json.load(fh)
        return self._layout_json_schema

    def print_json(self):
        """Print JSON output."""
        print(json.dumps({'validation_data': self.validation_data}))

    def print_results(self):
        """Print results."""
        # Validating Syntax
        if self.validation_data.get('fileSyntax'):
            print(f'\n{c.Style.BRIGHT}{c.Fore.BLUE}Validated File Syntax:')
            print(f"{c.Style.BRIGHT}{'File:'!s:<60}{'Status:'!s:<25}")
            for f in self.validation_data.get('fileSyntax'):
                status_color = self.status_color(f.get('status'))
                status_value = self.status_value(f.get('status'))
                print(f"{f.get('filename')!s:<60}{status_color}{status_value!s:<25}")

        # Validating Imports
        if self.validation_data.get('moduleImports'):
            print(f'\n{c.Style.BRIGHT}{c.Fore.BLUE}Validated Imports:')
            print(f"{c.Style.BRIGHT}{'File:'!s:<30}{'Module:'!s:<30}{'Status:'!s:<25}")
            for f in self.validation_data.get('moduleImports'):
                status_color = self.status_color(f.get('status'))
                status_value = self.status_value(f.get('status'))
                print(
                    f"{f.get('filename')!s:<30}{c.Fore.WHITE}"
                    f"{f.get('module')!s:<30}{status_color}{status_value!s:<25}"
                )

        # Validating Schema
        if self.validation_data.get('schema'):
            print(f'\n{c.Style.BRIGHT}{c.Fore.BLUE}Validated Schema:')
            print(f"{c.Style.BRIGHT}{'File:'!s:<60}{'Status:'!s:<25}")
            for f in self.validation_data.get('schema'):
                status_color = self.status_color(f.get('status'))
                status_value = self.status_value(f.get('status'))
                print(f"{f.get('filename')!s:<60}{status_color}{status_value!s:<25}")

        # Validating Layouts
        if self.validation_data.get('layouts'):
            print(f'\n{c.Style.BRIGHT}{c.Fore.BLUE}Validated Layouts:')
            print(f"{c.Style.BRIGHT}{'Params:'!s:<60}{'Status:'!s:<25}")
            for f in self.validation_data.get('layouts'):
                status_color = self.status_color(f.get('status'))
                status_value = self.status_value(f.get('status'))
                print(f"{f.get('params')!s:<60}{status_color}{status_value!s:<25}")

        if self.validation_data.get('errors'):
            print('\n')  # separate errors from normal output
        for error in self.validation_data.get('errors'):
            # print all errors
            print(f'* {c.Fore.RED}{error}')

            # ignore exit code
            if not self.args.ignore_validation:
                self.exit_code = 1

    @staticmethod
    def status_color(status):
        """Return the appropriate status color."""
        status_color = c.Fore.GREEN
        if not status:
            status_color = c.Fore.RED
        return status_color

    @staticmethod
    def status_value(status):
        """Return the appropriate status color."""
        status_value = 'passed'
        if not status:
            status_value = 'failed'
        return status_value
