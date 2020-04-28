# -*- coding: utf-8 -*-
"""Base pytest configuration file."""
import os
import shutil
import sys
import pytest

# NOTE: tcex profile is imported at EOF after sys.path modifications


def profiles(profiles_dir):
    """Get all testing profile names for current feature."""
    profile_names = []
    for filename in sorted(os.listdir(profiles_dir)):
        if filename.endswith('.json'):
            profile_names.append(filename.replace('.json', ''))
    return profile_names


def pytest_addoption(parser):
    """Add arg flag to control replacement of outputs."""
    profile_addoption(parser)


def pytest_generate_tests(metafunc):
    """ Generate the tests for this metafunc --
        Specifically looks at the fixures the function wants;
        if the function does *not* want profile_data, we ignore markup
        on this test function.
    """

    config = metafunc.config
    # we don't add automatic parameterization to anything that doesn't request profile_name
    if 'profile_name' not in metafunc.fixturenames:
        return
    profile_dir = os.path.join(
        os.path.dirname(os.path.abspath(metafunc.module.__file__)), 'profiles.d'
    )
    profile_names = profiles(profile_dir)

    permutations = []
    ids = []
    for profile_name in profile_names:
        # At this point, we append one permutation record for *each* variation of the profile

        feature = profile_dir.split(os.sep)[-2]

        profile = Profile(name=profile_name, feature=feature, pytestconfig=config)
        # test_permutations will give us back a list of (id, base_name, options)
        test_permutations = profile.test_permutations()
        permutations.extend([x[1:] for x in test_permutations])

        ids.extend([x[0] for x in test_permutations])

    metafunc.parametrize('profile_name,test_options', permutations, ids=ids)


@pytest.fixture()
def options(test_options, request):
    """ Mark up the options, if it exists, with the request object, so
        that the profile can access test case methods
    """

    if test_options and isinstance(test_options, dict):
        test_options['request'] = request

    return test_options


@pytest.fixture()
def merge_outputs(pytestconfig):
    """Return the current value for merge_outputs args."""
    return pytestconfig.getoption('--merge_outputs')


@pytest.fixture()
def replace_exit_message(pytestconfig):
    """Return the current value for replace_outputs args."""
    return pytestconfig.getoption('--replace_exit_message')


@pytest.fixture()
def replace_outputs(pytestconfig):
    """Return the current value for replace_outputs args."""
    return pytestconfig.getoption('--replace_outputs')


# clear log directory
def clear_log_directory():
    """Clear the App log directory."""
    log_directory = 'log'
    if os.path.isdir(log_directory):
        print('Clearing log directory.')
        for log_file in os.listdir(log_directory):
            file_path = os.path.join(log_directory, log_file)
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            if os.path.isfile(file_path):
                os.remove(file_path)


def get_lib_directories():
    """Get all "lib" directories."""
    lib_directories = []
    contents = os.listdir(os.getcwd())
    for c in contents:
        # ensure content starts with lib, is directory, and is readable
        if c.startswith('lib') and os.path.isdir(c) and (os.access(c, os.R_OK)):
            lib_directories.append(c)

    # return sorted lib directories with newest Python version first
    return sorted(lib_directories, reverse=True)


def update_system_path():
    """Update the system path to ensure project modules and dependencies can be found."""
    # set lib directory version based off current Python interpreter
    lib_major_version = f'lib_{sys.version_info.major}'
    lib_minor_version = f'{lib_major_version}.{sys.version_info.minor}'
    lib_micro_version = f'{lib_minor_version}.{sys.version_info.micro}'

    cwd = os.getcwd()  # the current working directory

    # get existing lib directories for current App
    lib_directories = get_lib_directories()

    # set default lib directory to lib_latest in case no other matches can be found (best effort)
    lib_directory = os.path.join(cwd, 'lib_latest')

    # search for most appropriate lib directory for the current version of Python
    if lib_micro_version in lib_directories:
        lib_directory = lib_micro_version  # exact micro version match
    elif lib_minor_version in lib_directories:
        lib_directory = lib_minor_version  # exact minor version match
    elif lib_major_version in lib_directories:
        lib_directory = lib_major_version  # exact major version match
    else:
        # no exact matches found, find closest match
        for lv in [lib_micro_version, lib_minor_version, lib_major_version]:
            for d in lib_directories:  # lib_directores are sorted newest to oldest version
                if lv in d:
                    lib_directory = d
                    break
            else:
                continue
            break

    sys.path.insert(0, lib_directory)

    # insert the current working directory into the system Path for the App, ensuring that it is
    # always the first entry in the list.
    try:
        sys.path.remove(cwd)
    except ValueError:
        pass
    sys.path.insert(0, cwd)


def pytest_unconfigure(config):  # pylint: disable=unused-argument
    """Execute unconfigure logic before test process is exited."""
    log_directory = os.path.join(os.getcwd(), 'log')

    # remove any 0 byte files from log directory
    for root, dirs, files in os.walk(log_directory):  # pylint: disable=unused-variable
        for f in files:
            f = os.path.join(root, f)
            try:
                if os.path.getsize(f) == 0:
                    os.remove(f)
            except OSError:
                continue

    # display any Errors or Warnings in tests.log
    test_log_file = os.path.join(log_directory, 'tests.log')
    if os.path.isfile(test_log_file):
        with open(test_log_file, 'r') as fh:
            issues = []
            for line in fh:
                if '- ERROR - ' in line or '- WARNING - ' in line:
                    issues.append(line.strip())

            if issues:
                print('\nErrors and Warnings:')
                for i in issues:
                    print(f'- {i}')

    # remove service started file
    try:
        os.remove('./SERVICE_STARTED')
    except OSError:
        pass


clear_log_directory()
update_system_path()

# pylint: disable=wrong-import-position
# can't import TCEX profile until the system path is fixed
from tcex.app_config_object.profile import Profile, profile_addoption
