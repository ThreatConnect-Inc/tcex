# -*- coding: utf-8 -*-
"""Gather profiles for test case."""
import json
import os


def profiles(profiles_dir):
    """Get all testing profile names for current feature."""
    envs = set(os.environ.get('TCEX_TEST_ENVS', 'build').split(','))
    profile_names = []
    for filename in sorted(os.listdir(profiles_dir)):
        if filename.endswith('.json'):
            with open(os.path.join(profiles_dir, filename), 'r') as fh:
                pd = json.load(fh)
            if envs.intersection(set(pd.get('environments', ['build']))):
                profile_names.append(filename.replace('.json', ''))
    return profile_names
