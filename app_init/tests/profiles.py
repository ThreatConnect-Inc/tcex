# -*- coding: utf-8 -*-
"""Gather profiles for test case."""
import json
import os


def profiles(profiles_dir):
    """Get all testing profile names for current feature."""
    envs = set(os.environ.get('TCEX_TEST_ENVS', 'build').split(','))
    profile_names = []
    skip_profiles = []  # profiles marked to be skipped
    for filename in sorted(os.listdir(profiles_dir)):
        profile_name = filename.replace('.json', '')
        profile_names.append(profile_name)

        # find profiles that should be skipped due to environment settings
        if filename.endswith('.json'):
            with open(os.path.join(profiles_dir, filename), 'r') as fh:
                pd = json.load(fh)
            if not envs.intersection(set(pd.get('environments', ['build']))):
                skip_profiles.append(profile_name)
    return profile_names, skip_profiles
