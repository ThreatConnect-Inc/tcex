"""TcEx Service Common Module"""
# standard library
import http.server
import json
import os
import socketserver
import sys
import time
from threading import Event, Thread
from typing import Optional
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

# third-party
from requests.auth import HTTPBasicAuth

# first-party
from tcex.sessions import ExternalSession

from .test_case_service_common import TestCaseServiceCommon


class ApiServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """HTTP Server for testing API Services"""

    allow_reuse_address = True

    def __init__(self, test_case: object, bind_addr: tuple):
        """Initialize Class properties

        Args:
            test_case: The test_case object.
            bind_addr: The binding address w/ port.
        """
        super().__init__(bind_addr, RequestHandler)
        self.test_case = test_case

        # properties
        self._host = bind_addr[0]
        self._port = bind_addr[1]
        self.active_requests = {}
        self.active_responses = {}
        self.args = test_case.default_args
        self.log = test_case.log
        self.message_broker = test_case.message_broker
        self.mqtt_client = test_case.message_broker.client

        # start server thread
        service = Thread(group=None, target=self.run, name='SimpleServerThread', daemon=True)
        service.start()

    def listen(self):
        """List for message coming from broker."""
        self.message_broker.add_on_connect_callback(self.on_connect)
        self.message_broker.add_on_message_callback(
            callback=self.on_message, topics=[self.test_case.client_topic]
        )

        t = Thread(name='broker-listener', target=self.message_broker.connect, args=(), daemon=True)
        t.start()

    def on_connect(self, client, userdata, flags, rc):  # pylint: disable=unused-argument
        """Handle message broker on_connect events."""
        # subscribe to client topic
        client.subscribe(self.test_case.client_topic)

    def on_message(self, client, userdata, message):  # pylint: disable=unused-argument
        """Handle message broker on_message events."""
        try:
            m = json.loads(message.payload)
        except ValueError:
            raise RuntimeError(f'Could not parse API service response JSON. ({message})')

        # only process RunService Acknowledged commands.
        if m.get('command').lower() == 'acknowledged' and m.get('type').lower() == 'runservice':
            self.active_responses[m.get('requestKey')] = m
            self.active_requests.pop(m.get('requestKey')).set()

    def run(self):
        """Run the server in threat."""
        print(f'\nRunning server: http://{self._host}:{self._port}')
        self.serve_forever()


class RequestHandler(http.server.BaseHTTPRequestHandler):
    """Request handler to forward request to API service."""

    def _build_request(self, method: str) -> dict:
        """Return request built from incoming HTTP request.

        {
            "apiToken": "SVC:5:RgIo6v:1596670377509:95:vWO1zu8W0a2NyXctWORKMe/kA616P6Vk8dsYvG ... ",
            "appId": 95,
            "bodyVariable": "request.body",
            "command": "RunService",
            "expireSeconds": 1596670377,
            "headers": [
                {
                    "name": "Accept",
                    "value": "*/*"
                },
                {
                    "name": "User-Agent",
                    "value": "PostmanRuntime/7.26.2"
                },
                {
                    "name": "Content-Type",
                    "value": "application/json"
                }
            ],
            "method": "GET",
            "path": "/data",
            "queryParams": [
                {
                    "name": "max",
                    "value": "1000"
                }
            ],
            "requestKey": "c29927c8-b94d-4116-a397-e6eb7002f41c"
        }

        Args:
            method: The HTTP method.

        Returns:
            dict: The response to send to API service over message broker topic.
        """
        url_parts = urlparse(self.path)

        # query params
        params = []
        for name, value in parse_qs(url_parts.query).items():
            if isinstance(value, list):
                for v in value:
                    params.append({'name': name, 'value': v})
            else:
                params.append({'name': name, 'value': value})

        # forward request to service
        request_key = str(uuid4())

        content_length = int(self.headers.get('content-length', 0))
        if content_length:
            body = self.rfile.read(content_length)
            self.server.test_case.redis_client.hset(request_key, 'request.body', body)

        request_url = self.headers.get('Host', 'http://localhost:8042')

        if request_url and not request_url.startswith(('http://', 'https://')):
            request_url = f'https://{request_url}'

        return {
            'apiToken': self.server.test_case.tc_token,
            'appId': 95,
            'bodyVariable': 'request.body',
            'command': 'RunService',
            'expireSeconds': int(time.time() + 600),
            'headers': [{'name': name, 'value': value} for name, value in self.headers.items()],
            'method': method,
            'path': url_parts.path,
            'queryParams': params,
            'requestKey': request_key,
            'requestUrl': request_url,
            'remoteAddress': '127.0.0.1',
        }

    def _build_response(self, response: Optional[dict] = None) -> None:
        """Build response data from API service response.

        {
            "bodyVariable": "response.body",
            "command": "Acknowledged",
            "headers": [
                {
                    "name": "x-cache",
                    "value": "MISS"
                },
                {
                    "name": "retry-after",
                    "value": "20"
                },
                {
                    "name": "content-type",
                    "value": "application/json"
                },
            ],
            "requestKey": "97190c5a-05e7-493d-8cb5-33844190eb72",
            "status": "Too Many Requests",
            "statusCode": "429",
            "type": "RunService"
        }

        Args:
            response: The response data from API service.
        """
        if response is None:
            self.send_error(500, message='No response sent on message broker client channel.')
            return

        # status code
        self.send_response(int(response.get('statusCode')))

        # headers
        for header in response.get('headers'):
            self.send_header(header.get('name'), str(header.get('value')))
        self.end_headers()

        # body
        body = self.server.test_case.redis_client.hget(response.get('requestKey'), 'response.body')
        if body is not None:
            self.wfile.write(body)

    def call_service(self, method: str):  # pylint: disable=useless-return
        """Call the API Service

        Args:
            method: The HTTP method.
        """
        request = self._build_request(method)
        request_key = request.get('requestKey')

        # create lock and sve request
        event = Event()
        self.server.active_requests[request_key] = event

        # publish run service
        self.server.test_case.publish(
            message=json.dumps(request), topic=self.server.test_case.server_topic
        )

        # block for x seconds
        event.wait(60)
        response: dict = self.server.active_responses.pop(request_key, None)

        self._build_response(response=response)

        return

    def do_DELETE(self):
        """Handle DELETE method."""
        return self.call_service('DELETE')

    def do_GET(self):
        """Handle GET method."""
        return self.call_service('GET')

    def do_PATCH(self):
        """Handle PATCH method."""
        return self.call_service('PATCH')

    def do_POST(self):
        """Handle POST method."""
        return self.call_service('POST')


