# -*- coding: utf-8 -*-
"""TcEx Service Common Module"""
import sys
from .test_case_service_common import TestCaseServiceCommon


class TestCaseTriggerService(TestCaseServiceCommon):
    """Service App TestCase Class"""

    # TOOD: move to service command
    def run(self, args):
        """Run the Playbook App.

        Args:
            args (dict): The App CLI args.

        Returns:
            int: The App exit code
        """
        from run import run

        # backup sys.argv
        sys_argv_orig = sys.argv

        # clear sys.argv
        sys.argv = sys.argv[:1]

        # run the app
        exit_code = 0
        try:
            run()
        except SystemExit as e:
            exit_code = e.code

        # restore sys.argv
        sys.argv = sys_argv_orig

        self.log.data('run', 'Exit Code', exit_code)
        return exit_code
