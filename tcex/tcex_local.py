""" standard """
import argparse
import json
import os
import re
import shutil
import sys
import time
import zipfile
from setuptools.command import easy_install

""" third-party """
try:
    from jsonschema import SchemaError, ValidationError, validate
except ImportError as e:
    print('Error: {}'.format(e))
    print('Try app.py --lib or adding jsonschema to setup.py')

# Load Schema
schema_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tcex_json_schema.json')
with open(schema_file) as fh:
    schema = json.load(fh)

class TcExLocal:
    """
    Class to support running local instance TcEx Apps
    """

    def __init__(self):
        """
        """
        # Required Argument
        self._parsed = False  # only parse once from user
        self._parser = argparse.ArgumentParser()

        self._install_json = {}
        # self.load_install_json()
        self._app_packages = []

        self._required_arguments()
        self._args, unknown = self._parser.parse_known_args()

    @property
    def args(self):
        """The parsed args

        Returns:
            (namespace): ArgParser parsed arguments
        """
        if not self._parsed:
            self._args, unknown = self._parser.parse_known_args()
            self._parsed = True

        return self._args

    @property
    def parser(self):
        """The ArgParser parser object

        Returns:
            (ArgumentParser): TcEx local parser object
        """
        return self._parser

    @property
    def run(self):
        """Execute the script with arguments provided in tc.json."""

        if not os.path.isfile(self._args.script):
            msg = 'Provided script file does not exist ({0}).'
            msg.format(self._args.script)
            self._exit(msg, 1)

        command = '{0} . {1} {2}'.format(
            self._args.python,
            self._args.script.split('.')[0],
            self._parameters)
        os.system(command)

        msg = 'Executed: {0}'.format(command)
        self._exit(msg)

    @property
    def _config(self):
        """Configuration value retrieve from JSON configuration file

        Returns:
            (dict): Dictionary of configuration parameters
        """
        if not os.path.isfile(self._args.config):
            msg = 'Provided config file does not exist ({0}).'
            msg.format(self._args.config)
            self._exit(msg, 1)

        with open(self._args.config) as data_file:
            # return json.load(data_file)
            data = json.load(data_file)

        test_section = self._args.test
        if self._args.test is None:
            test_section = 'default'

        data = data.get(test_section)
        if data is None:
            msg = 'The tc.json configuration test named {} was not found.'.format(test_section)
            self._exit(msg, 1)

        return data

    def _exit(self, message, code=0):
        """Exit the script

        Args:
            message (str): An exit message
            code (Optional [int]): The exit status code
        """
        print(message)
        sys.exit(code)

    @property
    def _parameters(self):
        """Build CLI arguments to pass to script on the command line.

        This method takes the json data and covert it to CLI args for the execution
        of the script.

        Returns:
            (str): A string containing all parameter to pass to script
        """
        parameters = ' '
        for config_key, config_val in self._config.items():
            if isinstance(config_val, bool):
                if config_val:
                    parameters += '--{0} '.format(config_key)
            elif isinstance(config_val, list):
                for val in config_val:
                    parameters += '--{0} {1} '.format(
                        config_key, self._wrap(val))
            elif isinstance(config_val, (int, float, long, str, unicode)):
                parameters += '--{0} {1} '.format(
                    config_key, self._wrap(str(config_val)))
            else:
                msg = '{0} error: ({1}) is not of Type list or str. ({2})'
                msg.format(type(config_val), config_val)
                self._exit(msg, 1)

        return parameters

    def _required_arguments(self):
        """Required arguments for this class to function"""

        # actions
        self._parser.add_argument(
            '--lib', action='store_true', help='Gen the libs')
        self._parser.add_argument(
            '--package', action='store_true', help='Package the app')
        self._parser.add_argument(
            '--run', action='store_true', help='Run the app')
        self._parser.add_argument(
            '--validate', action='store_true', help='Validate JSON configs')

        # run args
        self._parser.add_argument(
            '--config', help='The configuration file', default='tc.json')
        self._parser.add_argument(
            '--python', help='The python executable', default='python')
        self._parser.add_argument(
            '--script', help='The script to be executed', required=False)
        self._parser.add_argument(
            '--test', help='The test to be executed', default=None)

        # validate args
        self._parser.add_argument(
            '--install_json', help='The install.json filename', default='install.json')

        # package args
        self._parser.add_argument(
            '--collection', help='Build app collection', action='store_true')
        self._parser.add_argument(
            '--zip_out', help='The zip output path', default=None)

    @staticmethod
    def _wrap(data):
        """Wrap any parameters that contain spaces

        Returns:
            (string): String containing parameters wrapped in double quotes
        """
        if len(re.findall(r'[!\-\s\$]{1,}', data)) > 0:
            data = '\'{}\''.format(data)
        return data

    ############################################################################
    # bcs - add comment and cleanup
    ############################################################################

    def load_install_json(self):
        """Read the install.json file"""
        with open('install.json') as fh:
            self._install_json = json.load(fh)

    def gen_lib(self):
        """Build libs locally for app

        Using the setup.py this method will install all required python modules locally
        to be used for local testing.
        """
        lib_directory = 'lib_{}.{}.{}'.format(
                sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
        app_path = os.getcwd()
        app_name = os.path.basename(app_path)

        lib_path = os.path.join(app_path, lib_directory)
        if not os.path.isdir(lib_path):
            os.mkdir(lib_path)

        os.environ['PYTHONPATH'] = '{0}'.format(lib_path)
        stdout = sys.stdout
        stderr = sys.stderr
        try:
            with open(os.path.join(app_path, '{}-libs.log'.format(app_name)), 'w') as log:
                sys.stdout = log
                sys.stderr = log
                easy_install.main(['-axZ', '-d', lib_path, str(app_path)])
        except SystemExit as e:
            raise Exception(str(e))
        finally:
            sys.stdout = stdout
            sys.stderr = stderr

        if len(os.listdir(lib_path)) == 0:
            raise Exception('Encountered error running easy_install for {}.  Check log file for details.'.format(app_name))

        build_path = os.path.join(app_path, 'build')
        if os.access(build_path, os.W_OK):
            shutil.rmtree(build_path)
        temp_path = os.path.join(app_path, 'temp')
        if os.access(temp_path, os.W_OK):
            shutil.rmtree(temp_path)

    def package(self):
        """Package the app for deployment

        This method will package the app for deployment to ThreatConnect.  It will download
        all required dependencies and include them in the package.  Validating of the
        install.json file or files will be automatically run before packaging the app.
        """

        # bcs - other options
        # app_name = self._install_json['displayName'].replace(' ', '_')
        # app_path = os.path.dirname(os.path.realpath(__file__))

        lib_directory = 'lib_{}.{}.{}'.format(
            sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
        app_path = os.getcwd()
        contents = os.listdir(app_path)

        # create build directory
        tmp_path = os.path.join(os.sep, 'tmp', 'tcex_builds')
        if not os.path.isdir(tmp_path):
            os.mkdir(tmp_path)

        # copy project directory to temp location to use as template for multiple builds
        base_name = os.path.basename(app_path)
        template_app_path = os.path.join(tmp_path, base_name)
        if os.access(template_app_path, os.W_OK):
            # cleanup any previous failed builds
            shutil.rmtree(template_app_path)

        # ignore unwanted files from build to ensure app packages are minimum size
        ignore_patterns = shutil.ignore_patterns(
            '*.git*', 'lib', '*log', '*python-version', 'tc.json', '*.tcx')
        shutil.copytree(app_path, template_app_path, False, ignore_patterns)

        for install_json in contents:
            if 'install.json' not in install_json:
                continue

            self.validate(install_json)

            base_name = os.path.basename(app_path)
            if install_json == 'install.json':
                app_name = base_name
            else:
                app_name = install_json.split('.')[0]

            tmp_app_path = os.path.join(tmp_path, app_name)
            if tmp_app_path != template_app_path:
                shutil.copytree(template_app_path, tmp_app_path)

            lib_path = os.path.join(tmp_app_path, lib_directory)
            if os.access(lib_path, os.W_OK):
                shutil.rmtree(lib_path)
            os.mkdir(lib_path)

            os.environ['PYTHONPATH'] = '{0}'.format(lib_path)
            stdout = sys.stdout
            stderr = sys.stderr
            try:
                with open(os.path.join(app_path, '{}-package.log'.format(app_name)), 'w') as log:
                    sys.stdout = log
                    sys.stderr = log
                    easy_install.main(['-axZ', '-d', lib_path, str(tmp_app_path)])
            except SystemExit as e:
                raise Exception(str(e))
            finally:
                sys.stdout = stdout
                sys.stderr = stderr

            if len(os.listdir(lib_path)) == 0:
                raise Exception('Encountered error running easy_install for {}.  Check log file for details.'.format(app_name))

            # cleanup
            git_path = os.path.join(tmp_app_path, '.git')
            if os.access(git_path, os.W_OK):
                shutil.rmtree(git_path)
            build_path = os.path.join(tmp_app_path, 'build')
            if os.access(build_path, os.W_OK):
                shutil.rmtree(build_path)

            # rename install.json
            if install_json != 'install.json':
                install_json_path = os.path.join(tmp_app_path, install_json)
                if os.access(build_path, os.W_OK):
                    shutil.rmtree(install_json_path)
                shutil.move(install_json_path, os.path.join(tmp_app_path, 'install.json'))

            # zip build directory
            zip_file = os.path.join(app_path, app_name)
            if self._args.zip_out is not None and os.access(self._args.zip_out, os.W_OK):
                zip_file = os.path.join(self._args.zip_out, app_name)

            zip_file_zip = '{}.zip'.format(zip_file)
            zip_file_tcx = '{}.tcx'.format(zip_file)
            shutil.make_archive(zip_file, 'zip', tmp_path, app_name)
            shutil.move(zip_file_zip, zip_file_tcx)
            self._app_packages.append(zip_file_tcx)

            # cleanup build directory
            if install_json != 'install.json':
                shutil.rmtree(tmp_app_path)

        if self._args.collection and len(self._app_packages) > 0:
            collection_file = '{}.zip'.format(base_name)
            z = zipfile.ZipFile(collection_file, 'w')
            for app in self._app_packages:
                z.write(app, os.path.basename(app))
            z.close
            if self._args.zip_out is not None and os.access(self._args.zip_out, os.W_OK):
                collection_zip = os.path.join(self._args.zip_out, collection_file)
                shutil.move(collection_file, collection_zip)

        # cleanup template directory
        if os.access(template_app_path, os.W_OK):
            shutil.rmtree(template_app_path)

    def validate(self, install_json):
        """Validate install.json file for required parameters"""

        # install.json validation
        try:
            with open(install_json) as fh:
                data = json.loads(fh.read())
            validate(data, schema)
            print('{} is valid'.format(install_json))
        except SchemaError as e:
            print('{} is invalid "{}"'.format(install_json, e))
        except ValidationError as e:
            print('{} is invalid "{}"'.format(install_json, e))
