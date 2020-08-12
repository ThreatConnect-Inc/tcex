#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework Test Generation Module."""
# standard library
import copy
import json
import os

from ..app_config_object.templates import (
    CustomTemplates,
    DownloadTemplates,
    TestProfileTemplates,
    ValidationTemplates,
)
from ..profile import Interactive, Profile
from .bin import Bin


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
        self.profile_interactive = Interactive(self.profile)
        self.test_profile_template = TestProfileTemplates(self.profile, self.args.branch)
        self.validation_templates = ValidationTemplates(self.profile, self.args.branch)

    def add_negative_profile(self, profile_name, inputs, fail_on_error=None):
        """Create a negative profile."""
        # build profile name
        exit_code = 1  # default exit code is 1
        if fail_on_error is not None:
            if fail_on_error is False:
                exit_code = 0
            profile_name = f'{profile_name}_foe_{str(fail_on_error).lower()}'

        # get profile data and update with new inputs
        profile_data = self.profile.contents
        profile_data['exit_codes'] = [exit_code]
        profile_data['exit_message'] = None
        profile_data['inputs'] = inputs
        profile_data['outputs'] = None

        # create a meaningful profile name
        new_profile = Profile(default_args={}, feature=self.args.feature, name=profile_name)
        new_profile.add(profile_data=profile_data)

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

    def create_negative_profiles(self):
        """Create negative profiles using interactive profile base."""
        for inputs in self.profile.profile_inputs:
            for name, value in inputs.get('required', {}).items():
                ij_data = self.profile.ij.params_dict.get(name, {})
                # create a profile for each pb data type
                for pb_data_type in ij_data.get('playbookDataType', []):
                    for negative_type in self.negative_inputs.get(pb_data_type.lower(), []):
                        # the value is pre-staged in test_case_playbook_common.py
                        value = f'#App:1234:{negative_type}!{pb_data_type}'
                        profile_name = f'negative_{name}_{pb_data_type.lower()}_{negative_type}'
                        # modify copy so original is preserved for next interation
                        new_inputs = copy.deepcopy(inputs)
                        new_inputs['required'][name] = value

                        if 'fail_on_error' in inputs.get('optional', {}):
                            # handle fail on error
                            for b in [False, True]:
                                new_inputs['optional']['fail_on_error'] = b
                                self.add_negative_profile(profile_name, new_inputs, b)
                        else:
                            self.add_negative_profile(profile_name, new_inputs)

    def interactive_profile(self, negative=False):
        """Present interactive profile inputs."""
        self.profile_interactive.present()
        profile_data = {
            'exit_codes': self.profile_interactive.exit_codes,
            'inputs': self.profile_interactive.inputs,
            'stage': self.profile_interactive.staging_data,
        }
        self.profile.add(profile_data=profile_data)

        if negative:
            # if user specified negative arg then create negative test profiles
            self.create_negative_profiles()

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

    @property
    def negative_inputs(self):
        """Return dict of negative inputs."""
        return {
            'binary': ['empty', 'null'],
            'binaryarray': ['empty', 'null'],
            'keyvalue': ['null'],
            'keyvaluearray': ['null'],
            'string': ['empty', 'null'],
            'stringarray': ['empty', 'null'],
            'tcentity': ['null'],
            'tcentityarray': ['null'],
        }
