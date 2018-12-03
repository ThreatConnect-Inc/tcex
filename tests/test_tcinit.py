#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import shutil
import subprocess

import pytest

PATH_TO_TCINIT = os.path.abspath(os.path.join(os.path.dirname(__file__), "./../bin/tcinit"))
TESTING_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "./test-app"))
FILES_TO_BE_UPDATED = ['__main__.py', '.gitignore', 'setup.cfg', 'tcex_json_schema.json']


def _run_subprocess(command_list, reset_testing_dir=True):
    """Run the given commands in subprocess."""
    if reset_testing_dir:
        # delete the directory if it exists
        if os.path.exists(TESTING_DIR):
            shutil.rmtree(TESTING_DIR)
        # create a new directory
        os.makedirs(TESTING_DIR)
    command = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=TESTING_DIR)
    results = command.communicate()
    return {
        'stdout': results[0],
        'stderr': results[1]
    }


def _validate_tcinit_files(app_type, action='create'):
    """Make sure that the expected files were created by the tcinit command."""
    for path, dirs, files in os.walk(TESTING_DIR):
        if app_type == 'job':
            assert set(files) == {'requirements.txt', 'run.py', 'README.md', 'tcex.json', '.gitignore', 'setup.cfg', 'tcex_json_schema.json', '__main__.py', 'install.json', 'app.py', 'args.py', 'job_app.py'}
        else:
            assert set(files) == {'requirements.txt', 'README.md', 'tcex.json', 'app.py', '.gitignore', 'setup.cfg', 'tcex_json_schema.json', '__main__.py', 'install.json', 'args.py', 'playbook_app.py', 'run.py'}
        assert len(files) == 12

        # if we just updated the app, make sure the contents of all of the updated files are correct
        if action == 'update':
            for file_ in files:
                if file_ in FILES_TO_BE_UPDATED:
                    with open(os.path.join(path, file_)) as f:
                        assert f.read() != 'foobar'


def _change_files_before_updating():
    """Change the files which are supposed to be updated to make sure they are properly updated."""
    for file_ in FILES_TO_BE_UPDATED:
        with open(os.path.join(TESTING_DIR, file_), 'w') as f:
            f.write('foobar')


def test_tcinit_without_args():
    """Run the tcinit command without any arguments."""
    output = _run_subprocess([PATH_TO_TCINIT])
    print(output)
    assert output['stdout'] == ''
    assert 'usage: tcinit [-h] [--branch {master,develop}]\n              [--action {create,update,migrate}] --type {job,playbook}\n              [--force]\ntcinit: error: argument --type is required' in output['stderr']


def test_tcinit_without_proper_action():
    """Run the tcinit command with an incorrect argument to make sure it fails correctly."""
    output = _run_subprocess([PATH_TO_TCINIT, '--type', 'job', '--action', 'foobar'])
    print(output)
    assert "argument --action: invalid choice: 'foobar'" in output['stderr']


def test_tcinit_update_on_empty_dir():
    """Run the tcinit command trying to update an app in an empty dir."""
    output = _run_subprocess([PATH_TO_TCINIT, '--type', 'job', '--action', 'update'])
    print(output)
    assert 'RuntimeWarning: No app exists in this directory. Try using "tcinit --type job --action create --branch master" to create an app.' in output['stdout']


def test_tcinit_migrate_on_empty_dir():
    """Run the tcinit command trying to migrate an app in an empty dir."""
    output = _run_subprocess([PATH_TO_TCINIT, '--type', 'job', '--action', 'migrate'])
    print(output)
    assert 'RuntimeWarning: No app exists in this directory. Try using "tcinit --type job --action create --branch master" to create an app.' in output['stdout']


def _check_command_succeeded(subprocess_output):
    """Make sure the subprocess command succeeded."""
    assert 'Using files from "master" branch' in subprocess_output['stdout']
    assert 'Traceback' not in subprocess_output['stdout']
    assert subprocess_output['stderr'] == ''


def test_create_job_app():
    """Run the tcinit command to create a job app."""
    # create the app
    output = _run_subprocess([PATH_TO_TCINIT, '--type', 'job', '--action', 'create'])

    # make sure the app was created properly
    _check_command_succeeded(output)
    _validate_tcinit_files('job')

    # make sure the name in the tcex.json is formatted correctly
    with open(os.path.join(TESTING_DIR, 'tcex.json'), 'r') as f:
        tcex_json = json.load(f)
        assert tcex_json['package']['app_name'] == 'TC_-_My_Job_App'


def test_update_job_app():
    """Run the tcinit command to create a job app."""
    # modify the file to make sure the things are being updated properly
    _change_files_before_updating()

    # update the app
    output = _run_subprocess([PATH_TO_TCINIT, '--type', 'job', '--action', 'update'], reset_testing_dir=False)

    # make sure the app was updated properly
    _check_command_succeeded(output)
    _validate_tcinit_files('job', action='update')


def test_migrate_job_app():
    """Run the tcinit command in a non-empty dir."""
    output = _run_subprocess([PATH_TO_TCINIT, '--type', 'job', '--action', 'migrate'], reset_testing_dir=False)
    print(output)
    assert 'Would you like to overwrite the contents of __main__.py (y/n)?' in output['stdout']


def test_create_app_in_nonempty_dir():
    """Run the tcinit command in a non-empty dir."""
    output = _run_subprocess([PATH_TO_TCINIT, '--type', 'job', '--action', 'create'], reset_testing_dir=False)
    print(output)
    assert 'Would you like to overwrite the contents of __main__.py (y/n)?' in output['stdout']


def test_create_app_in_nonempty_dir_with_force():
    """Run the tcinit command in a non-empty dir with the --force command."""
    output = _run_subprocess([PATH_TO_TCINIT, '--type', 'job', '--action', 'create', '--force'], reset_testing_dir=False)
    print(output)
    _check_command_succeeded(output)
    _validate_tcinit_files('job')


def test_create_playbook_app():
    """Run the tcinit command to create a playbook app."""
    # create the app
    output = _run_subprocess([PATH_TO_TCINIT, '--type', 'playbook', '--action', 'create'])

    # make sure the app was created properly
    _check_command_succeeded(output)
    _validate_tcinit_files('playbook')


def test_update_playbook_app():
    """Run the tcinit command to update a playbook app."""
    # modify the file to make sure the things are being updated properly
    _change_files_before_updating()

    # update the app
    output = _run_subprocess([PATH_TO_TCINIT, '--type', 'playbook', '--action', 'update'], reset_testing_dir=False)

    # make sure the app was updated properly
    _check_command_succeeded(output)
    _validate_tcinit_files('playbook', action='update')


def test_migrate_playbook_app():
    """Run the tcinit command in a non-empty dir."""
    output = _run_subprocess([PATH_TO_TCINIT, '--type', 'playbook', '--action', 'migrate'], reset_testing_dir=False)
    print(output)
    assert 'Would you like to overwrite the contents of __main__.py (y/n)?' in output['stdout']


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """Cleanup the testing directory once we are finished."""
    def remove_test_dir():
        shutil.rmtree(TESTING_DIR)
    request.addfinalizer(remove_test_dir)
