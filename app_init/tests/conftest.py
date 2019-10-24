# -*- coding: utf-8 -*-
"""Base pytest configuration file."""
import os
import shutil
import sys


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
    lib_major_version = 'lib_{}'.format(sys.version_info.major)
    lib_minor_version = '{}.{}'.format(lib_major_version, sys.version_info.minor)
    lib_micro_version = '{}.{}'.format(lib_minor_version, sys.version_info.micro)

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
    """Execute uncofigure logic before test process is exited."""
    directory = os.path.join(os.getcwd(), 'log')
    for root, dirs, files in os.walk(directory):  # pylint: disable=unused-variable
        for f in files:
            f = os.path.join(root, f)
            try:
                if os.path.getsize(f) == 0:
                    os.remove(f)
            except OSError:
                continue


clear_log_directory()
update_system_path()
