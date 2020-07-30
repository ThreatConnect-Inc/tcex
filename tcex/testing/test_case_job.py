# -*- coding: utf-8 -*-
"""TcEx Runtime App Test Case"""
# standard library
import os
import subprocess
import sys

from .test_case import TestCase


class TestCaseJob(TestCase):
    """App TestCase Class"""

    run_method = 'inline'  # run service inline or a as subprocess

    @staticmethod
    def create_shelf_dir(shelf_path):
        """Create a directory in log with the context name containing the batch data."""
        if not os.path.isdir(shelf_path):
            os.makedirs(shelf_path)
            with open(os.path.join(shelf_path, 'DEBUG'), 'a'):
                os.utime(os.path.join(shelf_path, 'DEBUG'), None)

    def run(self):
        """Run the Playbook App.

        Returns:
            int: The exit code fo the App.
        """
        # first-party
        from run import run  # pylint: disable=no-name-in-module

        # run the app
        exit_code = 0
        try:
            run()
        except SystemExit as e:
            exit_code = e.code

        self.log.data('run', 'Exit Code', exit_code)
        return exit_code

    def run_profile(self):
        """Run an App using the profile name."""
        self.create_shelf_dir(self.profile.tc_temp_path)

        # create encrypted config file
        self.create_config(self.profile.args)

        # run the service App in 1 of 3 ways
        if self.run_method == 'inline':
            # backup sys.argv
            sys_argv_orig = sys.argv

            # clear sys.argv
            sys.argv = sys.argv[:1]

            # run the App
            exit_code = self.run()

            # restore sys.argv
            sys.argv = sys_argv_orig
        elif self.run_method == 'subprocess':
            # run the Service App as a subprocess
            app_process = subprocess.Popen(['python', 'run.py'])
            exit_code = app_process.wait()

        # run the App
        return exit_code
