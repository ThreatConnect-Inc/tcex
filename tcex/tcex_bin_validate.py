#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework Validate Module."""
import argparse
import ast
import imp
import importlib
import json
import os
import sys
import traceback
from collections import deque

import colorama as c
from jsonschema import SchemaError, ValidationError, validate
from stdlib_list import stdlib_list

# Python 2 unicode
if sys.version_info[0] == 2:
    reload(sys)  # noqa: F821; pylint: disable=E0602
    sys.setdefaultencoding('utf-8')  # pylint: disable=E1101

parser = argparse.ArgumentParser()
parser.add_argument(
    '--ignore_validation', action='store_true', help='Do not exit on validation errors.'
)
parser.add_argument('--install_json', help='The install.json file to user during validation.')
parser.add_argument('--interactive', action='store_true', help='Keep running and listen for stdin.')
parser.add_argument('--json_output', action='store_true', help='Do not exit on validation errors.')
args, extra_args = parser.parse_known_args()


class TcExValidate(object):
    """Validate syntax, imports, and schemas.

    * Python and JSON file syntax
    * Python import modules
    * install.json schema
    * layout.json schema
    """

    def __init__(self, _args):
        """Init Class properties."""
        self.args = _args
        self.app_path = os.getcwd()
        self.exit_code = 0

        # defaults
        self._app_packages = []
        self.config = {}
        self._schema = None
        self.schema_file = 'tcex_json_schema.json'
        self.validation_data = self._validation_data

        # initialize colorama
        c.init(autoreset=True, strip=False)

    @property
    def _validation_data(self):
        return {'errors': [], 'fileSyntax': [], 'moduleImports': [], 'schema': []}

    def check_ast(self, app_path=None):
        """Run ast on each Python file.

        Args:
            app_path (str, optional): Defaults to None. The path of Python files.
        """

        app_path = app_path or '.'
        error = False

        for filename in sorted(os.listdir(app_path)):
            errors = []
            status = 'passed'
            status_color = c.Fore.GREEN
            if filename.endswith('.py'):
                try:
                    with open(filename, 'rb') as f:
                        ast.parse(f.read(), filename=filename)
                except SyntaxError:
                    status = 'failed'
                    status_color = c.Fore.RED
                    errors = traceback.format_exc().split('\n')[-5:-2]
                    error = True

            elif filename.endswith('.json'):
                try:
                    with open(filename, 'r') as fh:
                        json.load(fh)
                except Exception:
                    status = 'failed'
                    status_color = c.Fore.RED
                    error = True
            else:
                # skip unsupported file types
                continue

            # store status for this file
            self.validation_data['fileSyntax'].append(
                {
                    'filename': filename,
                    'status_color': status_color,
                    'status': status,
                    'errors': errors,
                }
            )

        if error:
            self.validation_data['errors'].append(
                'Build failed due to file(s) with invalid syntax.'
            )

    def check_imports(self):
        """Check the projects top level directory for missing imports.

        This method will check only files ending in **.py** and does not handle imports validation
        for sub-directories.
        """
        modules = []
        missing_modules = []
        for file in sorted(os.listdir(self.app_path)):
            if not file.endswith('.py'):
                continue

            fq_path = os.path.join(self.app_path, file)
            with open(fq_path, 'rb') as f:
                # TODO: fix this
                code_lines = deque([(f.read(), 1)])

                while code_lines:
                    status = 'missing'
                    status_color = c.Fore.RED

                    code, lineno = code_lines.popleft()  # pylint: disable=W0612
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
                                    if not m_status:
                                        missing_modules.append(m)
                                    modules.append({'file': file, 'module': m, 'status': m_status})
                            elif isinstance(node, ast.ImportFrom):
                                m = node.module.split('.')[0]
                                if self.check_import_stdlib(m):
                                    # stdlib module, not need to proceed
                                    continue
                                m_status = self.check_imported(m)
                                if not m_status:
                                    missing_modules.append(m)
                                modules.append({'file': file, 'module': m, 'status': m_status})
                            else:
                                continue
                    except SyntaxError:
                        pass

        for module_data in modules:
            status = 'passed'
            status_color = c.Fore.GREEN
            if not module_data.get('status'):
                status = 'failed'
                status_color = c.Fore.RED
            # update validation data for module
            self.validation_data['moduleImports'].append(
                {
                    'filename': module_data.get('file'),
                    'module': module_data.get('module'),
                    'status_color': status_color,
                    'status': status,
                    'missing_modules': missing_modules,
                }
            )

        if missing_modules:
            err = (
                'Build failed due to the following missing Python module(s) '
                '(not in requirements.txt?).\n'
            )
            for mm in missing_modules:
                err += '  * {}\n'.format(mm)
            self.validation_data['errors'].append(err)

    @staticmethod
    def check_import_stdlib(module):
        """Check if module is in Python stdlib."""
        if (
            module in stdlib_list('2.7')  # pylint: disable=R0916
            or module in stdlib_list('3.4')
            or module in stdlib_list('3.5')
            or module in stdlib_list('3.6')
            or module in stdlib_list('3.7')
            or module in ['app', 'args', 'playbook_app']
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

        imported = True
        module_info = ('', '', '')
        # TODO: update to a cleaner method that doesn't require importing the module and
        # running inline code.
        try:
            importlib.import_module(module)
            module_info = imp.find_module(module)
        except ImportError:
            imported = False

        # get module path
        module_path = module_info[1]
        description = module_info[2]

        if not description:
            # if description is None or empty string the module could not be imported
            imported = False
        elif not description and not module_path:
            # if description/module_path are None or empty string the module could not be imported
            imported = False
        elif module_path is not None and (
            'dist-packages' in module_path or 'site-packages' in module_path
        ):
            # if dist-packages|site-packages in module_path the import doesn't count
            imported = False
        return imported

    def check_install_json(self):
        """Check all install.json files for valid schema."""
        # the install.json files can't be validates if the schema file is not present
        if self.schema is None:
            return

        if self.args.install_json is not None:
            contents = [self.args.install_json]
        else:
            contents = os.listdir(self.app_path)

        invalid_schema = False
        for install_json in sorted(contents):
            # skip files that are not install.json files
            if 'install.json' not in install_json:
                continue

            error = None
            status = 'passed'
            status_color = c.Fore.GREEN

            if self.schema is not None:
                try:
                    with open(install_json) as fh:
                        data = json.loads(fh.read())
                    validate(data, self.schema)
                except SchemaError as e:
                    # check_ast performs JSON validation of all JSON files. this exception should
                    # never match.
                    status = 'failed'
                    status_color = c.Fore.RED
                    error = e
                    invalid_schema = True
                except ValidationError as e:
                    status = 'failed'
                    status_color = c.Fore.RED
                    error = e.message
                    invalid_schema = True
                except Exception as e:
                    status = 'failed'
                    status_color = c.Fore.RED
                    error = e
                    invalid_schema = True
            # update validation data for module
            self.validation_data['schema'].append(
                {
                    'filename': install_json,
                    'status_color': status_color,
                    'status': status,
                    'invalid_schema': invalid_schema,
                    'error': error,
                }
            )

        if invalid_schema:
            self.validation_data['errors'].append(
                'Build failed due to invalid schema in install.json file(s).'
            )

    def interactive(self):
        """Run in interactive mode."""
        while True:
            line = sys.stdin.readline().strip()
            if line == 'quit':
                sys.exit()
            elif line == 'validate':
                self.check_ast()
                self.check_imports()
                self.check_install_json()
                self.print_json()

            # reset validation_data
            self.validation_data = self._validation_data

    def print_json(self):
        """Print JSON output."""
        print(json.dumps({'validation_data': self.validation_data}))

    def print_results(self):
        """Print results."""
        # Validating Syntax
        print('\n{}{}Validated File Syntax:'.format(c.Style.BRIGHT, c.Fore.BLUE))
        print('{}{!s:<60}{!s:<25}'.format(c.Style.BRIGHT, 'File:', 'Status:'))
        for f in self.validation_data.get('fileSyntax'):
            print(
                '{!s:<60}{}{!s:<25}'.format(
                    f.get('filename'), f.get('status_color'), f.get('status')
                )
            )
            for e in f.get('errors'):
                print('{}{}{}'.format(c.Style.BRIGHT, c.Fore.RED, e))

        # Validating Imports
        print('\n{}{}Validated Imports:'.format(c.Style.BRIGHT, c.Fore.BLUE))
        print('{}{!s:<30}{!s:<30}{!s:<25}'.format(c.Style.BRIGHT, 'File:', 'Module:', 'Status:'))
        for f in self.validation_data.get('moduleImports'):
            print(
                '{!s:<30}{}{!s:<30}{}{!s:<25}'.format(
                    f.get('filename'),
                    c.Fore.WHITE,
                    f.get('module'),
                    f.get('status_color'),
                    f.get('status'),
                )
            )

        # Validating Schema
        print('\n{}{}Validated install.json Schema:'.format(c.Style.BRIGHT, c.Fore.BLUE))
        print('{}{!s:<60}{!s:<25}'.format(c.Style.BRIGHT, 'File:', 'Status:'))
        for f in self.validation_data.get('schema'):
            print(
                '{!s:<60}{}{!s:<25}'.format(
                    f.get('filename'), f.get('status_color'), f.get('status')
                )
            )
            if f.get('error'):
                print('  {}{}{}'.format(c.Style.BRIGHT, c.Fore.RED, f.get('error')))

        # ignore exit code
        if not self.args.ignore_validation:
            if self.validation_data.get('errors'):
                print('\n')  # separate errors from normal output
            # print all errors
            for error in self.validation_data.get('errors'):
                print('{}{}'.format(c.Fore.RED, error))
                self.exit_code = 1

    @property
    def schema(self):
        """Load JSON schema file."""
        if self._schema is None:
            if os.path.isfile(self.schema_file):
                with open(self.schema_file) as fh:
                    self._schema = json.load(fh)
        return self._schema

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
