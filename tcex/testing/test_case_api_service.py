"""TcEx Service Common Module"""
# standard library
import http.server
import json
import os
import socketserver
import sys
import time
import traceback
from base64 import b64decode, b64encode
from threading import Event, Thread
from typing import Optional
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

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
        self._connected = False
        self.active_requests = {}
        self.active_responses = {}
        # self.args = test_case.args
        self.args = test_case.default_args
        self.log = test_case.log
        self.mqtt_client = test_case.mqtt_client

        # start server thread
        service = Thread(group=None, target=self.run, name='SimpleServerThread', daemon=True)
        service.start()

    def connect(self):
        """Listen for message coming from broker."""
        try:
            # handle connection issues by not using loop_forever. give the service X seconds to
            # connect to message broker, else timeout and log generic connection error.
            self.mqtt_client.loop_start()
            deadline = time.time() + self.args.get('tc_svc_broker_conn_timeout')
            while True:
                if not self._connected and deadline < time.time():
                    self.mqtt_client.loop_stop()
                    raise ConnectionError(
                        '''failed to connect to message broker host '''
                        f'''{self.args.get('tc_svc_broker_host')} on port '''
                        f'''{self.args.get('tc_svc_broker_port')}.'''
                    )
                time.sleep(1)

        except Exception as e:
            self.log.trace(f'error in listen_mqtt: {e}')
            self.log.error(traceback.format_exc())

    def listen(self):
        """List for message coming from broker."""
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        t = Thread(name='broker-listener', target=self.connect, args=(), daemon=True)
        t.start()

    def on_connect(self, client, userdata, flags, rc):  # pylint: disable=unused-argument
        """Handle MQTT on_connect events."""
        self.log.info(f'Message broker connection status: {str(rc)}')
        # subscribe to client topic
        client.subscribe(self.test_case.client_topic)
        self._connected = True

    def on_message(self, client, userdata, message):  # pylint: disable=unused-argument
        """Handle MQTT on_message events."""
        try:
            m = json.loads(message.payload)
        except ValueError:
            raise RuntimeError(f'Could not parse API service response JSON. ({message})')

        # self.active_requests[m.get('requestKey')] = m
        self.active_responses[m.get('requestKey')] = m
        self.active_requests.pop(m.get('requestKey')).set()

    def run(self):
        """Run the server in threat."""
        print('-- running server')
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

        # print('-- rfile dir', dir(self.rfile))
        # print('-- rfile type', type(self.rfile))

        content_length = int(self.headers.get('content-length', 0))
        # print('-- content_length', content_length)
        body = self.rfile.read(content_length)
        if body:
            body = b64encode(body)
        # print('-- body', body)
        # print('-- body', type(body))
        self.server.test_case.redis_client.hset(request_key, 'request.body', body)
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
            body = b64decode(body)
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
        self.server.test_case.publish(json.dumps(request))

        # block for x seconds
        event.wait(60)
        response: dict = self.server.active_responses.pop(request_key)

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

    api_service_host = os.getenv('API_SERVICE_HOST', 'localhost')
    api_service_port = int(os.getenv('API_SERVICE_PORT', '8042'))

    @property
    def test_client(self):
        """Return test client."""
        base_url = f'http://{self.api_service_host}:{self.api_service_port}'
        return ExternalSession(base_url)

    def run(self):
        """Run the Playbook App.

        Returns:
            int: The App exit code
        """
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
        api_server = ApiServer(self, (self.api_service_host, self.api_service_port))
        api_server.listen()

        super().setup_method()
