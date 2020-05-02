# -*- coding: utf-8 -*-
"""Base pytest configuration file."""
import os
import shutil
import pytest


def pytest_addoption(parser):
    """Add arg flag to control replacement of outputs."""
    parser.addoption('--merge_inputs', action='store_true')
    parser.addoption('--merge_outputs', action='store_true')
    parser.addoption('--replace_exit_message', action='store_true')
    parser.addoption('--replace_outputs', action='store_true')
    parser.addoption('--update', action='store_true')


@pytest.fixture()
def merge_inputs(pytestconfig):
    """Return the current value for merge_inputs args."""
    return pytestconfig.getoption('merge_inputs')


@pytest.fixture()
def merge_outputs(pytestconfig):
    """Return the current value for merge_outputs args."""
    return pytestconfig.getoption('merge_outputs')


@pytest.fixture()
def replace_exit_message(pytestconfig):
    """Return the current value for replace_outputs args."""
    return pytestconfig.getoption('replace_exit_message')


@pytest.fixture()
def replace_outputs(pytestconfig):
    """Return the current value for replace_outputs args."""
    return pytestconfig.getoption('replace_outputs')


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
