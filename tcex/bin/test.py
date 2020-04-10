#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework Test Generation Module."""
import json
import os

from .bin import Bin
from ..app_config_object import Profile, ProfileInteractive
from ..app_config_object.templates import (
    CustomTemplates,
    DownloadTemplates,
    TestProfileTemplates,
    ValidationTemplates,
)


class Test(Bin):
    """Create testing files for ThreatConnect Exchange App.

    Args:
        _args (namespace): The argparser args Namespace.
    """

    def __init__(self, _args):
        """Initialize Class properties."""
        super().__init__(_args)

        # properties
        self.profile = Profile(
            default_args={}, feature=self.args.feature, name=self.args.profile_name
        )
        self.custom_templates = CustomTemplates(self.profile, self.args.branch)
        self.download_template = DownloadTemplates(self.profile, self.args.branch)
        self.profile_interactive = ProfileInteractive(self.profile)
        self.test_profile_template = TestProfileTemplates(self.profile, self.args.branch)
        self.validation_templates = ValidationTemplates(self.profile, self.args.branch)

    def migrate_profile(self):
        """Migrate legacy profile to new framework."""
        data = []
        profile_file = os.path.join(self.app_path, 'tcex.d', 'profiles', self.args.profile_file)
        if os.path.isfile(self.args.profile_file):
            with open(self.args.profile_file, 'r') as fh:
                data = json.load(fh)
        elif os.path.isfile(profile_file):
            with open(profile_file, 'r') as fh:
                data = json.load(fh)
        else:
            self.handle_error(f'Error reading in profile file: {self.args.profile_file}', True)

        for d in data:
            profile_data = {
                'exit_codes': d.get('exit_codes'),
                'exit_message': None,
                'inputs': d.get('args', {}).get('app'),
                'stage': {'kvstore': self.load_legacy_profiles(d.get('data_files', []))},
            }

            # add profile
            self.profile.add(profile_data=profile_data, profile_name=d.get('profile_name'))

    def create_dirs(self):
        """Create tcex.d directory and sub directories."""
        for d in [
            self.profile.test_directory,
            self.profile.feature_directory,
            self.profile.directory,
        ]:
            if not os.path.isdir(d):
                os.makedirs(d)

        # create __init__ files
        self.create_dirs_init()

    def create_dirs_init(self):
        """Create the __init__.py file under dir."""
        for d in [self.profile.test_directory, self.profile.feature_directory]:
            if os.path.isdir(d):
                with open(os.path.join(d, '__init__.py'), 'a'):
                    os.utime(os.path.join(d, '__init__.py'), None)

    def interactive_profile(self):
        """Present interactive profile inputs."""
        self.profile_interactive.present()
        profile_data = {
            'exit_codes': self.profile_interactive.exit_codes,
            'inputs': self.profile_interactive.inputs,
            'stage': self.profile_interactive.staging_data,
        }
        self.profile.add(profile_data=profile_data)

        # write user defaults file
        if self.profile_interactive.user_defaults:
            with open(self.profile_interactive.user_defaults_filename, 'w') as fh:
                json.dump(self.profile_interactive.user_defaults, fh)

    @staticmethod
    def load_legacy_profiles(staging_files):
        """Load staging data to migrate legacy templates."""
        staging_data = {}
        for sf in staging_files:
            with open(sf, 'r') as fh:
                data = json.load(fh)
            for d in data:
                staging_data[d.get('variable')] = d.get('data')
        return staging_data
