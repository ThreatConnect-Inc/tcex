# -*- coding: utf-8 -*-
"""TcEx Runtime App Test Case"""
import os
from .test_case import TestCase


class TestCaseJob(TestCase):
    """App TestCase Class"""

    @staticmethod
    def create_shelf_dir(shelf_path):
        """Create a directory in log with the context name containing the batch data."""
        if not os.path.isdir(shelf_path):
            os.makedirs(shelf_path)
            with open(os.path.join(shelf_path, 'DEBUG'), 'a'):
                os.utime(os.path.join(shelf_path, 'DEBUG'), None)

    def run(self, args):
        """Run the Playbook App.

        Args:
            args (dict): The App CLI args.

        Returns:
            int: The exit code fo the App.
        """
        from run import run

        # update args to app_args
        config = self._update_args(args)

        # run the app
        exit_code = 0
        try:
            run(config)
        except SystemExit as e:
            exit_code = e.code

        self.log.data('run', 'Exit Code', exit_code)
        return exit_code

    def run_profile(self):
        """Run an App using the profile name."""
        self.create_shelf_dir(self.profile.tc_temp_path)

        # run the App
        return self.run(self.profile.args)
