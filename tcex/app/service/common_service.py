"""TcEx Framework Module"""

# standard library
import json
import logging
import threading
import time
import traceback
import uuid
from collections.abc import Callable
from datetime import datetime

# first-party
from tcex.app.config import InstallJson
from tcex.app.key_value_store.key_value_store import KeyValueStore
from tcex.app.playbook.playbook import Playbook
from tcex.app.service.mqtt_message_broker import MqttMessageBroker
from tcex.app.token import Token
from tcex.input.model.module_app_model import ModuleAppModel
from tcex.logger.logger import Logger
from tcex.logger.trace_logger import TraceLogger
from tcex.util.util import Util

# get tcex logger
_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


class CommonService:
    """TcEx Framework Service Common module

    Shared service logic between the supported service types:
    * API Service
    * Custom Trigger Service
    * Webhook Trigger Service
    """

    def __init__(
        self,
        key_value_store: KeyValueStore,
        logger: Logger,
        model: ModuleAppModel,
        token: Token,
    ):
        """Initialize the Class properties."""
        # properties
        self._ready = False
        self._start_time = datetime.now()
        self.model = model
        self.configs = {}
        self.heartbeat_max_misses = 3
        self.heartbeat_sleep_time = 1
        self.heartbeat_watchdog = 0
        self.ij = InstallJson()
        self.key_value_store = key_value_store
        self.log = _logger
        self.logger = logger
        self.message_broker = MqttMessageBroker(
            broker_host=self.model.tc_svc_broker_host,
            broker_port=self.model.tc_svc_broker_port,
            broker_timeout=self.model.tc_svc_broker_conn_timeout,
            broker_token=self.model.tc_svc_broker_token,
            broker_cacert=self.model.tc_svc_broker_cacert_file,
        )
        self.ready = False
        self.redis_client = self.key_value_store.redis_client
        self.token = token
        self.util = Util()

        # config callbacks
        self.shutdown_callback = None

    def get_playbook(
        self, context: str | None = None, output_variables: list | None = None
    ) -> Playbook:
        """Return a new instance of playbook module.

        Args:
            context: The KV Store context/session_id. For PB Apps the context is provided on
                startup, but for service Apps each request gets a different context.
            output_variables: The requested output variables. For PB Apps outputs are provided on
                startup, but for service Apps each request gets different outputs.
        """
        return Playbook(self.key_value_store, context, output_variables)

    def process_acknowledged_command(self, message: dict):
        """Process the Acknowledge command.

        Args:
            message: The message payload from the server topic.
        """
        self.log.info(f'feature=service, event=acknowledge, message={message}')

    def add_metric(self, label: str, value: int | str):
        """Add a metric.

        Metrics are reported in heartbeat message.

        Args:
            label: The metric label (e.g., hits) to add.
            value: The value for the metric.
        """
        self._metrics[label] = value

    @property
    def command_map(self) -> dict[str, Callable[[dict], None]]:
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

    def heartbeat(self):
        """Start heartbeat process."""
        self.service_thread(name='heartbeat', target=self.heartbeat_monitor)

    def heartbeat_broker_check(self):
        """Send self check message to ensure communications with message broker."""
        message = {
            'command': 'BrokerCheck',
            'date': str(datetime.now()),
            'heartbeat_watchdog': self.heartbeat_watchdog,
        }
        self.message_broker.publish(
            message=json.dumps(message), topic=self.model.tc_svc_server_topic
        )

        # allow time for message to be received
        time.sleep(5)

    def heartbeat_monitor(self):
        """Publish heartbeat on timer."""
        self.log.info('feature=service, event=heartbeat-monitor-started')
        while True:
            # check heartbeat is not missed
            if self.heartbeat_watchdog > (
                int(self.model.tc_svc_hb_timeout_seconds) / int(self.heartbeat_sleep_time)
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

    def increment_metric(self, label: str, value: int = 1):
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
            self.on_message_handler, topics=[self.model.tc_svc_server_topic]
        )
        self.message_broker.register_callbacks()

        # start listener thread
        self.service_thread(name='broker-listener', target=self.message_broker.connect)

    def loop_forever(self, sleep: int = 1) -> bool:
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
        """Return current metric."""
        # TODO: move to trigger command and handle API Service
        if self._metrics.get('Active Playbooks') is not None:
            self.update_metric('Active Playbooks', len(self.configs))
        return self._metrics

    @metrics.setter
    def metrics(self, metrics: dict):
        """Return current metric."""
        if isinstance(metrics, dict):
            self._metrics = metrics
        else:
            self.log.error('feature=service, event=invalid-metric')

    def on_connect_handler(self, client, userdata, flags, rc):  # pylint: disable=unused-argument
        """On connect method for mqtt broker."""
        self.log.info(
            f'feature=service, event=topic-subscription, topic={self.model.tc_svc_server_topic}'
        )
        self.message_broker.client.subscribe(self.model.tc_svc_server_topic)
        self.message_broker.client.disable_logger()

    def on_message_handler(self, client, userdata, message):  # pylint: disable=unused-argument
        """On message for mqtt."""
        try:
            # messages on server topic must be json objects
            m = json.loads(message.payload)
            if m.get('triggerId') not in [None, '']:
                m['triggerId'] = int(m['triggerId'])
        except ValueError:
            self.log.warning(
                f'feature=service, event=parsing-issue, message="""{message.payload}"""'
            )
            return

        # use the command to call the appropriate method defined in command_map
        command = m.get('command', 'invalid').lower()
        trigger_id = m.get('triggerId')
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

    def process_broker_check(self, message: dict):
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
            message=json.dumps(response), topic=self.model.tc_svc_client_topic
        )
        self.log.info(f'feature=service, event=heartbeat-sent, metric={self.metrics}')

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
        level = message['level']
        self.log.info(f'feature=service, event=logging-change, level={level}')
        self.logger.update_handler_level(level)

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
            self.model.tc_svc_client_topic,
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
        self.message_broker.client.unsubscribe(self.model.tc_svc_server_topic)
        self.message_broker.client.disconnect()

        # update shutdown flag
        self.message_broker.shutdown = True

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
                ready_command: dict[str, list[str] | str] = {'command': 'Ready'}
                if self.ij.model.is_api_service_app and self.ij.model.service:
                    ready_command['discoveryTypes'] = self.ij.model.service.discovery_types
                self.message_broker.publish(
                    json.dumps(ready_command), self.model.tc_svc_client_topic
                )
                self._ready = True

    def service_thread(
        self,
        name: str,
        target: Callable[..., bool | None],
        args: tuple | None = None,
        kwargs: dict | None = None,
        session_id: str | None = None,
        trigger_id: int | None = None,
    ):
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
            t.session_id = session_id  # type: ignore
            # trigger id is used in Token module for the unique key for a token
            t.trigger_id = str(trigger_id)  # type: ignore
            t.start()
        except Exception:
            self.log.trace(traceback.format_exc())

    @property
    def session_id(self) -> str:
        """Return the current session_id."""
        if not hasattr(threading.current_thread(), 'session_id'):
            threading.current_thread().session_id = self.create_session_id()  # type: ignore
        return threading.current_thread().session_id  # type: ignore

    @property
    def thread_name(self) -> str:
        """Return a uuid4 session id."""
        return threading.current_thread().name

    def update_metric(self, label: str, value: int | str):
        """Update a metric if already exists.

        Args:
            label: The metric label (e.g., hits) to update.
            value: The updated value for the metric.
        """
        if self._metrics.get(label) is not None:
            self._metrics[label] = value
