"""TcEx Framework MQTT message broker module."""
# standard library
import ssl
import time
import traceback
from typing import Optional

# third-party
import paho.mqtt.client as mqtt


class MqttMessageBroker:
    """TcEx Framework MQTT message broker module."""

    def __init__(
        self,
        broker_host: str,
        broker_port: int,
        broker_timeout: int,
        broker_token: str,
        broker_cacert: str,
        client_topic: str,
        logger: object,
    ):
        """Initialize the Class properties.

        Args:
            broker_host: The MQTT server host (IP).
            broker_port: The MQTT server port.
            broker_timeout: The MQTT connection timeout.
            broker_token: The MQTT connect token.
            broker_cacert: The CA certfile for connection.
            client_topic: The default client topic.
            logger: A logging instance
        """
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.broker_timeout = broker_timeout
        self.broker_token = broker_token
        self.broker_cacert = broker_cacert
        self.client_topic = client_topic
        self.log = logger

        # properties
        self._client = None
        self._connected = False

    @property
    def client(self):
        """Return MQTT client."""
        if self._client is None:
            try:
                self._client = mqtt.Client(client_id='', clean_session=True)
                self._client.connect(self.broker_host, self.broker_port, self.broker_timeout)
                self._client.tls_set(
                    ca_certs=self.broker_cacert,
                    cert_reqs=ssl.CERT_REQUIRED,
                    tls_version=ssl.PROTOCOL_TLSv1_2,
                )
                # add logger
                self._client.enable_logger(logger=self.log)
                # username must be a empty string
                self._client.username_pw_set('', password=self.broker_token)
                self._client.tls_insecure_set(False)
            except Exception as e:
                self.log.error(f'Failed connection to MQTT service ({e})')
                self.log.trace(traceback.format_exc())
                self.process_shutdown_command({'reason': 'Failure connecting to message broker.'})

        return self._client

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
            self.log.trace(f'error in listen_mqtt: {e}')
            self.log.error(traceback.format_exc())

    def on_connect(self, client, userdata, flags, rc):  # pylint: disable=unused-argument
        """Handle MQTT on_connect events."""
        self.log.info(f'Message broker connection status: {str(rc)}')

    def on_disconnect(self, client, userdata, rc):  # pylint: disable=unused-argument
        """Handle MQTT on_disconnect events."""
        self.log.info(f'Message broker connection status: {str(rc)}')

    def on_log(self, client, userdata, level, buf):  # pylint: disable=unused-argument
        """Handle MQTT on_log events."""
        self.log.trace(f'on_log - buf: {buf}, level: {level}')

    def on_message(self, client, userdata, message):  # pylint: disable=unused-argument
        """Handle MQTT on_message events."""
        self.log.trace(f'on_message - message.payload: {message.payload}')
        self.log.trace(f'on_message - message.topic: {message.topic}')

    def on_publish(self, client, userdata, result):  # pylint: disable=unused-argument
        """Handle MQTT on_publish events."""
        self.log.trace(f'on_publish - {result}')

    def on_subscribe(self, client, userdata, mid, granted_qos):  # pylint: disable=unused-argument
        """Handle MQTT on_subscribe events."""
        self.log.trace(f'on_subscribe - mid: {mid}, granted_qos: {granted_qos}')

    def on_unsubscribe(self, client, userdata, mid):  # pylint: disable=unused-argument
        """Handle MQTT on_unsubscribe events."""
        self.log.trace(f'on_subscribe - mid: {mid}')

    def process_shutdown_command(self, message: dict):
        """Stub for child class override."""
        raise NotImplementedError('This method must be implemented in child class.')

    def publish(self, message: str, topic: Optional[str] = None):
        """Publish a message on client topic.

        Args:
            message: The message to be sent on client topic.
            topic: The broker topic. Default to None.
        """
        if topic is None:
            topic: str = self.client_topic
        self.log.debug(f'publish topic: ({topic})')
        self.log.debug(f'publish message: ({message})')

        r: object = self.client.publish(topic, message)
        self.log.trace(f'publish response: {r}')
