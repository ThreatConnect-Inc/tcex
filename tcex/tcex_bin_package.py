#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework Package Module."""
import json
import os
import re
import shutil
import sys
import zipfile
from builtins import range
from collections import OrderedDict

import colorama as c


class TcExPackage(object):
    """Package the App for deployment.

    This method will package the app for deployment to ThreatConnect. Validation of the
    install.json file or files will be automatically run before packaging the app.
    """

    def __init__(self, _args):
        """Init Class properties."""
        self.args = _args
        self.app_path = os.getcwd()
        self.exit_code = 0
        self.features = ['secureParams', 'aotExecutionEnabled']

        # defaults
        self._app_packages = []
        self.config = {}
        self.package_data = {'errors': [], 'updates': [], 'bundle': [], 'package': []}
        self.validation_data = {}

        # initialize colorama
        c.init(autoreset=True, strip=False)

        # load config
        self._load_config()

    def _load_config(self):
        """Load the tcex.conf file."""
        # load config
        if os.path.isfile(self.args.config):
            with open(self.args.config, 'r') as fh:
                try:
                    self.config = json.load(fh).get('package', {})
                except ValueError as e:
                    err = 'Invalid JSON File ({}).'.format(e)
                    # update package data
                    print('{}{}({})'.format(c.Style.BRIGHT, c.Fore.RED, err))
                    sys.exit(1)

    def _load_install_json(self, file):
        """Load install.json file."""
        install_data = {}
        if os.path.isfile(file):
            with open(file) as fh:
                install_data = json.load(fh, object_pairs_hook=OrderedDict)
        else:
            # update package data
            self.package_data['errors'].append('Could not load {} file.'.format(file))

        return install_data

    def _update_install_json(self, install_json):
        """Write install.json file."""
        updated = False
        # Update features
        install_json.setdefault('features', [])
        for feature in self.features:
            if feature not in install_json.get('features'):
                install_json['features'].append(feature)
                updated = True
                # update package data
                self.package_data['updates'].append(
                    {'action': 'Updated Feature:', 'output': feature}
                )

        return install_json, updated

    def _write_install_json(self, filename, install_json):
        """Write install.json file."""
        # TODO: why check if it exists?
        if os.path.isfile(filename):
            with open(filename, 'w') as fh:
                json.dump(install_json, fh, indent=4, sort_keys=True)
        else:
            err = 'Could not write file: {}.'.format(filename)
            # update package data
            self.package_data['errors'].append(err)

    def bundle(self, bundle_name):
        """Bundle Apps."""
        if self.args.bundle or self.config.get('bundle', False):
            if self.config.get('bundle_packages') is not None:
                for bundle in self.config.get('bundle_packages') or []:
                    bundle_name = bundle.get('name')
                    bundle_patterns = bundle.get('patterns')

                    bundle_apps = []
                    for app in self._app_packages:
                        for app_pattern in bundle_patterns:
                            p = re.compile(app_pattern, re.IGNORECASE)
                            if p.match(app):
                                bundle_apps.append(app)

                    # bundle app in zip
                    if bundle_apps:
                        self.bundle_apps(bundle_name, bundle_apps)
            else:
                self.bundle_apps(bundle_name, self._app_packages)

    def bundle_apps(self, bundle_name, bundle_apps):
        """Bundle zip (tcx) file."""
        bundle_file = os.path.join(
            self.app_path, self.args.outdir, '{}-bundle.zip'.format(bundle_name)
        )
        z = zipfile.ZipFile(bundle_file, 'w')
        for app in bundle_apps:
            # update package data
            self.package_data['bundle'].append(
                {'action': 'Adding App:', 'output': os.path.basename(app)}
            )
            z.write(app, os.path.basename(app))

        # update package data
        self.package_data['bundle'].append(
            {'action': 'Created Bundle:', 'output': os.path.basename(bundle_file)}
        )
        z.close()

    @property
    def commit_hash(self):
        """Return the current commit hash if available.

        This is not a required task so best effort is fine. In other words this is not guaranteed
        to work 100% of the time.
        """
        commit_hash = None
        branch = None
        branch_file = '.git/HEAD'  # ref: refs/heads/develop

        # get current branch
        if os.path.isfile(branch_file):
            with open(branch_file, 'r') as f:
                try:
                    branch = f.read().strip().split('/')[2]
                except IndexError:
                    pass

            # get commit hash
            if branch:
                hash_file = '.git/refs/heads/{}'.format(branch)
                if os.path.isfile(hash_file):
                    with open(hash_file, 'r') as f:
                        commit_hash = f.read().strip()
        return commit_hash

    def package(self):
        """Build the App package for deployment to ThreatConnect Exchange."""
        # create build directory
        tmp_path = os.path.join(self.app_path, self.args.outdir, 'build')
        if not os.path.isdir(tmp_path):
            os.makedirs(tmp_path)

        # temp path and cleanup
        template_app_path = os.path.join(tmp_path, 'template')
        if os.access(template_app_path, os.W_OK):
            # cleanup any previous failed builds
            shutil.rmtree(template_app_path)
        # update package data
        self.package_data['package'].append(
            {'action': 'Template Directory:', 'output': template_app_path}
        )

        # build exclude file/directory list
        excludes = [
            self.args.config,
            self.args.outdir,
            '__pycache__',
            '.c9',  # C9 IDE
            '.git',  # git directory
            '.gitmodules',  # git modules
            '*.pyc',  # any pyc file
            '.python-version',  # pyenv
            '.vscode',  # Visual Studio Code
            'log',  # log directory
        ]
        excludes.extend(self.args.exclude)
        excludes.extend(self.config.get('excludes', []))
        # update package data
        self.package_data['package'].append({'action': 'Excluded Files:', 'output': excludes})

        # copy project directory to temp location to use as template for multiple builds
        ignore_patterns = shutil.ignore_patterns(*excludes)
        shutil.copytree(self.app_path, template_app_path, False, ignore_patterns)

        # build list of app json files
        if self.args.install_json is not None:
            contents = [self.args.install_json]
        else:
            contents = os.listdir(self.app_path)

        # package app
        for install_json in sorted(contents):
            # skip files that are not install.json files
            if 'install.json' not in install_json:
                continue

            # get App Name from config, install.json prefix or directory name.
            if install_json == 'install.json':
                app_name = self.config.get('app_name', os.path.basename(self.app_path))
            else:
                app_name = install_json.split('.')[0]

            # update package data
            self.package_data['package'].append({'action': 'App Name:', 'output': app_name})

            # load install json
            ij = self._load_install_json(install_json)

            # automatically update install.json for feature sets supported by the SDK
            ij, ij_modified = self._update_install_json(ij)

            # write update install.json
            if ij_modified:
                self._write_install_json(install_json, ij)

            # find a usable app version
            program_version = ij.get('programVersion', '1.0.0').split('.')
            major_version = program_version[0]
            try:
                minor_version = program_version[1]
            except IndexError:
                minor_version = 0
            app_version = '{}'.format(
                self.config.get('app_version', 'v{}.{}'.format(major_version, minor_version))
            )

            # update package data
            self.package_data['package'].append(
                {'action': 'App Version:', 'output': 'v{}.{}'.format(major_version, minor_version)}
            )

            # !!! The name of the folder in the zip is the *key* for an App. This value must
            # !!! remain consistent for the App to upgrade successfully.
            app_name_version = '{}_{}'.format(app_name, app_version)

            # build app directory
            tmp_app_path = os.path.join(tmp_path, app_name_version)
            if os.access(tmp_app_path, os.W_OK):
                # cleanup any previous failed builds
                shutil.rmtree(tmp_app_path)
            shutil.copytree(template_app_path, tmp_app_path)

            # Copy install.json
            # TODO: do we need copy if writing the data in the next step?
            shutil.copy(install_json, os.path.join(tmp_app_path, 'install.json'))

            # Update commit hash after install.json has been copied.
            ij.setdefault('commitHash', self.commit_hash)
            self._write_install_json(os.path.join(tmp_app_path, 'install.json'), ij)

            # update package data
            self.package_data['package'].append(
                {'action': 'Commit Hash:', 'output': self.commit_hash}
            )

            # zip file
            self.zip_file(self.app_path, app_name_version, tmp_path)

            # cleanup build directory
            shutil.rmtree(tmp_app_path)

        # bundle zips (must have more than 1 app)
        if len(self._app_packages) > 1:
            self.bundle(self.config.get('bundle_name', app_name))

    def print_json(self):
        """Print JSON output."""
        print(
            json.dumps({'package_data': self.package_data, 'validation_data': self.validation_data})
        )

    def print_results(self):
        """Print results."""
        # Updates
        if self.package_data.get('updates'):
            print('\n{}{}Updates:'.format(c.Style.BRIGHT, c.Fore.BLUE))
            for p in self.package_data['updates']:
                print(
                    '{!s:<20}{}{} {!s:<50}'.format(
                        p.get('action'), c.Style.BRIGHT, c.Fore.CYAN, p.get('output')
                    )
                )

        # Packaging
        print('\n{}{}Package:'.format(c.Style.BRIGHT, c.Fore.BLUE))
        for p in self.package_data['package']:
            if isinstance(p.get('output'), list):
                n = 5
                list_data = p.get('output')
                print(
                    '{!s:<20}{}{} {!s:<50}'.format(
                        p.get('action'), c.Style.BRIGHT, c.Fore.CYAN, ', '.join(p.get('output')[:n])
                    )
                )
                del list_data[:n]
                for data in [
                    list_data[i : i + n] for i in range(0, len(list_data), n)  # noqa: E203
                ]:
                    print(
                        '{!s:<20}{}{} {!s:<50}'.format(
                            '', c.Style.BRIGHT, c.Fore.CYAN, ', '.join(data)
                        )
                    )

            else:
                print(
                    '{!s:<20}{}{} {!s:<50}'.format(
                        p.get('action'), c.Style.BRIGHT, c.Fore.CYAN, p.get('output')
                    )
                )

        # Bundle
        if self.package_data.get('bundle'):
            print('\n{}{}Bundle:'.format(c.Style.BRIGHT, c.Fore.BLUE))
            for p in self.package_data['bundle']:
                print(
                    '{!s:<20}{}{} {!s:<50}'.format(
                        p.get('action'), c.Style.BRIGHT, c.Fore.CYAN, p.get('output')
                    )
                )

        # ignore exit code
        if not self.args.ignore_validation:
            print('\n')  # separate errors from normal output
            # print all errors
            for error in self.package_data.get('errors'):
                print('{}{}'.format(c.Fore.RED, error))
                self.exit_code = 1

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

    def zip_file(self, app_path, app_name, tmp_path):
        """Zip the App with tcex extension."""
        # zip build directory
        zip_file = os.path.join(app_path, self.args.outdir, app_name)
        zip_file_zip = '{}.zip'.format(zip_file)
        zip_file_tcx = '{}.tcx'.format(zip_file)
        shutil.make_archive(zip_file, 'zip', tmp_path, app_name)
        shutil.move(zip_file_zip, zip_file_tcx)
        self._app_packages.append(zip_file_tcx)
        # update package data
        self.package_data['package'].append({'action': 'App Package:', 'output': zip_file_tcx})
