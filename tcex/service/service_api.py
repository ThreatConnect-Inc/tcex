# -*- coding: utf-8 -*-
"""TcEx Framework Service module"""
import base64
import json

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from .service_base import ServiceBase


class ServiceApi(ServiceBase):
    """Service methods for customer Service (e.g., Triggers)."""

    @staticmethod
    def format_query_string(params):
        """Convert name/value array to a query string."""
        query_string = ''
        for q in params:
            query_string += '{}={}'.format(q.get('name'), q.get('value'))
        return query_string

    @staticmethod
    def format_request_headers(headers):
        """Convert name/value array to a query string."""
        headers_ = {}
        for h in headers:
            headers_.setdefault(h.get('name').lower(), []).append(h.get('value'))
        return headers_

    @staticmethod
    def format_response_headers(headers):
        """Convert name/value array to a query string."""
        headers_ = []
        for h in headers:
            headers_.append({'name': h[0], 'value': h[1]})
        return headers_

    def api_service(self, callback):
        """Run subscribe method

        {
          "command": "RunService",
          "requestKey": "123abc",
          "method": "GET",
          "queryParams": [ { key/value pairs } ],
          "headers": [ { key/value pairs } ],
          "bodySessionId": "85be2761..."
          "responseBodySessionId": "91eee889..."
        }
        """
        if not self.tcex.default_args.tc_server_channel:
            raise RuntimeError('No server channel provided.')
        if not callable(callback):
            raise RuntimeError('Callback method is not a callable.')

        # start heartbeat
        self.heartbeat()

        # subscribe to channel/topic
        p = self.client.pubsub()
        p.subscribe(self.tcex.default_args.tc_server_channel)
        for m in p.listen():
            self.tcex.log.trace('server message: ({})'.format(m))
            # only process "message" on channel (exclude subscriptions)
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
            config = msg_data.get('config')  # used for shutdown command
            request_key = msg_data.get('requestKey')
            # body
            body = self.client.hget(request_key, 'request.body')
            if body is not None:
                body = StringIO(json.loads(base64.b64decode(body)))
            headers = self.format_request_headers(msg_data.get('headers'))
            method = msg_data.get('method')
            params = msg_data.get('queryParams')
            path = msg_data.get('path')

            environ = {
                'wsgi.errors': self.tcex.log.error,  # sys.stderr
                # 'wsgi.file_wrapper': <class 'wsgiref.util.FileWrapper'>
                'wsgi.input': body,
                'wsgi.multithread': True,
                'wsgi.multiprocess': False,
                'wsgi.run_once': True,
                'wsgi.url_scheme': 'https',
                'wsgi.version': (1, 0),
                'CONTENT_TYPE': headers.get('content-type', ''),
                'CONTENT_LENGTH': headers.get('content-length', 0),
                # 'GATEWAY_INTERFACE': 'CGI/1.1',
                # 'HTTP_ACCEPT': '',
                'HTTP_ACCEPT': headers.get('accept', ''),
                # 'HTTP_ACCEPT_ENCODING': '',
                # 'HTTP_ACCEPT_LANGUAGE': '',
                # 'HTTP_COOKIE': '',
                # 'HTTP_DNT': 1,
                # 'HTTP_CONNECTION': 'keep-alive',
                # 'HTTP_HOST': '',
                # 'HTTP_UPGRADE_INSECURE_REQUESTS': 1,
                'HTTP_USER_AGENT': headers.get('user-agent', ''),
                'PATH_INFO': path,
                'QUERY_STRING': self.format_query_string(params),
                # 'REMOTE_ADDR': '',
                # 'REMOTE_HOST': '',
                'REQUEST_METHOD': method.upper(),
                'SCRIPT_NAME': '/',
                # 'SERVER_NAME': '',
                # 'SERVER_PORT': '',
                'SERVER_PROTOCOL': 'HTTP/1.1',
                # 'SERVER_SOFTWARE': 'WSGIServer/0.2',
            }

            if not command:
                self.tcex.log.warning('Received a message without command ({})'.format(m))
                continue
            elif command == 'RunService':

                def response_handler(*args, **kwargs):  # pylint: disable=unused-argument
                    """Handle WSGI Response

                    ('200 OK', [('content-type', 'application/json'), ('content-length', '103')])
                    """
                    self.tcex.log.trace('args: {}'.format(args))
                    status_code, status = args[0].split(' ', 1)
                    response = {
                        'requestKey': request_key,  # pylint: disable=cell-var-from-loop
                        'status': status,
                        'statusCode': status_code,
                        'headers': self.format_response_headers(args[1]),
                        'body': 'response.body',
                    }
                    self.publish(json.dumps(response))

                body = callback(environ, response_handler)
                # decode body entries
                body = [base64.b64encode(b).decode('utf-8') for b in body]
                # write body to Redis
                self.client.hset(request_key, 'response.body', json.dumps(body))

            elif command == 'Shutdown':
                reason = (
                    'A shutdown command was received on server channel. Service is shutting down.',
                )
                if config:
                    reason = config.get('reason') or reason
                self.tcex.log.info('Shutdown - reason: {}'.format(reason))

                # acknowledge shutdown command
                self.publish(json.dumps({'status': 'Acknowledged', 'command': 'Shutdown'}))
                self.tcex.exit(0)  # final shutdown in case App did not
