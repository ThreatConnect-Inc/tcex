"""TcEx Framework Service Common module"""
# standard library
import json
import threading
import time
import traceback
import uuid
from datetime import datetime
from typing import Callable, Optional, Union

from .mqtt_message_broker import MqttMessageBroker


class CommonService:
    """TcEx Framework Service Common module

    Shared service logic between the supported service types:
    * API Service
    * Custom Trigger Service
    * Webhook Trigger Service
    """

    def __init__(self, tcex: object):
        """Initialize the Class properties.

        Args:
            tcex: Instance of TcEx.
        """
        self.tcex = tcex

        # properties
        self._ready = False
        self._redis_client = None
        self._start_time = datetime.now()
        self.args: object = tcex.default_args
        # TODO: remove after moving metric
        self.configs = {}
        self.heartbeat_max_misses = 3
        self.heartbeat_sleep_time = 1
        self.heartbeat_watchdog = 0
        self.log = tcex.log
        self.message_broker = MqttMessageBroker(
            broker_host=tcex.default_args.tc_svc_broker_host,
            broker_port=tcex.default_args.tc_svc_broker_port,
            broker_timeout=tcex.default_args.tc_svc_broker_conn_timeout,
            broker_token=tcex.default_args.tc_svc_broker_token,
            broker_cacert=tcex.default_args.tc_svc_broker_cacert_file,
            logger=tcex.log,
        )
        self.ready = False

        # config callbacks
        self.shutdown_callback = None

    def add_metric(self, label: str, value: Union[int, str]):
        """Add a metric.

        Metrics are reported in heartbeat message.

        Args:
            label: The metric label (e.g., hits) to add.
            value: The value for the metric.
        """
        self._metrics[label] = value

    @property
    def command_map(self):
        """Return the command map for the current Service type."""
        return {
            'heartbeat': self.process_heartbeat_command,
            'loggingchange': self.process_logging_change_command,
            'shutdown': self.process_shutdown_command,
        }

    def heartbeat(self):
        """Start heartbeat process."""
        t = threading.Thread(name='heartbeat', target=self.heartbeat_monitor, daemon=True)
        t.start()

    def heartbeat_monitor(self):
        """Publish heartbeat on timer."""
        self.log.info('feature=service, event=heartbeat-monitor-started')
        while True:
            if self.heartbeat_watchdog > (
                int(self.args.tc_svc_hb_timeout_seconds) / int(self.heartbeat_sleep_time)
            ):
                self.log.error(
                    'feature=service, event=missed-heartbeat, action=shutting-service-down'
                )
                self.process_shutdown_command({'reason': 'Missed heartbeat commands.'})
                break
            time.sleep(self.heartbeat_sleep_time)
            self.heartbeat_watchdog += 1

    def increment_metric(self, label: str, value: Optional[int] = 1):
        """Increment a metric if already exists.

        Args:
            label: The metric label (e.g., hits) to increment.
            value: The increment value. Defaults to 1.
        """
        if self._metrics.get(label) is not None:
            self._metrics[label] += value

    def listen(self):
        """List for message coming from broker."""
        self.message_broker.add_on_connect_callback(self.on_connect_handler)
        self.message_broker.add_on_message_callback(
            self.on_message_handler, topics=[self.args.tc_svc_server_topic]
        )

        self.message_broker.register_callbacks()

        t = threading.Thread(
            name='broker-listener', target=self.message_broker.connect, args=(), daemon=True
        )
        t.start()

    def loop_forever(self, sleep: Optional[int] = 1) -> bool:
        """Block and wait for shutdown.

        Args:
            sleep: The amount of time to sleep between iterations. Defaults to 1.

        Returns:
            Bool: Returns True until shutdown received.
        """
        while True:
            deadline = time.time() + sleep
            while time.time() < deadline:
                if self.message_broker.shutdown:
                    return False
                time.sleep(1)
            return True

    def message_thread(
        self, name: str, target: Callable[[], bool], args: tuple, kwargs: Optional[dict] = None
    ):
        """Start a message thread.

        Args:
            name: The name of the thread.
            target: The method to call for the thread.
            args: The args to pass to the target method.
            kwargs: Additional args.
        """
        try:
            t = threading.Thread(name=name, target=target, args=args, kwargs=kwargs, daemon=True)
            t.start()
        except Exception:
            self.log.trace(traceback.format_exc())

    @property
    def metrics(self) -> dict:
        """Return current metrics."""
        # TODO: move to trigger command and handle API Service
        if self._metrics.get('Active Playbooks') is not None:
            self.update_metric('Active Playbooks', len(self.configs))
        return self._metrics

    @metrics.setter
    def metrics(self, metrics: dict):
        """Return current metrics."""
        if isinstance(metrics, dict):
            self._metrics = metrics
        else:
            self.log.error('feature=service, event=invalid-metrics')

    def on_connect_handler(self, client, userdata, flags, rc):  # pylint: disable=unused-argument
        """On connect method for mqtt broker."""
        self.log.info(
            f'feature=service, event=topic-subscription, topic={self.args.tc_svc_server_topic}'
        )
        self.message_broker.client.subscribe(self.args.tc_svc_server_topic)
        self.message_broker.client.disable_logger()

    def on_message_handler(self, client, userdata, message):  # pylint: disable=unused-argument
        """On message for mqtt."""
        try:
            # messages on server topic must be json objects
            m = json.loads(message.payload)
        except ValueError:
            self.log.warning(
                f'feature=service, event=parsing-issue, message="""{message.payload}"""'
            )
            return

        # use the command to call the appropriate method defined in command_map
        command: str = m.get('command', 'invalid').lower()
        self.log.info(f'feature=service, event=command-received, command="{command}"')
        self.command_map.get(command, self.process_invalid_command)(m)

    def process_heartbeat_command(self, message: dict):  # pylint: disable=unused-argument
        """Process the HeartBeat command.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            {
                "command": "Heartbeat",
                "metric": {},
                "memoryPercent": 0,
                "cpuPercent": 0
            }

        Args:
            message: The message payload from the server topic.
        """
        self.heartbeat_watchdog = 0

        # send heartbeat -acknowledge- command
        response = {'command': 'Heartbeat', 'metric': self.metrics}
        self.message_broker.publish(
            message=json.dumps(response), topic=self.tcex.default_args.tc_svc_client_topic
        )
        self.log.info(f'feature=service, event=heartbeat-sent, metrics={self.metrics}')

    def process_logging_change_command(self, message: dict):
        """Process the LoggingChange command.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            {
                "command": "LoggingChange",
                "level": "DEBUG"
            }

        Args:
            message: The message payload from the server topic.
        """
        level: str = message.get('level')
        self.log.info(f'feature=service, event=logging-change, level={level}')
        self.tcex.logger.update_handler_level(level)

    def process_invalid_command(self, message: dict):
        """Process all invalid commands.

        Args:
            message: The message payload from the server topic.
        """
        self.log.warning(
            f'feature=service, event=invalid-command-received, message="""({message})""".'
        )

    def process_shutdown_command(self, message: dict):
        """Implement parent method to process the shutdown command.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            {
                "command": "Shutdown",
                "reason": "Service disabled by user."
            }

        Args:
            message: The message payload from the server topic.
        """
        reason = message.get('reason') or (
            'A shutdown command was received on server topic. Service is shutting down.'
        )
        self.log.info(f'feature=service, event=shutdown, reason={reason}')

        # acknowledge shutdown command
        self.message_broker.publish(
            json.dumps({'command': 'Acknowledged', 'type': 'Shutdown'}),
            self.tcex.default_args.tc_svc_client_topic,
        )

        # call App shutdown callback
        if callable(self.shutdown_callback):
            try:
                # call callback for shutdown and handle exceptions to protect thread
                self.shutdown_callback()  # pylint: disable=not-callable
            except Exception as e:
                self.log.error(
                    f'feature=service, event=shutdown-callback-error, error="""({e})""".'
                )
                self.log.trace(traceback.format_exc())

        # unsubscribe and disconnect from the broker
        self.message_broker.client.unsubscribe(self.args.tc_svc_server_topic)
        self.message_broker.client.disconnect()

        # update shutdown flag
        self.message_broker.shutdown = True

        # delay shutdown to give App time to cleanup
        time.sleep(5)
        self.tcex.exit(0)  # final shutdown in case App did not

    @property
    def ready(self):
        """Return ready boolean."""
        return self._ready

    @ready.setter
    def ready(self, bool_val: bool):
        """Set ready boolean."""
        if isinstance(bool_val, bool) and bool_val is True:
            # wait until connected to send ready command
            while not self.message_broker._connected:
                if self.message_broker.shutdown:
                    break
                time.sleep(1)
            else:  # pylint: disable=useless-else-on-loop
                self.log.info('feature=service, event=service-ready')
                ready_command = {'command': 'Ready'}
                if self.tcex.ij.runtime_level.lower() in ['apiservice']:
                    ready_command['discoveryTypes'] = self.tcex.ij.service_discovery_types
                self.message_broker.publish(
                    json.dumps(ready_command), self.tcex.default_args.tc_svc_client_topic
                )
                self._ready = True

    @property
    def redis_client(self):
        """Return the correct KV store for this execution."""
        if self._redis_client is None:
            self._redis_client: object = self.tcex.redis_client
        return self._redis_client

    @staticmethod
    def session_id(trigger_id: Optional[str] = None):  # pylint: disable=unused-argument
        """Return a uuid4 session id.

        Takes optional trigger_id for monkeypatch in testing framework.

        Args:
            trigger_id (str): Optional trigger_id value used in testing framework.
        """
        return str(uuid.uuid4())

    @property
    def thread_name(self):
        """Return a uuid4 session id."""
        return threading.current_thread().name

    def update_metric(self, label: str, value: Union[int, str]):
        """Update a metric if already exists.

        Args:
            label: The metric label (e.g., hits) to update.
            value: The updated value for the metric.
        """
        if self._metrics.get(label) is not None:
            self._metrics[label] = value