class TestCaseApiService(TestCaseServiceCommon):
    """Service App TestCase Class"""

    _test_client = None
    api_server = None
    api_service_host = os.getenv('API_SERVICE_HOST')
    api_service_path = ''
    api_service_path_base = '/api/services'
    api_service_port = os.getenv('API_SERVICE_PORT')
    api_service_protocol = 'https://'
    api_service_type = None
    stop_server = False

    def on_message(self, client, userdata, message):  # pylint: disable=unused-argument
        """Handle message broker on_message shutdown command events."""
        try:
            m = json.loads(message.payload)
        except ValueError:
            raise RuntimeError(f'Could not parse API service response JSON. ({message})')

        # only process RunService Acknowledged commands.
        if message.topic == self.server_topic and m.get('command').lower() == 'shutdown':
            self.stop_server = True

    def run(self):
        """Run the Playbook App.

        Returns:
            int: The App exit code
        """
        if not self.utils.to_bool(os.getenv('API_SERVICE_RUN', 'false')):
            return None

        # first-party
        from run import run  # pylint: disable=no-name-in-module

        # backup sys.argv
        sys_argv_orig = sys.argv

        # clear sys.argv
        sys.argv = sys.argv[:1]

        # run the app
        exit_code = 0
        try:
            # provide callback to to run.py method on Trigger Service Apps
            run(set_app=self._app_callback)  # pylint: disable=unexpected-keyword-arg
        except SystemExit as e:
            exit_code = e.code

        # restore sys.argv
        sys.argv = sys_argv_orig

        self.log.data('run', 'Exit Code', exit_code)
        return exit_code

    def setup_method(self):
        """Run before each test method runs."""
        if not self.utils.to_bool(os.getenv('API_SERVICE_RUN', 'false')):
            super().setup_method()
            return

        self.api_service_host = 'localhost'
        self.api_service_path = ''
        self.api_service_path_base = ''
        self.api_service_protocol = 'http://'
        self.api_service_port = 8042

        self.api_server = ApiServer(self, (self.api_service_host, self.api_service_port))
        self.api_server.listen()

        # subscribe to server topic
        self.message_broker.client.subscribe(self.server_topic)

        # register on_message shutdown monitor
        self.message_broker.add_on_message_callback(
            callback=self.on_message, index=0, topics=[self.server_topic]
        )

        super().setup_method()

    def teardown_method(self):
        """Run after each test method runs."""
        if not self.utils.to_bool(os.getenv('API_SERVICE_RUN', 'false')):
            super().teardown_method()
            return

        self.api_server.server_close()
        super().teardown_method()

    @property
    def test_client(self):
        """Return test client."""
        if not self._test_client:
            if not self.api_service_host:
                self.tcex.exit(1, 'Required env variable: API_SERVICE_HOST not set.')
            base_url = f'{self.api_service_protocol}{self.api_service_host}'
            if self.api_service_port:
                base_url += f':{int(self.api_service_port)}'
            base_url += f'{self.api_service_path_base}{self.api_service_path}'
            self._test_client = self.tcex.session
            if self.api_service_type.lower() == 'external':
                self._test_client = ExternalSession(base_url)
            else:
                self._test_client.base_url = base_url
        return self._test_client

    def set_test_client_auth(self, username: str, password: str) -> None:
        """Set basic auth on test_client.

        Args:
            username: The basic auth username.
            password: The basic auth password.
        """
        self.test_client.auth = HTTPBasicAuth(username, password)
