#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework Package Module."""
import json
import os
import re
import shutil
import uuid
import zipfile

import colorama as c

from ..app_config_object import InstallJson
from .bin import Bin


class Package(Bin):
    """Package ThreatConnect Job or Playbook App for deployment.

    This method will package the app for deployment to ThreatConnect. Validation of the
    install.json file or files will be automatically run before packaging the app.

    Args:
        _args (namespace): The argparser args Namespace.
    """

    def __init__(self, _args):
        """Initialize Class properties."""
        super().__init__(_args)

        # properties
        self.features = ['aotExecutionEnabled', 'secureParams']

        # properties
        self._app_packages = []
        self.package_data = {'errors': [], 'updates': [], 'bundle': [], 'package': []}
        self.validation_data = {}

    @property
    def _build_excludes(self):
        """Return a list of files and folders that should be excluded during the build process."""
        return [
            'tcex.json',
            self.args.outdir,
            '__pycache__',
            '.cache',  # local cache directory
            '.c9',  # C9 IDE
            '.coverage',  # coverage file
            '.coveragerc',  # coverage configuration file file
            '.git',  # git directory
            '.gitmodules',  # git modules
            '.idea',  # PyCharm
            '.pytest_cache',  # pytest cache directory
            '*.iml',  # PyCharm files
            '*.pyc',  # any pyc file
            '.python-version',  # pyenv
            '.vscode',  # Visual Studio Code
            'artifacts',  # pytest in BB Pipelines
            'assets',  # pytest in BB Pipelines
            'local-*',  # log directory
            'log',  # log directory
            'test-reports',  # pytest in BB Pipelines
            'tests',  # pytest test directory
        ]

    def _update_install_json(self, install_json):
        """Update install.json file.

        Args:
            install_json (dict): The contents of the install.json file.

        Returns:
            dict, bool: The contents of the install.json file and boolean value that is True if
                an update was made.
        """
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

        # all App should have an appId to uniquely identify the App. this is not intended to be
        # used by core to identify an App.  using appId + major Version could be used for unique
        # App identification in core in a future release.
        if install_json.get('appId') is None:
            install_json['appId'] = str(
                uuid.uuid5(uuid.NAMESPACE_X500, os.path.basename(os.getcwd()).lower())
            )
            updated = True

        return install_json, updated

    def _write_install_json(self, filename, install_json):
        """Write install.json file.

        Some projects have bundles App with multiple install.json files.  Typically these files are
        prefixed with the App name (e.g., MyApp.install.json).

        Args:
            filename (str): The install.json file name.
            install_json (dict): The contents of the install.json file.
        """
        # TODO: why check if it exists?
        if os.path.isfile(filename):
            with open(filename, 'w') as fh:
                json.dump(install_json, fh, indent=4, sort_keys=True)
        else:
            err = f'Could not write file: {filename}.'
            # update package data
            self.package_data['errors'].append(err)

    def bundle(self, bundle_name):
        """Bundle multiple Job or Playbook Apps into a single zip file.

        Args:
            bundle_name (str): The output name of the bundle zip file.
        """
        if self.args.bundle or self.tcex_json.get('package', {}).get('bundle', False):
            if self.tcex_json.get('package', {}).get('bundle_packages') is not None:
                for bundle in self.tcex_json.get('package', {}).get('bundle_packages') or []:
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
        """Bundle multiple Job or Playbook Apps (.tcx files) into a single zip file.

        Args:
            bundle_name (str): The output name of the bundle zip file.
            bundle_apps (list): A list of Apps to include in the bundle.
        """
        bundle_file = os.path.join(self.app_path, self.args.outdir, f'{bundle_name}-bundle.zip')
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
                hash_file = f'.git/refs/heads/{branch}'
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
        excludes = list(self._build_excludes)
        excludes.extend(self.args.exclude)
        excludes.extend(self.tcex_json.get('package', {}).get('excludes', []))

        # update package data
        self.package_data['package'].append({'action': 'Excluded Files:', 'output': excludes})

        # copy project directory to temp location to use as template for multiple builds
        ignore_patterns = shutil.ignore_patterns(*excludes)
        shutil.copytree(self.app_path, template_app_path, False, ignore_patterns)

        # build list of app json files
        contents = os.listdir(self.app_path)
        if self.args.install_json is not None:
            contents = [self.args.install_json]

        # package app
        for install_json_name in sorted(contents):
            # skip files that are not install.json files
            if 'install.json' not in install_json_name:
                continue

            # load install json
            ij = InstallJson(install_json_name)

            # automatically update install.json for feature sets supported by the SDK
            ij, ij_modified = self._update_install_json(ij.contents)

            # write update install.json
            if ij_modified:
                self._write_install_json(install_json_name, ij)

            # get App Name from config, install.json prefix or directory name.
            app_name = self.app_name(install_json_name)

            # update package data
            self.package_data['package'].append({'action': 'App Name:', 'output': app_name})

            # find a usable app version
            app_version = self.app_version(ij)

            # update package data
            self.package_data['package'].append(
                {'action': 'App Version:', 'output': f'{app_version}'}
            )

            # !!! The name of the folder in the zip is the *key* for an App. This value must
            # !!! remain consistent for the App to upgrade successfully.
            app_name_version = f'{app_name}_{app_version}'

            # build app directory
            tmp_app_path = os.path.join(tmp_path, app_name_version)
            if os.access(tmp_app_path, os.W_OK):
                # cleanup any previous failed builds
                shutil.rmtree(tmp_app_path)
            shutil.copytree(template_app_path, tmp_app_path)

            # Copy install.json
            # TODO: do we need copy if writing the data in the next step?
            shutil.copy(install_json_name, os.path.join(tmp_app_path, 'install.json'))

            # Update commit hash after install.json has been copied.
            if self.commit_hash is not None:
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
            self.bundle(self.tcex_json.get('package', {}).get('bundle_name', app_name))

    def app_name(self, install_json_name):
        """Return the app package name without version.

        1. Use the prefix on the install.json file (bundled Apps).
        2. Use the app_name field from the tcex.json file.
        3. Use the app directory name. This option should not be used.
        """
        if install_json_name != 'install.json':
            return install_json_name.split('.')[0]
        return self.tcex_json.get('package', {}).get('app_name', os.path.basename(self.app_path))

    def app_version(self, ij):
        """Return the app version "v1".

        1. Use app_version value from tcex.json if available. Typicall version is major only
           (e.g., v1), but from older Apps it could have minor version.
        2. Use major version from programVersion field in install.json if available.
        3. Default to '1.0.0' updated to major version only ('v1').
        """
        major_version = ij.get('programVersion', '1.0.0').split('.')[0]
        return str(self.tcex_json.get('package', {}).get('app_version', f'v{major_version}'))

    def print_json(self):
        """Print JSON output containing results of the package command."""
        print(
            json.dumps({'package_data': self.package_data, 'validation_data': self.validation_data})
        )

    def print_results(self):
        """Print results of the package command."""
        # Updates
        if self.package_data.get('updates'):
            print(f'\n{c.Style.BRIGHT}{c.Fore.BLUE}Updates:')
            for p in self.package_data['updates']:
                print(
                    f"{p.get('action')!s:<20}{c.Style.BRIGHT}{c.Fore.CYAN} {p.get('output')!s:<50}"
                )

        # Packaging
        print(f'\n{c.Style.BRIGHT}{c.Fore.BLUE}Package:')
        for p in self.package_data['package']:
            if isinstance(p.get('output'), list):
                n = 5
                list_data = p.get('output')
                print(
                    f"{p.get('action'):<20}{c.Style.BRIGHT}{c.Fore.CYAN} "
                    f"{', '.join(p.get('output')[:n]):<50}"
                )
                del list_data[:n]
                for data in [
                    list_data[i : i + n] for i in range(0, len(list_data), n)  # noqa: E203
                ]:
                    print(f"{''!s:<20}{c.Style.BRIGHT}{c.Fore.CYAN} {', '.join(data)!s:<50}")

            else:
                print(
                    f"{p.get('action')!s:<20}{c.Style.BRIGHT}{c.Fore.CYAN} {p.get('output')!s:<50}"
                )

        # Bundle
        if self.package_data.get('bundle', False):
            print(f'\n{c.Style.BRIGHT}{c.Fore.BLUE}Bundle:')
            for p in self.package_data['bundle']:
                print(
                    f"{p.get('action')!s:<20}{c.Style.BRIGHT}{c.Fore.CYAN} {p.get('output')!s:<50}"
                )

        # ignore exit code
        if not self.args.ignore_validation:
            print('\n')  # separate errors from normal output
            # print all errors
            for error in self.package_data.get('errors'):
                print(f'{c.Fore.RED}{error}')
                self.exit_code = 1

    def zip_file(self, app_path, app_name, tmp_path):
        """Zip the App with tcex extension.

        Args:
            app_path (str): The path of the current project.
            app_name (str): The name of the App.
            tmp_path (str): The temp output path for the zip.
        """
        # zip build directory
        zip_file = os.path.join(app_path, self.args.outdir, app_name)
        zip_file_zip = f'{zip_file}.zip'
        zip_file_tcx = f'{zip_file}.tcx'
        shutil.make_archive(zip_file, 'zip', tmp_path, app_name)
        shutil.move(zip_file_zip, zip_file_tcx)
        self._app_packages.append(zip_file_tcx)
        # update package data
        self.package_data['package'].append({'action': 'App Package:', 'output': zip_file_tcx})
