# -*- coding: utf-8 -*-
"""TcEx Runtime App Test Case"""
import os

from .test_case import TestCase


class TestCaseJob(TestCase):
    """App TestCase Class"""

    _output_variables = None
    redis_client = None

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
            [type]: [description]
        """
        # resolve env vars
        for k, v in list(args.items()):
            if isinstance(v, str):
                args[k] = self.resolve_env_args(v)

        self.log_data('run', 'args', args)
        self.app = self.app_init(args)

        # Start
        exit_code = self.run_app_method(self.app, 'start')
        if exit_code != 0:
            return exit_code

        # Run
        exit_code = self.run_app_method(self.app, 'run')
        if exit_code != 0:
            return exit_code

        # Done
        exit_code = self.run_app_method(self.app, 'done')
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
        if isinstance(profile, str):
            profile = self.init_profile(profile)

        args = {'tc_temp_path': os.path.join(self._app_path, 'log', self.context)}
        self.create_shelf_dir(args['tc_temp_path'])

        # build args from install.json
        args.update(profile.get('inputs', {}).get('required', {}))
        args.update(profile.get('inputs', {}).get('optional', {}))

        # run the App
        exit_code = self.run(args)

        return exit_code
