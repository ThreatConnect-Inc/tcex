# -*- coding: utf-8 -*-
"""TcEx Framework TcexJson Object."""
# standard library
import json
import logging
import os
import re
from collections import OrderedDict

# third-party
import colorama as c

from ..env_store import EnvStore
from .install_json import InstallJson


class TcexJson:
    """Object for tcex.json file.

    Args:
        filename (str, optional): The config filename. Defaults to tcex.json.
        path (str, optional): The path to the file. Defaults to os.getcwd().
        logger (logging.Logger, optional): A instance of Logger. Defaults to None.
    """

    def __init__(self, filename=None, path=None, logger=None):
        """Initialize class properties."""
        self._filename = filename or 'tcex.json'
        self._path = path or os.getcwd()
        self.log = logger or logging.getLogger('layout_json')

        # properties
        self._contents = None
        self.env_store = EnvStore()
        self.ij = InstallJson()

    @property
    def contents(self):
        """Return install.json contents."""
        if self._contents is None:
            try:
                with open(self.filename, 'r') as fh:
                    contents = json.load(fh, object_pairs_hook=OrderedDict)

                    # replace all variables
                    contents = self.replace_env_variables(contents)

                    # set updated contents
                    self._contents = contents
            except OSError:
                self._contents = {}

            # raise error if tcex.json is missing app_name field
            if self._contents and not self._contents.get('package', {}).get('app_name'):
                raise RuntimeError('The tcex.json file is missing the package.app_name field.')

            # log warning for old Apps
            if self._contents.get('package', {}).get('app_version'):
                print(
                    f'{c.Fore.YELLOW}'
                    'WARNING: The tcex.json file defines "app_version" which should only be '
                    'defined in legacy Apps. Removing the value can cause the App to be treated '
                    'as a new App by TcExchange. Please remove "app_version" when appropriate.'
                    f'{c.Fore.RESET}'
                )

        return self._contents

    @property
    def filename(self):
        """Return the fqpn for the layout.json file."""
        return os.path.join(self._path, self._filename)

    def replace_env_variables(self, json_data):
        """Update any env variable.

        Args:
            json_data (dict): The profile data dict.

        Returns:
            dict: The updated dict.
        """
        profile = json.dumps(json_data)

        for m in re.finditer(r'\${(env|envs|local|remote):(.*?)}', profile):
            try:
                full_match = m.group(0)
                env_type = m.group(1)
                env_key = m.group(2)

                env_value = self.env_store.getenv(env_key, env_type)
                if env_value is not None:
                    profile = profile.replace(full_match, env_value)
            except IndexError:
                print(f'{c.Fore.YELLOW}Invalid variable found {full_match}.')
        return json.loads(profile)

    def update(self, template=None):
        """Update the contents of the tcex.json file."""
        if not os.path.isfile(self.filename):
            return

        with open(self.filename, 'r+') as fh:
            json_data = json.load(fh)

            # update app_name
            self.update_package_app_name(json_data)

            # update deprecated fields
            self.update_deprecated_fields(json_data)

            # update package excludes
            self.update_package_excludes(json_data)

            # update package excludes
            self.update_lib_versions(json_data)

            # update variable pattern
            json_data = self.update_variable_pattern_env(json_data)

            # update template
            if template is not None:
                json_data['template'] = template

            # write updated profile
            fh.seek(0)
            fh.write(f'{json.dumps(json_data, indent=2, sort_keys=True)}\n')
            fh.truncate()

        # update contents
        self._contents = self.replace_env_variables(json_data)

    def update_package_app_name(self, json_data):
        """Update the package app_name in the tcex.json file."""
        if self.package_app_name in [None, '', 'TC_-_', 'TCPB_-_', 'TCVC_-_', 'TCVW_-_']:
            # lower case name and replace prefix if already exists
            app_name = os.path.basename(os.getcwd()).lower().replace(self.ij.app_prefix.lower(), '')

            # replace spaces and dashes with underscores
            app_name = app_name.replace(' ', '_').replace('-', '_').lower()

            # title case app name
            app_name = '_'.join([a.title() for a in app_name.split('_')])

            # prepend appropriate App prefix (e.g., TCPB_-_)
            app_name = f'{self.ij.app_prefix}{app_name}'

            # update App name
            json_data['package']['app_name'] = app_name

    @staticmethod
    def update_deprecated_fields(json_data):
        """Update deprecated fields in the tcex.json file."""
        deprecated_fields = ['profile_include_dirs']
        for d in deprecated_fields:
            try:
                del json_data[d]
            except KeyError:
                pass

    def update_package_excludes(self, json_data):
        """Update the excludes values in the tcex.json file."""
        excludes = self.package_excludes
        excludes.extend(
            [
                '.gitignore',
                '.pre-commit-config.yaml',
                'local-*',
                'pyproject.toml',
                'setup.cfg',
                'tcex.json',
                '*.install.json',
                'tcex.d',
            ]
        )
        excludes = sorted(list(set(excludes)))
        # the requirements.txt file is required for App Builder
        try:
            excludes.remove('requirements.txt')
        except ValueError:
            pass
        json_data['package']['excludes'] = excludes

    def update_lib_versions(self, json_data):
        """Update the lib_versions array in the tcex.json file."""
        if os.getenv('TCEX_LIB_VERSIONS') and not self.lib_versions:
            lib_versions = []
            for version in os.getenv('TCEX_LIB_VERSIONS').split(','):
                lib_versions.append(
                    {
                        'lib_dir': f'lib_${{env:{version}}}',
                        'python_executable': f'~/.pyenv/versions/${{env:{version}}}/bin/python',
                    }
                )
            json_data['lib_versions'] = lib_versions

    @staticmethod
    def update_variable_pattern_env(json_data):
        """Update the profile variable to latest pattern

        Args:
            json_data (dict): The profile data dict.

        Returns:
            dict: The updated dict.
        """
        data = json.dumps(json_data)

        for m in re.finditer(r'\$(env|envs|local|remote)\.([^(\/|\")]*)', data):
            try:
                full_match = m.group(0)
                env_type = m.group(1)
                env_key = m.group(2)

                new_variable = f'${{{env_type}:{env_key}}}'
                data = data.replace(full_match, new_variable)
            except IndexError:
                print(f'{c.Fore.YELLOW}Invalid variable found {full_match}.')
        return json.loads(data)

    #
    # properties
    #

    @property
    def lib_versions(self):
        """Return property."""
        return self.contents.get('lib_versions', [])

    @property
    def package(self):
        """Return property."""
        return self.contents.get('package', {})

    @property
    def package_app_name(self):
        """Return property."""
        return self.package.get('app_name')

    @property
    def package_app_version(self):
        """Return property."""
        return self.package.get('app_version')

    @property
    def package_bundle(self):
        """Return property."""
        return self.package.get('bundle', False)

    @property
    def package_bundle_name(self):
        """Return property."""
        return self.package.get('bundle_name')

    @property
    def package_bundle_packages(self):
        """Return property."""
        return self.package.get('bundle_packages', [])

    @property
    def package_excludes(self):
        """Return property."""
        return self.package.get('excludes', [])

    @property
    def template(self):
        """Return property."""
        return self.contents.get('template')
