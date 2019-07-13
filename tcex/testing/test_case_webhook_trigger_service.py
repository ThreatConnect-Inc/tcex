# -*- coding: utf-8 -*-
"""TcEx Webhook Trigger Server Test Case"""
import traceback
from six import string_types
from .test_case_service_common import TestCaseServiceCommon


class TestCaseWebHookTriggerService(TestCaseServiceCommon):
    """WebHookTrigger App TestCase Class"""

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

        args['tc_playbook_out_variables'] = ','.join(self.output_variables)
        self.log_data('run', 'args', args)
        app = self.app(args)

        # Setup
        exit_code = self.run_app_method(app, 'setup')
        if exit_code != 0:
            return exit_code

        # Trigger
        try:
            # start the webhook trigger (blocking)
            app.tcex.service.webhook_trigger(
                callback=app.webhook_callback,
                create_callback=app.create_config_callback,
                delete_callback=app.delete_config_callback,
                update_callback=app.update_config_callback,
                shutdown_callback=app.shutdown_callback,
            )
        except SystemExit as e:
            self.log.error('App failed in run() method ({}).'.format(e))
            return self._exit(e.code)
        except Exception:
            self.log.error(
                'App encountered except in run() method ({}).'.format(traceback.format_exc())
            )
            return self._exit(1)

        # Teardown
        exit_code = self.run_app_method(app, 'teardown')
        if exit_code != 0:
            return exit_code

        return self._exit(app.tcex.exit_code)
