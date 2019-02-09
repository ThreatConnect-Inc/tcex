#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx App Init."""

import json
import os
import sys

import requests
import colorama as c

# Python 2 unicode
if sys.version_info[0] == 2:
    get_input = raw_input  # noqa: F821; pylint: disable=E0602
else:
    get_input = input


class TcExInit(object):
    """Install Required Modules for App."""

    def __init__(self, _arg):
        """Init TcLib Module."""
        self.args = _arg
        self.app_path = os.getcwd()
        self.base_url = (
            'https://raw.githubusercontent.com/ThreatConnect-Inc/tcex/{}/app_init/'
        ).format(self.args.branch)
        self.exit_code = 0
        self.confirm_overwrite = True

        # initialize colorama
        c.init(autoreset=True, strip=False)

        if self.args.action == 'update' or self.args.action == 'migrate':
            # check if the current directory is empty (if so, a RuntimeWarning is raised)
            self._check_empty_app_dir()
            # if self.args.action == 'update':
            #     self.confirm_overwrite = False

        if self.args.force:
            self.confirm_overwrite = False

    def _check_empty_app_dir(self):
        """Check to see if the directory in which the app is going to be created is empty."""
        # if we are updating/migrating an app and the directory is empty - raise a warning
        if not any(os.listdir(self.app_path)):
            message = (
                'No app exists in this directory. Try using "tcinit --template '
                '{} --action create --branch {}" to create an app.'
            ).format(self.args.template, self.args.branch)
            raise RuntimeWarning(message)

    @staticmethod
    def _print_results(file, status):
        """Print the download results."""
        file_color = c.Fore.GREEN
        status_color = c.Fore.RED
        if status == 'Success':
            status_color = c.Fore.GREEN
        elif status == 'Skipped':
            status_color = c.Fore.YELLOW
        print(
            '{}{!s:<20}{}{!s:<35}{}{!s:<15}{}{!s:<15}'.format(
                c.Fore.CYAN,
                'Downloading:',
                file_color,
                file,
                c.Fore.CYAN,
                'Status:',
                status_color,
                status,
            )
        )

    @staticmethod
    def _file_exists(file_path):
        """Check if a file at the given path exists."""
        return os.access(file_path, os.F_OK)

    @staticmethod
    def _confirm_overwrite(file_path):
        """Confirm overwrite of template files.

        Make sure the user would like to continue downloading a file which will overwrite a file
        in the current directory.
        """
        message = '{}Would you like to overwrite the contents of {} (y/[n])? '.format(
            c.Fore.MAGENTA, file_path
        )
        response = get_input(message) or 'n'
        response = response.lower()

        if response in ['y', 'yes']:
            return True
        return False

    def download_file(self, remote_filename, local_filename=None):
        """Download file from github."""
        status = 'Failed'
        if local_filename is None:
            local_filename = remote_filename

        if self.confirm_overwrite and self._file_exists(local_filename):
            if not self._confirm_overwrite(local_filename):
                self._print_results(local_filename, 'Skipped')
                # print('{}{!s:<20}{}'.format(c.Fore.YELLOW, 'Skipping:', local_filename))
                return

        # github url
        url = '{}{}'.format(self.base_url, remote_filename)
        r = requests.get(url, allow_redirects=True)
        if r.ok:
            open(local_filename, 'wb').write(r.content)
            status = 'Success'
        else:
            print('{}{}Error requesting: {}'.format(c.Style.BRIGHT, c.Fore.RED, url))

        # print download status
        self._print_results(local_filename, status)

    @staticmethod
    def update_install_json():
        """Update the install.json configuration file if exists."""
        if not os.path.isfile('install.json'):
            return

        with open('install.json', 'r') as f:
            install_json = json.load(f)

        if install_json.get('programMain'):
            install_json['programMain'] = 'run'

        # update features
        install_json['features'] = ['aotExecutionEnabled', 'appBuilderCompliant', 'secureParams']

        with open('install.json', 'w') as f:
            json.dump(install_json, f, indent=2, sort_keys=True)

    @staticmethod
    def update_tcex_json():
        """Update the tcex.json configuration file if exists."""
        if not os.path.isfile('tcex.json'):
            return

        with open('tcex.json', 'r') as f:
            tcex_json = json.load(f)

        # display warning on missing app_name field
        if tcex_json.get('package', {}).get('app_name') is None:
            print('{}The tcex.json file is missing the "app_name" field.'.format(c.Fore.MAGENTA))

        # display warning on missing app_version field
        if tcex_json.get('package', {}).get('app_version') is None:
            print('{}The tcex.json file is missing the "app_version" field.'.format(c.Fore.YELLOW))

        # update excludes
        excludes = [
            '.gitignore',
            '.pre-commit-config.yaml',
            'pyproject.toml',
            'setup.cfg',
            'tcex.json',
            '*.install.json',
            'tcex.d',
        ]

        missing_exclude = False
        for exclude in excludes:
            if exclude not in tcex_json.get('package').get('excludes', []):
                missing_exclude = True
                break

        if missing_exclude:
            message = '{}The tcex.json file is missing excludes items. Update ([y]/n)? '.format(
                c.Fore.YELLOW
            )
            response = (get_input(message) or 'y').lower()

            if response in ['y', 'yes']:
                # get unique list of excludes
                excludes.extend(tcex_json.get('package', {}).get('excludes'))
                tcex_json['package']['excludes'] = sorted(list(set(excludes)))

                with open('tcex.json', 'w') as f:
                    json.dump(tcex_json, f, indent=2, sort_keys=True)
