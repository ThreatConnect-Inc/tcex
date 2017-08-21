#!/usr/bin/env python

""" standard """
import argparse
import json
import os
import re
import shutil
import sys
import traceback
import zipfile
""" third-party """
from jsonschema import SchemaError, ValidationError, validate
""" custom """

parser = argparse.ArgumentParser()
parser.add_argument(
    '--bundle', action='store_true', help='Build a bundle file.')
parser.add_argument(
    '--exclude', action='append', default=[], help='File and directories to exclude from build.')
parser.add_argument(
    '--config', default='tcex.json', help='Build configuration file. (Default: tcex.json)')
# parser.add_argument(
#     '--dryrun', action='store_true', help='Perform a dry run of the build.')
parser.add_argument(
    '--install_json', help='The install.json file name for the App that should be built.')
parser.add_argument(
    '--outdir', default='target', help='Location to write the outfile. (Defaul: target)')
# parser.add_argument(
#     '--validate', help='The install.json file to validate.')
args, extra_args = parser.parse_known_args()

# Load Schema
# schema_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tcex_json_schema.json')


# TODO: Clean this up when time allows
class TcPackage(object):
    """Package the app for deployment

    This method will package the app for deployment to ThreatConnect. Validation of the
    install.json file or files will be automatically run before packaging the app.
    """
    def __init__(self, args):
        """ """
        self._args = args
        self.app_path = os.getcwd()
        self.exit_code = 0

        # defaults
        self._app_packages = []
        self.schema = None
        self.schema_file = 'tcex_json_schema.json'

        # color settings
        self.DEFAULT = '\033[m'
        self.BOLD = '\033[1m'
        # colors
        self.CYAN = '\033[36m'
        self.GREEN = '\033[32m'
        self.MAGENTA = '\033[35m'
        self.RED = '\033[31m'
        self.YELLOW = "\033[33m"
        # bold colors
        self.BOLD_CYAN = '{}{}'.format(self.BOLD, self.CYAN)
        self.BOLD_GREEN = '{}{}'.format(self.BOLD, self.GREEN)
        self.BOLD_MAGENTA = '{}{}'.format(self.BOLD, self.MAGENTA)
        self.BOLD_RED = '{}{}'.format(self.BOLD, self.RED)
        self.BOLD_YELLOW = '{}{}'.format(self.BOLD, self.YELLOW)

        # load config
        self._load_config()

        # load schema
        self._load_schema()

    def _load_config(self):
        """ """
        # load config
        if os.path.isfile(args.config):
            with open(args.config, 'r') as fh:
                try:
                    self.config = json.load(fh).get('package', {})
                except ValueError as e:
                    print('Invalid JSON file {}({}){}.'.format(
                        self.BOLD_RED, e, self.DEFAULT))
                    sys.exit(1)

    def _load_schema(self):
        """Load JSON schema file"""
        if os.path.isfile(self.schema_file):
            with open(self.schema_file) as fh:
                self.schema = json.load(fh)
        else:
            print('{}Packager can not validate install.json without {} schema file.{}'.format(
                self.BOLD_YELLOW, self.schema_file, self.DEFAULT))

    def _load_install_json(self, file):
        """Load install.json file"""
        install_data = {}
        if os.path.isfile(file):
            with open(file) as fh:
                install_data = json.load(fh)
        else:
            print('{}Could not load {} file.{}'.format(
                self.BOLD_YELLOW, file, self.DEFAULT))

        return install_data

    def package(self):
        """Package the App for deployment in TcEx"""

        #
        # create build directory
        #
        tmp_path = os.path.join(self.app_path, self._args.outdir, 'build')
        if not os.path.isdir(tmp_path):
            os.makedirs(tmp_path)

        #
        # temp path and cleanup
        #
        template_app_path = os.path.join(tmp_path, 'template')
        if os.access(template_app_path, os.W_OK):
            # cleanup any previous failed builds
            shutil.rmtree(template_app_path)
        print('Building App Template: {}{}{}'.format(
            self.BOLD_CYAN, template_app_path, self.DEFAULT))

        #
        # build exclude file/directory list
        #
        excludes = [
            self._args.config,
            self._args.outdir,
            '__pycache__',
            '*.git*',
            '*log',
            '*.pyc',
            '*python-version',
            'tcex.json',
            '*install.json'
        ]
        excludes.extend(self._args.exclude)
        excludes.extend(self.config.get('excludes', []))
        patterns = ', '.join(excludes)
        print('Excluding: {}{}{}'.format(
            self.BOLD_CYAN, patterns, self.DEFAULT))

        #
        # copy project directory to temp location to use as template for multiple builds
        #
        ignore_patterns = shutil.ignore_patterns(*excludes)
        shutil.copytree(self.app_path, template_app_path, False, ignore_patterns)

        #
        # build list of app json files
        #
        if self._args.install_json is not None:
            contents = [self._args.install_json]
        else:
            contents = os.listdir(self.app_path)

        # base name of app directory
        base_name = os.path.basename(self.app_path)

        #
        # package app
        #
        for install_json in sorted(contents):
            # skip files that are not install.json files
            if 'install.json' not in install_json:
                continue

            # divider
            print('-' * 100)

            # TODO: need better way to get app name
            if install_json == 'install.json':
                app_name = base_name
            else:
                app_name = install_json.split('.')[0]

            print('Processing: {}{}{}'.format(
                self.BOLD_CYAN, app_name, self.DEFAULT))

            #
            # validate install json
            #
            if self.schema is not None:
                self.validate(install_json)

            #
            # load install json
            #
            ij = self._load_install_json(install_json)
            major_version = ij.get('programVersion', '1').split('.')[0]
            # The name of the folder in the zip is the *key* for an App. This value must
            # remain consistent for the App to upgrade successfully.
            app_name = '{}_v{}.0'.format(app_name, major_version)

            #
            # build app directory
            #
            tmp_app_path = os.path.join(tmp_path, app_name)
            if os.access(tmp_app_path, os.W_OK):
                # cleanup any previous failed builds
                shutil.rmtree(tmp_app_path)
            shutil.copytree(template_app_path, tmp_app_path)

            # Copy install.json
            shutil.copy(install_json, os.path.join(tmp_app_path, 'install.json'))

            # zip file
            self.zip_file(self.app_path, app_name, tmp_path)
            # cleanup build directory
            shutil.rmtree(tmp_app_path)

        # bundle zips
        if len(self._app_packages) > 0:
            self.bundle(self.config.get('bundle_name', base_name))

    def zip_file(self, app_path, app_name, tmp_path):
        """ """
        # zip build directory
        zip_file = os.path.join(app_path, self._args.outdir, app_name)
        zip_file_zip = '{}.zip'.format(zip_file)
        print('Creating zip: {}{}{}'.format(
            self.BOLD_CYAN, os.path.basename(zip_file_zip), self.DEFAULT))
        # zip_file_tcx = '{}.tcx'.format(zip_file)
        shutil.make_archive(zip_file, 'zip', tmp_path, app_name)
        # shutil.move(zip_file_zip, zip_file_tcx)
        self._app_packages.append(zip_file_zip)

    def bundle(self, bundle_name):
        """ """
        if self._args.bundle or self.config.get('bundle', False):
            print('-' * 100)
            if self.config.get('bundle_packages') is not None:
                for bundle in self.config.get('bundle_packages', []):
                    bundle_name = bundle.get('name')
                    bundle_patterns = bundle.get('patterns')

                    bundle_apps = []
                    for app in self._app_packages:
                        for app_pattern in bundle_patterns:
                            p = re.compile(app_pattern, re.IGNORECASE)
                            if p.match(app):
                                bundle_apps.append(app)

                    # bundle app in zip
                    if len(bundle_apps) > 0:
                        self.bundle_apps(bundle_name, bundle_apps)
            else:
                self.bundle_apps(bundle_name, self._app_packages)

    def bundle_apps(self, bundle_name, bundle_apps):
        """ """
        bundle_file = os.path.join(self.app_path, self._args.outdir, '{}-bundle.zip'.format(bundle_name))
        print('Creating bundle: {}{}{}'.format(
            self.BOLD_CYAN, os.path.basename(bundle_file), self.DEFAULT))
        z = zipfile.ZipFile(bundle_file, 'w')
        for app in bundle_apps:
            print('  Adding: {}{}{}'.format(
                self.BOLD_GREEN, os.path.basename(app), self.DEFAULT))
            z.write(app, os.path.basename(app))
        z.close

    def validate(self, install_json):
        """Validate install.json file for required parameters"""

        # install.json validation
        try:
            with open(install_json) as fh:
                data = json.loads(fh.read())
            validate(data, self.schema)
            print('Validating: {}{}{} {}({}){}'.format(
                self.BOLD_CYAN, install_json, self.DEFAULT, self.BOLD_GREEN, 'valid', self.DEFAULT))
        except SchemaError as e:
            print('Validating: {}{}{} {}({}){}'.format(
                self.BOLD_CYAN, install_json, self.DEFAULT, self.BOLD_RED, e, self.DEFAULT))
        except ValidationError as e:
            print('Validating: {}{}{} {}({}){}'.format(
                self.BOLD_CYAN, install_json, self.DEFAULT, self.BOLD_RED, e, self.DEFAULT))


if __name__ == '__main__':
    try:
        tcp = TcPackage(args)
        tcp.package()
        sys.exit(tcp.exit_code)
    except Exception as e:
        # TODO: Update this, possibly raise
        print(traceback.format_exc())
        sys.exit(1)