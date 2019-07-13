# -*- coding: utf-8 -*-
"""TcEx Framework Service module"""
import json
import threading
from .service_base import ServiceBase


class ServiceTrigger(ServiceBase):
    """Service methods for customer Service (e.g., Triggers)."""

    def add_metric(self, label, value):
        """Add a metric to get reported in heartbeat."""
        self._metric[label] = str(value)

    def custom_trigger(
        self,
        create_callback=None,
        delete_callback=None,
        update_callback=None,
        shutdown_callback=None,
    ):
        """Add custom trigger

        Args:
            create_callback (callable): Method or function to call when create config command
                received. Default to None.
            update_callback (callable): Method or function to call when update config command
                received. Default to None.
            delete_callback (callable): Method or function to call when delete config command
                received. Default to None.
            shutdown_callback (callable): Method or function to call when shutdown command received.
                Default to None.
        """
        if not self.tcex.default_args.tc_server_channel:
            raise RuntimeError('No server channel provided.')

        # start heartbeat
        self.heartbeat()

        self.tcex.log.trace('initialized')
        self.config_thread = threading.Thread(
            target=self.custom_trigger_subscriber,
            args=(create_callback, delete_callback, update_callback, shutdown_callback),
        )
        self.config_thread.daemon = True  # use setter for py2
        self.config_thread.start()

    def custom_trigger_subscriber(
        self,
        create_callback=None,
        delete_callback=None,
        update_callback=None,
        shutdown_callback=None,
    ):
        """Add custom trigger subscriber

        Args:
            create_callback (callable): Method or function to call when create config command
                received. Default to None.
            update_callback (callable): Method or function to call when update config command
                received. Default to None.
            delete_callback (callable): Method or function to call when delete config command
                received. Default to None.
            shutdown_callback (callable): Method or function to call when shutdown command received.
                Default to None.
        """
        if not self.tcex.default_args.tc_server_channel:
            self.tcex.exit(1, 'No server channel provided.')

        self.tcex.log.trace('subscriber thread started.')

        p = self.client.pubsub()
        p.subscribe(self.tcex.default_args.tc_server_channel)
        for m in p.listen():
            self.tcex.log.trace('server message: ({})'.format(m))

            # only process "message" on channel (exclude subscriptions, etc)
            if m.get('type') != 'message':
                continue

            try:
                # load message data
                msg_data = json.loads(m.get('data'))
            except ValueError:
                self.tcex.log.warning('Cannot parse message ({}).'.format(m))
                continue

            # parse message data contents
            command = msg_data.get('command')
            # parameters for config commands
            trigger_id = msg_data.get('triggerId')
            config = msg_data.get('config')

            if not command:
                self.tcex.log.warning('Received a message without command ({})'.format(m))
                continue

            if command == 'Shutdown':
                p.unsubscribe(self.tcex.default_args.tc_server_channel)
                break

            # process config message
            self.process_message(
                command=command,
                config=config,
                trigger_id=trigger_id,
                create_callback=create_callback,
                delete_callback=delete_callback,
                update_callback=update_callback,
                shutdown_callback=shutdown_callback,
            )

        # final process config command after shutdown
        self.tcex.log.trace('final process command')
        if command == 'Shutdown':
            self.process_message(
                command=command,
                config=config,
                trigger_id=trigger_id,
                create_callback=create_callback,
                delete_callback=delete_callback,
                update_callback=update_callback,
                shutdown_callback=shutdown_callback,
            )
