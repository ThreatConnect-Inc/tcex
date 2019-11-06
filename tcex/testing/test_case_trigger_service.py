# -*- coding: utf-8 -*-
"""TcEx Service Common Module"""
import traceback
from six import string_types
from .test_case_service_common import TestCaseServiceCommon


class TestCaseTriggerService(TestCaseServiceCommon):
    """Service App TestCase Class"""

    def run(self, args):  # pylint: disable=too-many-return-statements
        """Run the Playbook App.

        Args:
            args (dict): The App CLI args.

        Returns:
            int: The App exit code
        """
        # resolve env vars
        for k, v in list(args.items()):
            if isinstance(v, string_types):
                args[k] = self.resolve_env_args(v)

        args['tc_playbook_out_variables'] = ','.join(self.output_variables)
        self.log_data('run', 'args', args)
        self.app = self.app_init(args)

        # Setup
        exit_code = self.run_app_method(self.app, 'setup')
        if exit_code != 0:
            return exit_code

        # Trigger
        try:
            # configure custom trigger message handler
            self.app.tcex.service.create_config_callback = self.app.create_config_callback
            self.app.tcex.service.delete_config_callback = self.app.delete_config_callback
            self.app.tcex.service.shutdown_callback = self.app.shutdown_callback

            self.app.tcex.service.listen()
            self.app.tcex.service.heartbeat()
            self.app.tcex.service.ready = True
        except SystemExit as e:
            self.log.error('App failed in run() method ({}).'.format(e))
            return self._exit(e.code)
        except Exception:
            self.log.error(
                'App encountered except in run() method ({}).'.format(traceback.format_exc())
            )
            return self._exit(1)

        # Run
        exit_code = self.run_app_method(self.app, 'run')
        if exit_code != 0:
            return exit_code

        # Teardown
        exit_code = self.run_app_method(self.app, 'teardown')
        if exit_code != 0:
            return exit_code

        return self._exit(self.app.tcex.exit_code)
