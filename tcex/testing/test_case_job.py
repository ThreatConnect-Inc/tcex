# -*- coding: utf-8 -*-
"""TcEx Runtime App Test Case"""
import os
from six import string_types
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
            if isinstance(v, string_types):
                args[k] = self.resolve_env_args(v)

        self.log_data('run', 'args', args)
        app = self.app(args)

        # Start
        exit_code = self.run_app_method(app, 'start')
        if exit_code != 0:
            return exit_code

        # Run
        exit_code = self.run_app_method(app, 'run')
        if exit_code != 0:
            return exit_code

        # Write Output
        exit_code = self.run_app_method(app, 'write_output')
        if exit_code != 0:
            return exit_code

        # Done
        exit_code = self.run_app_method(app, 'done')
        if exit_code != 0:
            return exit_code

        return self._exit(app.tcex.exit_code)

    def run_profile(self, profile_name):
        """Run an App using the profile name."""
        profile = self.profile(profile_name)
        if not profile:
            self.log.error('No profile named {} found.'.format(profile_name))
            return self._exit(1)

        args = {'tc_temp_path': os.path.join(self._app_path, 'log', self.context)}
        self.create_shelf_dir(args['tc_temp_path'])

        # build args from install.json
        args.update(profile.get('inputs', {}).get('required', {}))
        args.update(profile.get('inputs', {}).get('optional', {}))
        if not args:
            self.log.error('No profile named {} found.'.format(profile_name))
            return self._exit(1)

        # run the App
        exit_code = self.run(args)

        return self._exit(exit_code)
