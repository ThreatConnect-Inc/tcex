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

    def run(self, args):  # pylint: disable=too-many-return-statements
        """Run the Playbook App.

        Args:
            args (dict): The App CLI args.

        Returns:
            int: The exit code fo the App.
        """
        self.log.data('run', 'args', args)
        self.app = self.app_init(args)

        # Setup
        exit_code = self.run_app_method(self.app, 'setup')
        if exit_code != 0:
            return exit_code

        # Run
        exit_code = self.run_app_method(self.app, 'run')
        if exit_code != 0:
            return exit_code

        # Teardown
        exit_code = self.run_app_method(self.app, 'teardown')
        if exit_code != 0:
            return exit_code

        try:
            # call exit for message_tc output, but don't exit
            self.app.tcex.playbook.exit(msg=self.app.exit_message)
        except SystemExit:
            pass

        return self._exit(self.app.tcex.exit_code)

    def run_profile(self, profile):
        """Run an App using the profile name."""
        self.create_shelf_dir(profile.tc_temp_path)

        # run the App
        return self.run(profile.args)
