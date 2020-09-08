"""TcEx Framework API Service module."""
# standard library
import json
import sys
import threading
import traceback
from io import BytesIO
from typing import Any

from .common_service import CommonService


class ApiService(CommonService):
    """TcEx Framework API Service module."""

    def __init__(self, tcex: object):
        """Initialize the Class properties.

        Args:
            tcex: Instance of TcEx.
        """
        super().__init__(tcex)

        # properties
        self._metrics = {'Errors': 0, 'Requests': 0, 'Responses': 0}

        # config callbacks
        self.api_event_callback = None

    @property
    def command_map(self) -> dict:
        """Return the command map for the current Service type."""
        command_map = super().command_map
        command_map.update({'runservice': self.process_run_service_command})
        return command_map

    def format_query_string(self, params: dict) -> str:
        """Convert name/value array to a query string.

        Args:
            params: The query params for the request.

        Returns:
            str: The query params reformatted as a string.
        """
        query_string = []
        try:
            for q in params:
                query_string.append(f'''{q.get('name')}={q.get('value')}''')
        except AttributeError as e:
            self.log.error(
                f'feature=api-service, event=bad-params-provided, params={params}, error="""{e})"""'
            )
            self.log.trace(traceback.format_exc())
        return '&'.join(query_string)

    def format_request_headers(self, headers: dict) -> dict:
        """Convert name/value array to a headers dict.

        Args:
            headers: The dict of key/value header data.

        Returns:
            dict: The restructured header data.
        """
        headers_ = {}
        try:
            for h in headers:
                # TODO: either support tuple or csv list of values
                # headers_.setdefault(h.get('name').lower(), []).append(h.get('value'))
                headers_.setdefault(h.get('name').lower(), str(h.get('value')))

        except AttributeError as e:
            self.log.error(
                f'feature=api-service, event=bad-headers-provided, '
                f'headers={headers}, error="""{e})"""'
            )
            self.log.trace(traceback.format_exc())
        return headers_

    def format_response_headers(self, headers: dict) -> dict:
        """Convert name/value array to a query string.

        Args:
            headers: The dict header data to be converted to key/value pairs.

        Returns:
            dict: The restructured header data.
        """
        headers_ = []
        try:
            for h in headers:
                headers_.append({'name': h[0], 'value': h[1]})
        except AttributeError as e:
            self.log.error(
                f'feature=api-service, event=bad-headers-provided, '
                f'headers={headers}, error="""{e})"""'
            )
            self.log.trace(traceback.format_exc())
        return headers_

    def process_run_service_response(self, *args, **kwargs) -> None:
        """Handle service event responses.

        ('200 OK', [('content-type', 'application/json'), ('content-length', '103')])
        """
        self.log.info('feature=api-service, event=response-received, status=waiting-for-body')
        kwargs.get('event').wait(30)  # wait for thread event - (set on body write)
        self.log.trace(f'feature=api-service, event=response, args={args}')
        try:
            status_code, status = args[0].split(' ', 1)
            response = {
                'bodyVariable': 'response.body',
                'command': 'Acknowledged',
                'headers': self.format_response_headers(args[1]),
                'requestKey': kwargs.get('request_key'),  # pylint: disable=cell-var-from-loop
                'status': status,
                'statusCode': status_code,
                'type': 'RunService',
            }
            self.log.info('feature=api-service, event=response-sent')
            self.message_broker.publish(json.dumps(response), self.args.tc_svc_client_topic)
            self.increment_metric('Responses')
        except Exception as e:
            self.log.error(
                f'feature=api-service, event=failed-creating-response-body, error="""{e}"""'
            )
            self.log.trace(traceback.format_exc())
            self.increment_metric('Errors')

    def process_run_service_command(self, message: dict) -> None:
        """Process the RunService command.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            {
              "command": "RunService",
              "apiToken": "abc123",
              "bodyVariable": "request.body",
              "headers": [ { key/value pairs } ],
              "method": "GET",
              "queryParams": [ { key/value pairs } ],
              "requestKey": "123abc",
              "userConfig": [{
                "name": "tlpExportSetting",
                "value": "TLP:RED"
              }],
            }

        Args:
            message: The message payload from the server topic.
        """
        # register config apiToken (before any logging)
        self.token.register_token(
            self.thread_name, message.get('apiToken'), message.get('expireSeconds')
        )
        self.log.info(f'feature=api-service, event=runservice-command, message="{message}"')

        # thread event used to block response until body is written
        event = threading.Event()

        # process message
        request_key: str = message.get('requestKey')
        body = None
        try:
            # read body from redis
            body_variable: str = message.get('bodyVariable')
            if body_variable is not None:
                body: Any = self.redis_client.hget(request_key, message.get('bodyVariable'))
                if body is not None:
                    # for API service the data in Redis is not b64 encoded
                    body = BytesIO(body)
        except Exception as e:
            self.log.error(f'feature=api-service, event=failed-reading-body, error="""{e}"""')
            self.log.trace(traceback.format_exc())
        headers: dict = self.format_request_headers(message.get('headers'))
        method: str = message.get('method')
        params: dict = message.get('queryParams')
        path: str = message.get('path')

        try:
            environ = {
                'wsgi.errors': sys.stderr,
                'wsgi.input': body,
                'wsgi.multithread': True,
                'wsgi.multiprocess': False,
                'wsgi.run_once': True,
                'wsgi.url_scheme': 'https',
                'wsgi.version': (1, 0),
                'PATH_INFO': path,
                'QUERY_STRING': self.format_query_string(params),
                'REMOTE_ADDR': message.get('remoteAddress', ''),
                # 'REMOTE_HOST': message.get('remoteAddress', ''),
                'REQUEST_METHOD': method.upper(),
                'SCRIPT_NAME': '/',
                'SERVER_NAME': '',
                'SERVER_PORT': '',
                'SERVER_PROTOCOL': 'HTTP/1.1',
            }

            # Add user config for TAXII or other service that supports the data type
            environ['user_config'] = message.get('userConfig', [])

            # add headers
            if headers.get('content-type') is not None:
                environ['CONTENT_TYPE'] = headers.pop('content-type')

            # add content length
            if headers.get('content-length') is not None:
                environ['CONTENT_LENGTH'] = headers.pop('content-length')

            for header, value in headers.items():
                environ[f'HTTP_{header}'.upper()] = value

            self.log.trace(f'feature=api-service, environ={environ}')
            self.increment_metric('Requests')
        except Exception as e:
            self.log.error(f'feature=api-service, event=failed-building-environ, error="""{e}"""')
            self.log.trace(traceback.format_exc())
            self.increment_metric('Errors')
            return  # stop processing

        def response_handler(*args, **kwargs):  # pylint: disable=unused-argument
            """Handle WSGI Response"""
            kwargs['event'] = event  # add event to kwargs for blocking
            kwargs['request_key'] = request_key
            self.service_thread(
                name='response-handler',
                target=self.process_run_service_response,
                args=args,
                kwargs=kwargs,
            )

        if callable(self.api_event_callback):
            try:
                body_data: Any = self.api_event_callback(  # pylint: disable=not-callable
                    environ, response_handler
                )

                # process body
                body = ''
                if hasattr(body_data, 'read'):
                    body = body_data.read()
                elif isinstance(body_data, list):
                    for bd in body_data:
                        if hasattr(bd, 'read'):
                            body += bd.read()
                        elif isinstance(bd, bytes):
                            body += bd.decode()
                        elif isinstance(bd, list):
                            for b in bd:
                                self.log.error(f'unhandled type - {type(b)}')
                        else:
                            self.log.error(f'unhandled type - {type(body)}')
                            self.log.error(f'unhandled type dir - {dir(body)}')

                # write body to Redis
                self.redis_client.hset(request_key, 'response.body', body)

                # set thread event to True to trigger response
                self.log.info('feature=api-service, event=response-body-written')
                event.set()
            except Exception as e:
                self.log.error(
                    f'feature=api-service, event=api-event-callback-failed, error="""{e}""".'
                )
                self.log.trace(traceback.format_exc())
                self.increment_metric('Errors')

        # unregister config apiToken
        self.token.unregister_token(self.thread_name)
