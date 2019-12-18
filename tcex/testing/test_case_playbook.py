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
        self.app = self.app_init(args)

        # Start
        exit_code = self.run_app_method(self.app, 'start')
        if exit_code != 0:
            return exit_code

        # Run
        try:
            if hasattr(self.app.args, 'tc_action') and self.app.args.tc_action is not None:
                tc_action = self.app.args.tc_action
                tc_action_formatted = tc_action.lower().replace(' ', '_')
                tc_action_map = 'tc_action_map'
                if hasattr(self.app, tc_action):
                    getattr(self.app, tc_action)()
                elif hasattr(self.app, tc_action_formatted):
                    getattr(self.app, tc_action_formatted)()
                elif hasattr(self.app, tc_action_map):
                    self.app.tc_action_map.get(
                        self.app.args.tc_action
                    )()  # pylint: disable=no-member
                else:
                    self.log.error(
                        'Action method ({}) was not found.'.format(self.app.args.tc_action)
                    )
                    self._exit(1)
            else:
                self.app.run()
        except SystemExit as e:
            self.log.error('App failed in run() method ({}).'.format(e))
            return self._exit(e.code)
        except Exception:
            self.log.error(
                'App encountered except in run() method ({}).'.format(traceback.format_exc())
            )
            return self._exit(1)

        # Write Output
        exit_code = self.run_app_method(self.app, 'write_output')
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

        # build args from install.json
        args = {}
        args.update(profile.get('inputs', {}).get('required', {}))
        args.update(profile.get('inputs', {}).get('optional', {}))

        # run the App
        exit_code = self.run(args)

        # add context for populating output variables
        self.context_tracker.append(self.context)

        return exit_code

    def setup_method(self):
        """Run before each test method runs."""
        super(TestCasePlaybook, self).setup_method()
        self.stager.redis.from_dict(self.redis_staging_data)
        self.redis_client = self.tcex.playbook.db.r
