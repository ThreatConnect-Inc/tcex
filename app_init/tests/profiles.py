# -*- coding: utf-8 -*-
"""Gather profiles for test case."""
import os


def profiles(profiles_dir):
    """Get all testing profile names for current feature."""
    profile_names = []
    for filename in sorted(os.listdir(profiles_dir)):
        if filename.endswith('.json'):
            profile_names.append(filename.replace('.json', ''))
    return profile_names
