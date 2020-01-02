# -*- coding: utf-8 -*-
"""TcEx Webhook Trigger Server Test Case"""
import traceback

from .test_case_service_common import TestCaseServiceCommon


class TestCaseWebhookTriggerService(TestCaseServiceCommon):
    """WebhookTrigger App TestCase Class"""

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
            self.app.tcex.service.webhook_event_callback = self.app.webhook_event_callback

            self.app.tcex.service.listen()
            self.app.tcex.service.heartbeat()
            self.app.tcex.service.ready = True
            if hasattr(self.app, 'loop_forever'):
                self.app.loop_forever()
            else:
                self.app.tcex.service.loop_forever()
        except SystemExit as e:
            self.log.error(f'App failed in run() method ({e}).')
            return self._exit(e.code)
        except Exception:
            self.log.error(f'App encountered except in run() method ({traceback.format_exc()}).')
            return self._exit(1)

        # Teardown
        exit_code = self.run_app_method(self.app, 'teardown')
        if exit_code != 0:
            return exit_code

        return self._exit(self.app.tcex.exit_code)
