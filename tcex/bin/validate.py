#!/usr/bin/env python
"""TcEx Framework Validate Module."""
# standard library
import ast
import importlib
import json
import os
import sys
import traceback
from collections import deque
from pathlib import Path
from typing import Dict, Union

# third-party
import colorama as c
from pydantic import ValidationError
from stdlib_list import stdlib_list

# first-party
from tcex.app_config.install_json import InstallJson
from tcex.app_config.job_json import JobJson
from tcex.app_config.layout_json import LayoutJson
from tcex.app_config.permutation import Permutation
from tcex.app_config.tcex_json import TcexJson
from tcex.bin.bin_abc import BinABC

try:
    # standard library
    import sqlite3
except ModuleNotFoundError:
    # this module is only required for certain CLI commands
    pass


class Validate(BinABC):
    """Validate syntax, imports, and schemas.

    * Python and JSON file syntax
    * Python import modules
    * install.json schema
    * layout.json schema
    """

    def __init__(self, ignore_validation: bool):
        """Initialize Class properties."""
        super().__init__()
        self.permutations = Permutation()
        self.ignore_validation = ignore_validation

        # class properties
        self._app_packages = []
        self._install_json_schema = None
        self._layout_json_schema = None
        self.config = {}
        self.ij = InstallJson()
        self.invalid_json_files = []
        self.lj = LayoutJson()
        self.tj = TcexJson()

        # initialize validation data
        self.validation_data = self._validation_data

    @property
    def _validation_data(self) -> Dict[str, list]:
        """Return structure for validation data."""
        return {
            'errors': [],
            'fileSyntax': [],
            'layouts': [],
            'moduleImports': [],
            'schema': [],
            'feeds': [],
        }

    def _check_node_import(self, node: Union[ast.Import, ast.ImportFrom], filename: str):
        """."""
        if isinstance(node, ast.Import):
            for n in node.names:
                m = n.name.split('.')[0]
                if not self.check_import_stdlib(m):
                    m_status = self.check_imported(m)
                    if not m_status:
                        self.validation_data['errors'].append(
                            f'Module validation failed for {filename} '
                            f'module "{m}" could not be imported).'
                        )
                    self.validation_data['moduleImports'].append(
                        {'filename': filename, 'module': m, 'status': m_status}
                    )
        elif isinstance(node, ast.ImportFrom):
            m = node.module.split('.')[0]
            if not self.check_import_stdlib(m):
                m_status = self.check_imported(m)
                if not m_status:
                    self.validation_data['errors'].append(
                        f'Module validation failed for {filename} '
                        f'module "{m}" could not be imported).'
                    )
                self.validation_data['moduleImports'].append(
                    {'filename': filename, 'module': m, 'status': m_status}
                )

    def check_imports(self):
        """Check the projects top level directory for missing imports.

        This method will check only files ending in **.py** and does not handle imports validation
        for sub-directories.
        """
        for filename in sorted(os.listdir(self.app_path)):
            if not filename.endswith('.py'):
                continue

            fq_path = os.path.join(self.app_path, filename)
            with open(fq_path, 'rb') as f:
                # TODO: [low] is there a better way?
                code_lines = deque([(f.read(), 1)])

                while code_lines:
                    code, _ = code_lines.popleft()  # pylint: disable=unused-variable
                    try:
                        parsed_code = ast.parse(code)
                        for node in ast.walk(parsed_code):
                            self._check_node_import(node, filename)
                    except SyntaxError:
                        pass

    @staticmethod
    def check_import_stdlib(module: str) -> bool:
        """Check if module is in Python stdlib.

        Args:
            module: The name of the module to check.

        Returns:
            bool: Returns True if the module is in the stdlib or template.
        """
        if (
            module in stdlib_list('3.6')
            or module in stdlib_list('3.7')
            or module in stdlib_list('3.8')
            or module
            in ['app', 'args', 'base_app_input', 'job_app', 'playbook_app', 'run', 'service_app']
        ):
            return True
        return False

    @staticmethod
    def check_imported(module: str) -> bool:
        """Check whether the provide module can be imported (package installed).

        Args:
            module: The name of the module to check availability.

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
            try:
                if 'dist-packages' in find_spec.origin:
                    found = False
            except TypeError:
                pass

            try:
                if 'site-packages' in find_spec.origin:
                    found = False
            except TypeError:
                pass
        return found

    def check_install_json(self):
        """Check all install.json files for valid schema."""
        if 'install.json' in self.invalid_json_files:
            return

        status = True
        try:
            self.ij.model
        except ValidationError as ex:
            self.invalid_json_files.append(self.ij.fqfn.name)
            status = False
            for error in json.loads(ex.json()):
                location = [str(location) for location in error.get('loc')]
                self.validation_data['errors'].append(
                    '''Schema validation failed for install.json. '''
                    f'''{error.get('msg')}: {' -> '.join(location)}'''
                )
        except ValueError:
            # any JSON decode error will be caught during syntax validation
            return

        self.validation_data['schema'].append({'filename': self.ij.fqfn.name, 'status': status})

    def check_job_json(self):
        """Validate feed files for feed job apps."""
        if 'install.json' in self.invalid_json_files:
            # can't proceed if install.json can't be read
            return

        if not self.ij.model.feeds:
            # if no jobs, skip!
            return

        # use developer defined app version (deprecated) or package_version from InstallJson model
        app_version = self.tj.model.package.app_version or self.ij.model.package_version
        program_name = (f'''{self.tj.model.package.app_name}_{app_version}''').replace('_', ' ')
        status = True
        for feed in self.ij.model.feeds or []:
            if feed.job_file in self.invalid_json_files:
                # no need to check if schema if json is invalid
                continue

            jj = JobJson(filename=feed.job_file)

            # validate the job file exists
            if not jj.fqfn.is_file():
                self.validation_data['errors'].append(
                    f'''Schema validation failed for {feed.job_file}. '''
                    f'''The job.json file could not be found.'''
                )
                continue

            try:
                # validate the schema
                jj.model
            except ValidationError as ex:
                status = False
                for error in json.loads(ex.json()):
                    location = [str(location) for location in error.get('loc')]
                    self.validation_data['errors'].append(
                        f'''Schema validation failed for {feed.job_file}. '''
                        f'''{error.get('msg')}: {' -> '.join(location)}'''
                    )

            # validate program name
            if status is True and jj.model.program_name != program_name:
                status = False
                self.validation_data['errors'].append(
                    f'''Schema validation failed for {feed.job_file}. '''
                    f'''The job.json programName {jj.model.program_name} != {program_name}.'''
                )

            # validate program version
            if status is True and jj.model.program_version != self.ij.model.program_version:
                status = False
                self.validation_data['errors'].append(
                    f'''Schema validation failed for {feed.job_file}. The job.json program'''
                    f'''Version {jj.model.program_version} != {self.ij.model.program_version}.'''
                )

            self.validation_data['schema'].append({'filename': feed.job_file, 'status': status})

    def check_layout_json(self):
        """Check all layout.json files for valid schema."""
        if not self.lj.has_layout or 'layout.json' in self.invalid_json_files:
            return

        status = True
        try:
            self.lj.model
        except ValidationError as ex:
            self.invalid_json_files.append(self.ij.fqfn.name)
            status = False
            for error in json.loads(ex.json()):
                location = [str(location) for location in error.get('loc')]
                self.validation_data['errors'].append(
                    f'''Schema validation failed for layout.json. '''
                    f'''{error.get('msg')}: {' -> '.join(location)}'''
                )
        except ValueError:
            # any JSON decode error will be caught during syntax validation
            return

        self.validation_data['schema'].append({'filename': self.lj.fqfn.name, 'status': status})

        if status is True:
            self.check_layout_params()

    def check_layout_params(self):
        """Check that the layout.json is consistent with install.json.

        The layout.json files references the params.name from the install.json file.  The method
        will validate that no reference appear for inputs in install.json that don't exist.
        """
        # do not track hidden or serviceConfig inputs as they should not be in layouts.json
        ij_input_names = list(self.ij.model.filter_params(service_config=False, hidden=False))
        # pylint: disable=no-member
        ij_output_names = [o.name for o in self.ij.model.playbook.output_variables]

        # Check for duplicate inputs
        for name in self.ij.validate.validate_duplicate_input():
            self.validation_data['errors'].append(
                f'Duplicate input name found in install.json ({name})'
            )
            status = False

        # Check for duplicate sequence numbers
        for sequence in self.ij.validate.validate_duplicate_sequence():
            self.validation_data['errors'].append(
                f'Duplicate sequence number found in install.json ({sequence})'
            )
            status = False

        # Check for duplicate outputs variables
        for output in self.ij.validate.validate_duplicate_output():
            self.validation_data['errors'].append(
                f'Duplicate output variable name found in install.json ({output})'
            )
            status = False

        if 'sqlite3' in sys.modules:
            # create temporary inputs tables
            self.permutations.db_create_table(self.permutations._input_table, ij_input_names)

        # inputs
        status = True
        for i in self.lj.model.inputs:
            for p in i.parameters:
                if p.name not in ij_input_names:
                    # update validation data errors
                    self.validation_data['errors'].append(
                        'Layouts input.parameters[].name validations failed '
                        f'''("{p.name}" is defined in layout.json, '''
                        'but hidden or not found in install.json).'
                    )
                    status = False
                else:
                    # any item in list afterwards is a problem
                    ij_input_names.remove(p.name)

                if 'sqlite3' in sys.modules:
                    if p.display:
                        display_query = (
                            f'''SELECT * FROM {self.permutations._input_table}'''  # nosec
                            f''' WHERE {p.display}'''
                        )
                        try:
                            self.permutations.db_conn.execute(display_query.replace('"', ''))
                        except sqlite3.Error:
                            self.validation_data['errors'].append(
                                '''Layouts input.parameters[].display validations failed '''
                                f'''("{p.display}" query is an invalid statement).'''
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
        for o in self.lj.model.outputs:
            if o.name not in ij_output_names:
                # update validation data errors
                self.validation_data['errors'].append(
                    f'''Layouts output validations failed ({o.name} is defined '''
                    '''in layout.json, but not found in install.json).'''
                )
                status = False

            if 'sqlite3' in sys.modules:
                if o.display:
                    display_query = (
                        f'''SELECT * FROM {self.permutations._input_table} '''  # nosec
                        f'''WHERE {o.display}'''
                    )
                    try:
                        self.permutations.db_conn.execute(display_query.replace('"', ''))
                    except sqlite3.Error:
                        self.validation_data['errors'].append(
                            f"""Layouts outputs.display validations failed ("{o.display}" """
                            f"""query is an invalid statement)."""
                        )
                        status = False

        # update validation data for module
        self.validation_data['layouts'].append({'params': 'outputs', 'status': status})

    def check_syntax(self, app_path=None):
        """Run syntax on each ".py" and ".json" file.

        Args:
            app_path (str, optional): The path of Python files.
        """
        fqpn = Path(app_path or os.getcwd())

        for fqfn in sorted(fqpn.iterdir()):
            error = None
            status = True
            if fqfn.name.endswith('.py'):
                try:
                    with fqfn.open(mode='rb') as fh:
                        ast.parse(fh.read(), filename=fqfn.name)
                except SyntaxError:
                    status = False

                    # cleanup output
                    e = []
                    for line in traceback.format_exc().split('\n')[-5:-2]:
                        e.append(line.strip())
                    error = ' '.join(e)

            elif fqfn.name.endswith('.json'):
                try:
                    with fqfn.open() as fh:
                        json.load(fh)
                except ValueError as e:
                    # update tracker for common files
                    self.invalid_json_files.append(fqfn.name)
                    status = False
                    error = e
            else:
                # skip unsupported file types
                continue

            if error:
                # update validation data errors
                self.validation_data['errors'].append(
                    f'Syntax validation failed for {fqfn.name} ({error}).'
                )

            # store status for this file
            self.validation_data['fileSyntax'].append({'filename': fqfn.name, 'status': status})

    def interactive(self):
        """[App Builder] Run in interactive mode."""
        while True:
            line = sys.stdin.readline().strip()
            if line == 'quit':
                sys.exit()
            elif line == 'validate':
                self.check_syntax()
                self.check_imports()
                self.check_install_json()
                self.check_layout_json()
                self.check_job_json()
                self.print_json()

            # reset validation_data
            self.validation_data = self._validation_data

    def print_json(self):
        """[App Builder] Print JSON output."""
        print(json.dumps({'validation_data': self.validation_data}))

    # TODO: [low] switch to typer echo?
    def _print_file_syntax_results(self):
        """Print file syntax results."""
        if self.validation_data.get('fileSyntax'):
            print(f'\n{c.Style.BRIGHT}{c.Fore.BLUE}Validated File Syntax:')
            print(f'''{c.Style.BRIGHT}{'File:'!s:<60}{'Status:'!s:<25}''')
            for f in self.validation_data.get('fileSyntax'):
                status_color = self.status_color(f.get('status'))
                status_value = self.status_value(f.get('status'))
                print(f"{f.get('filename')!s:<60}{status_color}{status_value!s:<25}")

    def _print_imports_results(self):
        """Print import results."""
        if self.validation_data.get('moduleImports'):
            print(f'\n{c.Style.BRIGHT}{c.Fore.BLUE}Validated Imports:')
            print(f'''{c.Style.BRIGHT}{'File:'!s:<30}{'Module:'!s:<30}{'Status:'!s:<25}''')
            for f in self.validation_data.get('moduleImports'):
                status_color = self.status_color(f.get('status'))
                status_value = self.status_value(f.get('status'))
                print(
                    f'''{f.get('filename')!s:<30}{c.Fore.WHITE}'''
                    f'''{f.get('module')!s:<30}{status_color}{status_value!s:<25}'''
                )

    def _print_schema_results(self):
        """Print schema results."""
        if self.validation_data.get('schema'):
            print(f'\n{c.Style.BRIGHT}{c.Fore.BLUE}Validated Schema:')
            print(f'''{c.Style.BRIGHT}{'File:'!s:<60}{'Status:'!s:<25}''')
            for f in self.validation_data.get('schema'):
                status_color = self.status_color(f.get('status'))
                status_value = self.status_value(f.get('status'))
                print(f'''{f.get('filename')!s:<60}{status_color}{status_value!s:<25}''')

    def _print_layouts_results(self):
        """Print layout results."""
        if self.validation_data.get('layouts'):
            print(f'\n{c.Style.BRIGHT}{c.Fore.BLUE}Validated Layouts:')
            print(f'''{c.Style.BRIGHT}{'Params:'!s:<60}{'Status:'!s:<25}''')
            for f in self.validation_data.get('layouts'):
                status_color = self.status_color(f.get('status'))
                status_value = self.status_value(f.get('status'))
                print(f"{f.get('params')!s:<60}{status_color}{status_value!s:<25}")

    def _print_feed_results(self):
        """Print feed results."""
        if self.validation_data.get('feeds'):
            print(f'\n{c.Style.BRIGHT}{c.Fore.BLUE}Validated Feed Jobs:')
            print(f'''{c.Style.BRIGHT}{'Feeds:'!s:<60}{'Status:'!s:<25}''')
            for f in self.validation_data.get('feeds'):
                status_color = self.status_color(f.get('status'))
                status_value = self.status_value(f.get('status'))
                print(f"{f.get('name')!s:<60}{status_color}{status_value!s:<25}")

    def _print_errors(self):
        """Print errors results."""
        if self.validation_data.get('errors'):
            print('\n')  # separate errors from normal output
        for error in self.validation_data.get('errors'):
            # print all errors
            print(f'* {c.Fore.RED}{error}')

            # ignore exit code
            if not self.ignore_validation:
                self.exit_code = 1

    def print_results(self):
        """Print results."""
        # Validating Syntax
        self._print_file_syntax_results()

        # Validating Imports
        self._print_imports_results()

        # Validating Schema
        self._print_schema_results()

        # Validating Layouts
        self._print_layouts_results()

        # Validating Feed Job Definition Files
        self._print_feed_results()

        self._print_errors()

    @staticmethod
    def status_color(status) -> str:
        """Return the appropriate status color."""
        return c.Fore.GREEN if status else c.Fore.RED

    @staticmethod
    def status_value(status) -> str:
        """Return the appropriate status color."""
        return 'passed' if status else 'failed'
