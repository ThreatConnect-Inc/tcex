#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework Package Module."""
# standard library
import json
import os
import re
import shutil
import zipfile

# third-party
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

    def bundle(self, bundle_name):
        """Bundle multiple Job or Playbook Apps into a single zip file.

        Args:
            bundle_name (str): The output name of the bundle zip file.
        """
        if self.args.bundle or self.tj.package_bundle:
            if self.tj.package_bundle_packages:
                for bundle in self.tj.package_bundle_packages:
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
        excludes.extend(self.tj.package_excludes)

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
            if not install_json_name.endswith('install.json'):
                continue

            # load install json
            ij = InstallJson(install_json_name)

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

            # load template install json
            ij_template = InstallJson(path=tmp_app_path)

            # automatically update install.json in template directory
            ij_template.update(
                commit_hash=True, sequence=False, valid_values=False, playbook_data_types=False
            )

            # zip file
            self.zip_file(self.app_path, app_name_version, tmp_path)

            # cleanup build directory
            shutil.rmtree(tmp_app_path)

        # bundle zips (must have more than 1 app)
        if len(self._app_packages) > 1:
            self.bundle(self.tj.package_bundle_name or app_name)

    def app_name(self, install_json_name):
        """Return the app package name without version.

        1. Use the prefix on the install.json file (bundled Apps).
        2. Use the app_name field from the tcex.json file.
        3. Use the app directory name. This option should not be used.
        """
        if install_json_name != 'install.json':
            return install_json_name.split('.')[0]
        return self.tj.package_app_name or os.path.basename(self.app_path)

    def app_version(self, ij):
        """Return the app version "v1".

        1. Use app_version value from tcex.json if available. Typicall version is major only
           (e.g., v1), but from older Apps it could have minor version.
        2. Use major version from programVersion field in install.json if available.
        3. Default to '1.0.0' updated to major version only ('v1').
        """
        app_version = f"v{ij.program_version.split('.')[0]}"
        return self.tj.package_app_version or app_version

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
