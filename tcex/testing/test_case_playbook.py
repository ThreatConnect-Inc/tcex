# -*- coding: utf-8 -*-
"""TcEx Playbook Test Case module"""
import traceback
from six import string_types
from .test_case_playbook_common import TestCasePlaybookCommon


class TestCasePlaybook(TestCasePlaybookCommon):
    """Playbook TestCase Class"""

    def run(self, args):  # pylint: disable=too-many-return-statements
        """Run the Playbook App.

        Args:
            args (dict): The App CLI args.

        Returns:
            [type]: [description]
        """
        # resolve env vars
        for k, v in args.items():
            if isinstance(v, string_types):
                args[k] = self.resolve_env_args(v)

        args['tc_playbook_out_variables'] = ','.join(self.output_variables)
        self.log_data('run', 'args', args)
        app = self.app(args)

        # Start
        exit_code = self.run_app_method(app, 'start')
        if exit_code != 0:
            return exit_code

        # Run
        try:
            if hasattr(app.args, 'tc_action') and app.args.tc_action is not None:
                tc_action = app.args.tc_action
                tc_action_formatted = tc_action.lower().replace(' ', '_')
                tc_action_map = 'tc_action_map'
                if hasattr(app, tc_action):
                    getattr(app, tc_action)()
                elif hasattr(app, tc_action_formatted):
                    getattr(app, tc_action_formatted)()
                elif hasattr(app, tc_action_map):
                    app.tc_action_map.get(app.args.tc_action)()  # pylint: disable=no-member
            else:
                app.run()
        except SystemExit as e:
            self.log.error('App failed in run() method ({}).'.format(e))
            return self._exit(e.code)
        except Exception:
            self.log.error(
                'App encountered except in run() method ({}).'.format(traceback.format_exc())
            )
            return self._exit(1)

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

        # stage any staging data
        self.stager.redis.from_dict(profile.get('stage', {}).get('redis', {}))

        # build args from install.json
        args = {}
        args.update(profile.get('inputs', {}).get('required', {}))
        args.update(profile.get('inputs', {}).get('optional', {}))
        if not args:
            self.log.error('No profile named {} found.'.format(profile_name))
            return self._exit(1)

        # run the App
        exit_code = self.run(args)

        # populate the output variables
        # TODO: [INT-1320] investigate improvements
        if exit_code == 0:
            self.populate_output_variables(profile_name)

        return self._exit(exit_code)

    def setup_method(self):
        """Run before each test method runs."""
        super(TestCasePlaybook, self).setup_method()
        self.stager.redis.from_dict(self.redis_staging_data)
        self.redis_client = self.tcex.playbook.db.r

    def teardown_method(self):
        """Run after each test method runs."""
        r = self.stager.redis.delete_context(self.context)
        self.log_data('teardown method', 'delete count', r)
        super(TestCasePlaybook, self).teardown_method()
