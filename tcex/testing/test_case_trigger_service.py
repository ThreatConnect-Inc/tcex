# -*- coding: utf-8 -*-
"""TcEx Service Common Module"""
# standard library
import sys

from .test_case_service_common import TestCaseServiceCommon


class TestCaseTriggerService(TestCaseServiceCommon):
    """Service App TestCase Class"""

    # TOOD: move to service command
    def run(self):
        """Run the Playbook App.

        Returns:
            int: The App exit code
        """
        # first-party
        from run import run  # pylint: disable=no-name-in-module

        # backup sys.argv
        sys_argv_orig = sys.argv

        # clear sys.argv
        sys.argv = sys.argv[:1]

        # run the app
        exit_code = 0
        try:
            # provide callback to to run.py method on Trigger Service Apps
            run(set_app=self._app_callback)  # pylint: disable=unexpected-keyword-arg
        except SystemExit as e:
            exit_code = e.code

        # restore sys.argv
        sys.argv = sys_argv_orig

        self.log.data('run', 'Exit Code', exit_code)
        return exit_code
