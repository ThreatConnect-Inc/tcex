# -*- coding: utf-8 -*-
"""TcEx Playbook Test Case module"""
import sys
from .test_case_playbook_common import TestCasePlaybookCommon


class TestCasePlaybook(TestCasePlaybookCommon):
    """Playbook TestCase Class"""

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
        # backup sys.argv
        sys_argv_orig = sys.argv

        # clear sys.argv
        sys.argv = sys.argv[:1]

        # run the App
        exit_code = self.run(self.profile.args)

        # add context for populating output variables
        self.profile.add_context(self.context)

        # restore sys.argv
        sys.argv = sys_argv_orig

        return exit_code

    def setup_method(self):
        """Run before each test method runs."""
        super().setup_method()
        self.stager.redis.from_dict(self.redis_staging_data)

        self.redis_client = self.tcex.redis_client
