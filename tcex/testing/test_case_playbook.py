# -*- coding: utf-8 -*-
"""TcEx Playbook Test Case module"""
# standard library
import os
import subprocess
import sys

from .test_case_playbook_common import TestCasePlaybookCommon


class TestCasePlaybook(TestCasePlaybookCommon):
    """Playbook TestCase Class"""

    run_method = 'inline'  # run service inline or a as subprocess

    def run(self):
        """Run the Playbook App.

        Args:
            args (dict): The App CLI args.

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

        try:
            # remove env var for encrypted file if there
            del os.environ['TC_APP_PARAM_KEY']
            del os.environ['TC_APP_PARAM_FILE']
        except KeyError:
            pass

        # add context for populating output variables
        self.profile.add_context(self.context)

        return exit_code

    def setup_method(self):
        """Run before each test method runs."""
        super().setup_method()
        self.stager.redis.from_dict(self.redis_staging_data)

        self.redis_client = self.tcex.redis_client
