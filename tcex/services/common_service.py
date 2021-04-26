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
        self._start_time = datetime.now()
        self.args: object = tcex.default_args
        self.configs = {}
        self.heartbeat_max_misses = 3
        self.heartbeat_sleep_time = 1
        self.heartbeat_watchdog = 0
        self.ij = tcex.ij
        self.key_value_store = self.tcex.key_value_store
        self.log = tcex.log
        self.logger = tcex.logger
        self.message_broker = MqttMessageBroker(
            broker_host=self.args.tc_svc_broker_host,
            broker_port=self.args.tc_svc_broker_port,
            broker_timeout=self.args.tc_svc_broker_conn_timeout,
            broker_token=self.args.tc_svc_broker_token,
            broker_cacert=self.args.tc_svc_broker_cacert_file,
            logger=tcex.log,
        )
        self.ready = False
        self.redis_client = self.tcex.redis_client
        self.token = tcex.token

        # config callbacks
        self.shutdown_callback = None

    def _create_logging_handler(self):
        """Create a logging handler."""
        if self.logger.handler_exist(self.thread_name):
            return

        # create trigger id logging filehandler
        self.logger.add_pattern_file_handler(
            name=self.thread_name,
            filename=f'''{datetime.today().strftime('%Y%m%d')}/{self.session_id}.log''',
            level=self.args.tc_log_level,
            path=self.args.tc_log_path,
            # uuid4 pattern for session_id
            pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}.log$',
            handler_key=self.session_id,
            thread_key='session_id',
        )

    def process_acknowledged_command(
        self, message: dict
    ) -> None:  # pylint: disable=unused-argument
        """Process the Acknowledge command.

        Args:
            message: The message payload from the server topic.
        """
        self.log.info(f'feature=service, event=acknowledge, message={message}')

    def add_metric(self, label: str, value: Union[int, str]) -> None:
        """Add a metric.

        Metrics are reported in heartbeat message.

        Args:
            label: The metric label (e.g., hits) to add.
            value: The value for the metric.
        """
        self._metrics[label] = value

    @property
    def command_map(self) -> dict:
        """Return the command map for the current Service type."""
        return {
            'acknowledged': self.process_acknowledged_command,
            'brokercheck': self.process_broker_check,
            'heartbeat': self.process_heartbeat_command,
            'loggingchange': self.process_logging_change_command,
            'shutdown': self.process_shutdown_command,
        }

    @staticmethod
    def create_session_id() -> str:  # pylint: disable=unused-argument
        """Return a uuid4 session id.

        Returns:
            str: A unique UUID string value.
        """
        return str(uuid.uuid4())

    def heartbeat(self) -> None:
        """Start heartbeat process."""
        self.service_thread(name='heartbeat', target=self.heartbeat_monitor)

    def heartbeat_broker_check(self) -> None:
        """Send self check message to ensure communications with message broker."""
        message = {
            'command': 'BrokerCheck',
            'date': str(datetime.now()),
            'heartbeat_watchdog': self.heartbeat_watchdog,
        }
        self.message_broker.publish(
            message=json.dumps(message), topic=self.args.tc_svc_server_topic
        )

        # allow time for message to be received
        time.sleep(5)

    def heartbeat_monitor(self) -> None:
        """Publish heartbeat on timer."""
        self.log.info('feature=service, event=heartbeat-monitor-started')
        while True:
            # check heartbeat is not missed
            if self.heartbeat_watchdog > (
                int(self.args.tc_svc_hb_timeout_seconds) / int(self.heartbeat_sleep_time)
            ):
                # send self check message
                self.heartbeat_broker_check()

                self.log.error(
                    'feature=service, event=missed-heartbeat, action=shutting-service-down'
                )
                self.process_shutdown_command({'reason': 'Missed heartbeat commands.'})
                break
            time.sleep(self.heartbeat_sleep_time)
            self.heartbeat_watchdog += 1

    def increment_metric(self, label: str, value: Optional[int] = 1) -> None:
        """Increment a metric if already exists.

        Args:
            label: The metric label (e.g., hits) to increment.
            value: The increment value. Defaults to 1.
        """
        if self._metrics.get(label) is not None:
            self._metrics[label] += value

    def listen(self) -> None:
        """List for message coming from broker."""
        self.message_broker.add_on_connect_callback(self.on_connect_handler)
        self.message_broker.add_on_message_callback(
            self.on_message_handler, topics=[self.args.tc_svc_server_topic]
        )
        self.message_broker.register_callbacks()

        # start listener thread
        self.service_thread(name='broker-listener', target=self.message_broker.connect)

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

    def on_connect_handler(
        self, client, userdata, flags, rc  # pylint: disable=unused-argument
    ) -> None:
        """On connect method for mqtt broker."""
        self.log.info(
            f'feature=service, event=topic-subscription, topic={self.args.tc_svc_server_topic}'
        )
        self.message_broker.client.subscribe(self.args.tc_svc_server_topic)
        self.message_broker.client.disable_logger()

    def on_message_handler(
        self, client, userdata, message  # pylint: disable=unused-argument
    ) -> None:
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
        trigger_id: Optional[int] = m.get('triggerId')
        if trigger_id is not None:
            # coerce trigger_id to int in case a string was provided (testing framework)
            trigger_id = int(trigger_id)
        self.log.info(f'feature=service, event=command-received, command="{command}"')

        # create unique session id to be used as thread name
        # and stored as property of thread for logging emit
        session_id = self.create_session_id()

        # get the target method from command_map for the current command
        thread_method = self.command_map.get(command, self.process_invalid_command)
        self.service_thread(
            # use session_id as thread name to provide easy debugging per thread
            name=session_id,
            target=thread_method,
            args=(m,),
            session_id=session_id,
            trigger_id=trigger_id,
        )

    def process_broker_check(self, message: dict) -> None:
        """Implement parent method to log a broker check message.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            {
                "command": "BrokerCheck",
            }

        Args:
            message: The message payload from the server topic.
        """
        self.log.warning(f'feature=service, event=broker-check, message={message}')

    def process_heartbeat_command(self, message: dict) -> None:  # pylint: disable=unused-argument
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
            message=json.dumps(response), topic=self.args.tc_svc_client_topic
        )
        self.log.info(f'feature=service, event=heartbeat-sent, metrics={self.metrics}')

    def process_logging_change_command(self, message: dict) -> None:
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
        self.logger.update_handler_level(level)

    def process_invalid_command(self, message: dict) -> None:
        """Process all invalid commands.

        Args:
            message: The message payload from the server topic.
        """
        self.log.warning(
            f'feature=service, event=invalid-command-received, message="""({message})""".'
        )

    def process_shutdown_command(self, message: dict) -> None:
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
            self.args.tc_svc_client_topic,
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

        # TODO: [review] this doesn't help if MainThread does not die.
        # # delay shutdown to give App time to cleanup
        # time.sleep(5)
        # self.tcex.exit(0)  # final shutdown in case App did not

    @property
    def ready(self) -> bool:
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
                if self.ij.runtime_level.lower() in ['apiservice']:
                    ready_command['discoveryTypes'] = self.ij.service_discovery_types
                self.message_broker.publish(
                    json.dumps(ready_command), self.args.tc_svc_client_topic
                )
                self._ready = True

    def service_thread(
        self,
        name: str,
        target: Callable[[], bool],
        args: Optional[tuple] = None,
        kwargs: Optional[dict] = None,
        session_id: Optional[str] = None,
        trigger_id: Optional[int] = None,
    ) -> None:
        """Start a message thread.

        Args:
            name: The name of the thread.
            target: The method to call for the thread.
            args: The args to pass to the target method.
            kwargs: Additional args.
            session_id: The current session id.
            trigger_id: The current trigger id.
        """
        self.log.info(f'feature=service, event=service-thread-creation, name={name}')
        args = args or ()
        try:
            t = threading.Thread(name=name, target=target, args=args, kwargs=kwargs, daemon=True)
            # add session_id to thread to use in logger emit
            t.session_id = session_id
            # add trigger_id to thread to use in logger emit
            t.trigger_id = trigger_id
            t.start()
        except Exception:
            self.log.trace(traceback.format_exc())

    @property
    def session_id(self) -> Optional[str]:
        """Return the current session_id."""
        if not hasattr(threading.current_thread(), 'session_id'):
            threading.current_thread().session_id = self.create_session_id()
        return threading.current_thread().session_id

    @property
    def thread_name(self) -> str:
        """Return a uuid4 session id."""
        return threading.current_thread().name

    @property
    def trigger_id(self) -> Optional[int]:
        """Return the current trigger_id."""
        trigger_id = None
        if hasattr(threading.current_thread(), 'trigger_id'):
            trigger_id = threading.current_thread().trigger_id
            if trigger_id is not None:
                trigger_id = int(trigger_id)
        return trigger_id

    def update_metric(self, label: str, value: Union[int, str]) -> None:
        """Update a metric if already exists.

        Args:
            label: The metric label (e.g., hits) to update.
            value: The updated value for the metric.
        """
        if self._metrics.get(label) is not None:
            self._metrics[label] = value
