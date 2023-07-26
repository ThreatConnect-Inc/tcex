"""TcEx Framework Module"""
# standard library
import logging
import ssl
import time
import traceback
from collections.abc import Callable

# third-party
import paho.mqtt.client as mqtt

# first-party
from tcex.input.field_type.sensitive import Sensitive
from tcex.logger.trace_logger import TraceLogger
from tcex.pleb.cached_property import cached_property

# get tcex logger
_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


class MqttMessageBroker:
    """TcEx Framework MQTT message broker module."""

    def __init__(
        self,
        broker_host: str,
        broker_port: int,
        broker_timeout: int,
        broker_token: Sensitive | None = None,
        broker_cacert: str | None = None,
    ):
        """Initialize the Class properties.

        Args:
            broker_host: The MQTT server host (IP).
            broker_port: The MQTT server port.
            broker_timeout: The MQTT connection timeout.
            broker_token: The MQTT connect token.
            broker_cacert: The CA certfile for connection.
            logger: A logging instance
        """
        self.broker_host = broker_host
        self.broker_port = int(broker_port)
        self.broker_timeout = int(broker_timeout)
        self.broker_token = broker_token
        self.broker_cacert = broker_cacert

        # properties
        self._connected = False
        self._on_connect_callbacks: list[Callable] = []
        self._on_disconnect_callbacks: list[Callable] = []
        self._on_log_callbacks: list[Callable] = []
        self._on_message_callbacks: list[dict[str, Callable | list[str]]] = []
        self._on_publish_callbacks: list[Callable] = []
        self._on_subscribe_callbacks: list[Callable] = []
        self._on_unsubscribe_callbacks: list[Callable] = []
        self.log = _logger
        self.shutdown = False  # used in service App for shutdown flag

    def add_on_connect_callback(self, callback: Callable, index: int | None = None):
        """Add a callback for on_connect events.

        Args:
            callback: A callback that matches signature of an on_connect event.
            index: The index value to insert the callback into the list.
        """
        index = index or len(self._on_connect_callbacks)
        self._on_connect_callbacks.insert(index, callback)

    def add_on_disconnect_callback(self, callback: Callable, index: int | None = None):
        """Add a callback for on_disconnect events.

        Args:
            callback: A callback that matches signature of an on_disconnect event.
            index: The index value to insert the callback into the list.
        """
        index = index or len(self._on_disconnect_callbacks)
        self._on_disconnect_callbacks.insert(index, callback)

    def add_on_log_callback(self, callback: Callable, index: int | None = None):
        """Add a callback for on_log events.

        Args:
            callback: A callback that matches signature of an on_log event.
            index: The index value to insert the callback into the list.
        """
        index = index or len(self._on_log_callbacks)
        self._on_log_callbacks.insert(index, callback)

    def add_on_message_callback(
        self, callback: Callable, index: int | None = None, topics: list[str] | None = None
    ):
        """Add a callback for on_message events.

        Args:
            callback: A callback that matches signature of an on_message event.
            index: The index value to insert the callback into the list.
            topics: A optional list of topics to call callback. If value is None then callback
                will always be called.
        """
        index = index or len(self._on_message_callbacks)
        topics = topics or []
        self._on_message_callbacks.insert(index, {'callback': callback, 'topics': topics})

    def add_on_publish_callback(self, callback: Callable, index: int | None = None):
        """Add a callback for on_publish events.

        Args:
            callback: A callback that matches signature of an on_publish event.
            index: The index value to insert the callback into the list.
        """
        index = index or len(self._on_publish_callbacks)
        self._on_publish_callbacks.insert(index, callback)

    def add_on_subscribe_callback(self, callback: Callable, index: int | None = None):
        """Add a callback for on_subscribe events.

        Args:
            callback: A callback that matches signature of an on_subscribe event.
            index: The index value to insert the callback into the list.
        """
        index = index or len(self._on_subscribe_callbacks)
        self._on_subscribe_callbacks.insert(index, callback)

    def add_on_unsubscribe_callback(self, callback: Callable, index: int | None = None):
        """Add a callback for on_unsubscribe events.

        Args:
            callback: A callback that matches signature of an on_unsubscribe event.
            index: The index value to insert the callback into the list.
        """
        index = index or len(self._on_unsubscribe_callbacks)
        self._on_unsubscribe_callbacks.insert(index, callback)

    @cached_property
    def client(self) -> mqtt.Client:
        """Return MQTT client."""
        _client = mqtt.Client(client_id='', clean_session=True)
        try:
            _client.reconnect_delay_set(min_delay=1, max_delay=5)
            _client.connect(self.broker_host, self.broker_port, self.broker_timeout)
            if self.broker_cacert is not None:
                _client.tls_set(
                    ca_certs=self.broker_cacert,
                    cert_reqs=ssl.CERT_REQUIRED,
                    tls_version=ssl.PROTOCOL_TLSv1_2,
                )
                _client.tls_insecure_set(False)
            # add logger when logging in TRACE
            if self.log.getEffectiveLevel() == 5:
                _client.enable_logger(logger=self.log)
            # username must be a empty string
            if self.broker_token is not None:
                _client.username_pw_set('', password=self.broker_token.value)

        except Exception as e:
            self.log.error(f'feature=message-broker, event=failed-connection, error="""{e}"""')
            self.log.trace(traceback.format_exc())
            self.shutdown = True

        return _client

    def connect(self):
        """Listen for message coming from broker."""
        try:
            # handle connection issues by not using loop_forever. give the service X seconds to
            # connect to message broker, else timeout and log generic connection error.
            self.client.loop_start()
            deadline = time.time() + self.broker_timeout
            while True:
                if not self._connected and deadline < time.time():
                    self.client.loop_stop()
                    raise ConnectionError(
                        f'failed to connect to message broker host '
                        f'{self.broker_host} on port '
                        f'{self.broker_port}.'
                    )
                time.sleep(1)

        except Exception as e:
            self.log.trace(f'feature=message-broker, event=connection-error, error="""{e}"""')
            self.log.error(traceback.format_exc())

    def on_connect(self, client, userdata, flags, rc):
        """Handle MQTT on_connect events."""
        self.log.info(f'feature=message-broker, event=broker-connect, status={str(rc)}')
        self._connected = True
        for callback in self._on_connect_callbacks:
            callback(client, userdata, flags, rc)

    def on_disconnect(self, client, userdata, rc):
        """Handle MQTT on_disconnect events."""
        self.log.info(f'feature=message-broker, event=broker-disconnect, status={str(rc)}')
        for callback in self._on_disconnect_callbacks:
            callback(client, userdata, rc)

    def on_log(self, client, userdata, level, buf):
        """Handle MQTT on_log events."""
        # self.log.trace(f'feature=message-broker, event=on_log, buf={buf}, level={level}')
        for callback in self._on_log_callbacks:
            callback(client, userdata, level, buf)

    def on_message(self, client, userdata, message):
        """Handle MQTT on_message events."""
        mp = message.payload.decode().replace('\n', '')
        self.log.trace(
            f'''feature=message-broker, message-topic={message.topic}, message-payload={mp}'''
        )
        for cd in self._on_message_callbacks:
            topics = cd.get('topics')
            if topics is None or message.topic in topics:
                if callable(cd['callback']):
                    cd['callback'](client, userdata, message)

    def on_publish(self, client, userdata, result):
        """Handle MQTT on_publish events."""
        # self.log.trace(f'feature=message-broker, event=on_publish, result={result}')
        for callback in self._on_publish_callbacks:
            callback(client, userdata, result)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        """Handle MQTT on_subscribe events."""
        # self.log.trace(
        #     f'feature=message-broker, event=on_subscribe, mid={mid}, granted_qos={granted_qos}'
        # )
        for callback in self._on_subscribe_callbacks:
            callback(client, userdata, mid, granted_qos)

    def on_unsubscribe(self, client, userdata, mid):
        """Handle MQTT on_unsubscribe events."""
        # self.log.trace(f'feature=message-broker, event=on_subscribe, mid={mid}')
        for callback in self._on_unsubscribe_callbacks:
            callback(client, userdata, mid)

    def publish(self, message: str, topic: str):
        """Publish a message on client topic.

        Args:
            message: The message to be sent on client topic.
            topic: The broker topic.
        """
        r = self.client.publish(topic, message)
        self.log.debug(
            f'feature=service, event=publish-message, topic="{topic}", '
            f'message={message}, response={r}'
        )

    def register_callbacks(self):
        """Register all the message broker callbacks."""
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.on_subscribe = self.on_subscribe
        self.client.on_unsubscribe = self.on_unsubscribe
