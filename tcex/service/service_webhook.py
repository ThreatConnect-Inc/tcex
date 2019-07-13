# -*- coding: utf-8 -*-
"""TcEx Framework Service module"""
import json
from .service_base import ServiceBase


class ServiceWebhook(ServiceBase):
    """Service methods for customer Service (e.g., Triggers)."""

    def webhook_trigger(
        self,
        callback,
        create_callback=None,
        delete_callback=None,
        update_callback=None,
        shutdown_callback=None,
    ):
        """Add webhook subscriber

        {
          "command": "WebhookEvent",
          "requestKey": "123abc",
          "method": "GET",
          "queryParams": [{"name": "one", "value": 1}],
          "headers": [{"name": "User-Agent', "value": "Chrome"}],
          "body": "request.body"
        }

        Args:
            callback (callable): Method or function to call when webhook is triggered.
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
        if not callable(callback):
            raise RuntimeError('Callback method is not a callable.')

        # start heartbeat
        self.heartbeat()

        # subscribe to redis channel
        p = self.client.pubsub()
        p.subscribe(self.tcex.default_args.tc_server_channel)
        for m in p.listen():
            self.tcex.log.trace('broker message: ({})'.format(m))

            # only process "message" on channel (exclude subscriptions, etc)
            if m.get('type') != 'message':
                continue

            try:
                # load message data
                msg_data = json.loads(m.get('data'))
            except ValueError:
                self.tcex.log.warning('Cannot parse message ({}).'.format(m))
                continue
            self.tcex.log.trace('msg_data: ({})'.format(msg_data))

            # parse message data contents
            command = msg_data.get('command')
            # parameters for config commands
            trigger_id = msg_data.get('triggerId')
            config = msg_data.get('config')

            self.tcex.log.trace('command: ({})'.format(command))
            self.tcex.log.trace('trigger_id: ({})'.format(trigger_id))
            self.tcex.log.trace('config: ({})'.format(config))
            if not command:
                self.tcex.log.warning('Received a message without command ({})'.format(m))
                continue
            elif command.lower() == 'webhookevent':
                request_key = msg_data.get('requestKey')
                self.tcex.log.info(
                    'WebhookEvent - trigger_id: {} request_key : {}'.format(trigger_id, request_key)
                )
                self.fire_event(
                    callback, msg_data=msg_data, request_key=request_key, trigger_type='webhook'
                )
            else:
                self.process_message(
                    command=command,
                    config=config,
                    trigger_id=trigger_id,
                    create_callback=create_callback,
                    delete_callback=delete_callback,
                    update_callback=update_callback,
                    shutdown_callback=shutdown_callback,
                )
