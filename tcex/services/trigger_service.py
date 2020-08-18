"""TcEx Framework Custom Service Trigger module."""
# standard library
import traceback
from typing import Callable, Optional, Union

from .common_service_trigger import CommonServiceTrigger


class TriggerService(CommonServiceTrigger):
    """TcEx Framework Service Common module."""

    def fire_event(self, callback: Callable[[], bool], **kwargs: list):
        """Trigger a FireEvent command.

        Args:
            callback: The trigger method in the App to call.
            trigger_ids: A list of trigger ids to trigger.
        """
        if not callable(callback):
            raise RuntimeError('Callback method (callback) is not a callable.')

        # get developer passed trigger_ids
        trigger_ids: Optional[list] = kwargs.pop('trigger_ids', None)

        for trigger_id, config in list(self.configs.items()):
            if trigger_ids is not None and trigger_id not in trigger_ids:
                # skip config that don't match developer provided trigger ids
                continue

            try:
                # get a session_id specifically for this thread
                session_id: str = self.session_id(trigger_id)

                # only required for testing in tcex framework
                self._tcex_testing(session_id, trigger_id)

                # get instance of playbook specifically for this thread
                outputs: Union[list, str] = config.get('tc_playbook_out_variables') or []
                if isinstance(outputs, str):
                    outputs = outputs.split(',')

                # get an instance of PB module with current session_id to pass to callback
                playbook: object = self.tcex.pb(context=session_id, output_variables=outputs)

                self.log.info(f'feature=trigger-service, event=fire-event, trigger-id={session_id}')

                # current thread has session_id as name
                args = (callback, playbook, trigger_id, config)
                self.message_thread(session_id, self.fire_event_trigger, args, kwargs)
            except Exception:
                self.log.trace(traceback.format_exc())

    def fire_event_trigger(
        self,
        callback: Callable[[], bool],
        playbook: object,
        trigger_id: int,
        config: dict,
        **kwargs: str,
    ):
        """Fire event for trigger.

        Args:
            callback: The App callback method for firing an event.
            playbook: A configure playbook instance for using to interact with KvStore.
            trigger_id: The current trigger Id.
            config: A dict containing the configuration information.
        """
        # tokens are registered with a key, in this case the key is the trigger_id. each thread
        # is required to be registered to a key to use during lookup.
        self.tcex.token.register_thread(trigger_id, self.thread_name)

        # add a logging handler for this thread
        self.tcex.logger.add_thread_file_handler(
            name=self.thread_name,
            filename=self.session_logfile,
            level=self.args.tc_log_level,
            path=self.args.tc_log_path,
        )
        self.log.info(
            f'feature=trigger-service, event=fire-event-trigger,  thread-name={self.thread_name}'
        )

        try:
            if callback(playbook, trigger_id, config, **kwargs):
                self.increment_metric('Hits')
                self.fire_event_publish(trigger_id, self.thread_name)

                # capture fired status for testing framework
                self._tcex_testing_fired_events(self.thread_name, True)
            else:
                self.increment_metric('Misses')
                self.log.info(
                    'feature=trigger-service, event=fire-event-callback-miss, '
                    f'trigger-id={trigger_id}'
                )

                # capture fired status for testing framework
                self._tcex_testing_fired_events(self.thread_name, False)
        except Exception as e:
            self.increment_metric('Errors')
            self.log.error(
                f'feature=trigger-service, event=fire-event-callback-exception, error="""{e}"""'
            )
            self.log.trace(traceback.format_exc())
        finally:
            # remove temporary logging file handler
            self.tcex.logger.remove_handler_by_name(self.thread_name)

            # unregister thread from token
            self.tcex.token.unregister_thread(trigger_id, self.thread_name)
