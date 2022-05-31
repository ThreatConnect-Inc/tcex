"""ThreatConnect Exchange App Feature Advanced Request Module"""
# standard library
import json
import logging
from mimetypes import MimeTypes
from typing import Optional, Union

# third-party
import requests

# first-party
from tcex.input.input import Input
from tcex.playbook import Playbook

# get tcex logger
logger = logging.getLogger('tcex')


class AdvancedRequest:
    """App Feature Advanced Request Module

    Args:
        inputs: The instance of App inputs.
        playbooks: An instance Playbooks.
        session: An instance of Requests Session object.
        output_prefix: The output prefix.
        timeout: The timeout value for the request.
    """

    def __init__(
        self,
        inputs: Input,
        playbook: Playbook,
        session: requests.Session,
        output_prefix: str,
        timeout: Optional[int] = 600,
    ):
        """Initialize class properties."""
        self.inputs = inputs
        self.output_prefix: str = output_prefix
        self.playbook = playbook
        self.session = session
        self.timeout: int = timeout or 600

        # properties
        self.allow_redirects: bool = True
        self.data: Optional[Union[dict, str]] = None
        self.headers: dict = {}
        self.log = logger
        self.max_mb: int = 500
        self.mt: callable = MimeTypes()
        self.params: dict = {}

    def configure_body(self):
        """Configure Body"""
        self.data: Union[bytes, str] = self.inputs.model.tc_adv_req_body
        if self.data is not None:
            # INT-1386
            try:
                self.data: str = self.data.encode('utf-8')
            except AttributeError:
                pass  # Binary Data

        if self.inputs.model.tc_adv_req_urlencode_body:
            try:
                self.data: dict = json.loads(self.data)
            except ValueError:  # pragma: no cover
                self.log.error('Failed loading body as JSON data.')

    def configure_headers(self):
        """Configure Headers

        [{
            "key": "User-Agent",
            "value": "TcEx MyApp: 1.0.0",
        }]
        """
        for header_data in self.inputs.model.tc_adv_req_headers:
            value: str = self.playbook.read.variable(header_data.get('value'))
            self.headers[str(header_data.get('key'))] = str(value)

    def configure_params(self):
        """Configure Params

        [{
            "count": "500",
            "page": "1",
        }]
        """
        for param_data in self.inputs.model.tc_adv_req_params:
            param: str = str(param_data.get('key'))
            values: str = self.playbook.read.variable(param_data.get('value'))
            if not isinstance(values, list):
                values: list = [values]
            for value in values:
                if not value and self.inputs.model.tc_adv_req_exclude_null_params:
                    self.log.warning(
                        f'Query parameter {param} has a null/empty value '
                        'and will not be added to the request.'
                    )
                else:
                    self.params.setdefault(param, []).append(str(value))

    def request(self):
        """Make the HTTP request."""
        # configure body
        self.configure_body()

        # configure headers
        self.configure_headers()

        # configure params
        self.configure_params()

        # make http request
        try:
            response: object = self.session.request(
                allow_redirects=self.allow_redirects,
                data=self.data,
                headers=self.headers,
                method=self.inputs.model.tc_adv_req_http_method,
                params=self.params,
                timeout=self.timeout,
                url=self.inputs.model.tc_adv_req_path,
            )
        except requests.exceptions.RequestException as e:  # pragma: no cover
            response = None
            raise RuntimeError(f'Exception during request ({e}).')

        # write outputs as soon as they are available
        self.playbook.create.variable(
            f'{self.output_prefix}.request.headers', json.dumps(dict(response.headers)), 'String'
        )
        self.playbook.create.variable(
            f'{self.output_prefix}.request.ok', str(response.ok).lower(), 'String'
        )
        self.playbook.create.variable(
            f'{self.output_prefix}.request.reason', response.reason, 'String'
        )
        self.playbook.create.variable(
            f'{self.output_prefix}.request.status_code', response.status_code, 'String'
        )
        self.playbook.create.variable(
            f'{self.output_prefix}.request.url', response.request.url, 'String'
        )

        # get response size
        response_bytes: int = len(response.content)
        response_mb: float = response_bytes / 1000000
        self.log.info(f'Response MB: {response_mb}')
        if response_mb > self.max_mb:  # pragma: no cover
            raise RuntimeError('Download was larger than maximum supported 500 MB.')

        # write content after size validation
        self.playbook.create.variable(
            f'{self.output_prefix}.request.content', response.text, 'String'
        )
        self.playbook.create.variable(
            f'{self.output_prefix}.request.content.binary', response.content, 'Binary'
        )

        # fail if fail_on_error is selected and not ok
        if self.inputs.model.tc_adv_req_fail_on_error and not response.ok:
            raise RuntimeError(f'Failed for status ({response.status_code})')

        return response
