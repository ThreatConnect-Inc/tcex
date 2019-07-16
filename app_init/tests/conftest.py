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


def update_system_path():
    """Update the system path to ensure project modules and dependencies can be found."""
    cwd = os.getcwd()
    lib_dir = os.path.join(os.getcwd(), 'lib_')
    lib_latest = os.path.join(os.getcwd(), 'lib_latest')

    # insert the lib_latest directory into the system Path if no other lib directory found. This
    # entry will be bumped to index 1 after adding the current working directory.
    if not [p for p in sys.path if lib_dir in p]:
        sys.path.insert(0, lib_latest)

    # insert the current working directory into the system Path for the App, ensuring that it is
    # always the first entry in the list.
    try:
        sys.path.remove(cwd)
    except ValueError:
        pass
    sys.path.insert(0, cwd)


clear_log_directory()
update_system_path()
