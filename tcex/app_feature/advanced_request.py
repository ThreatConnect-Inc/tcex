# -*- coding: utf-8 -*-
"""ThreatConnect Exchange App Feature Advanced Request Module"""
# standard library
import json
from argparse import Namespace
from mimetypes import MimeTypes
from typing import Dict, List, Optional, Union

# third-party
import requests

from ..decorators import ReadArg


class AdvancedRequest:
    """App Feature Advanced Request Module

    Args:
        session (object): An instance of Requests Session object.
        tcex (object): An instance of Tcex object.
        timeout (Optional[int] = 600): The timeout value for the request.
    """

    def __init__(self, session: object, tcex: object, timeout: Optional[int] = 600):
        """Initialize class properties."""
        self.session: object = session
        self.tcex: object = tcex

        # properties
        self.args: Namespace = tcex.args  # required for ReadArgs
        self.allow_redirects: bool = True
        self.data: Optional[Union[dict, str]] = None
        self.headers: dict = {}
        self.max_mb: int = 500
        self.mt: callable = MimeTypes()
        self.output_prefix: str = self.tcex.ij.output_prefix
        self.params: dict = {}
        self.timeout: int = timeout or 600

    @ReadArg('tc_adv_req_body')
    def configure_body(self, tc_adv_req_body: Union[bytes, str]):
        """Configure Body

        Args:
            tc_adv_req_body (Union[bytes, str]): The request body.
        """
        self.data: Union[bytes, str] = tc_adv_req_body
        if self.data is not None:
            # INT-1386
            try:
                self.data: str = self.data.encode('utf-8')
            except AttributeError:
                pass  # Binary Data

        if self.args.tc_adv_req_urlencode_body:
            try:
                self.data: dict = json.loads(self.data)
            except ValueError:  # pragma: no cover
                self.tcex.log.error('Failed loading body as JSON data.')

    @ReadArg('tc_adv_req_headers', array=True)
    def configure_headers(self, tc_adv_req_headers: List[Dict[str, str]]):
        """Configure Headers

        [{
            "key": "User-Agent",
            "value": "TcEx MyApp: 1.0.0",
        }]

        Args:
            tc_adv_req_headers (List[Dict[str, str]]): A dict of headers.
        """
        for header_data in tc_adv_req_headers:
            self.headers[str(header_data.get('key'))] = header_data.get('value')

    @ReadArg('tc_adv_req_params', array=True)
    def configure_params(self, tc_adv_req_params: List[Dict[str, str]]):
        """Configure Params

        [{
            "count": "500",
            "page": "1",
        }]

        Args:
            tc_adv_req_params (List[Dict[str, str]]): A dict of Params.
        """
        for param_data in tc_adv_req_params:
            param: str = str(param_data.get('key'))
            values: str = param_data.get('value')
            if not isinstance(values, list):
                values: list = [values]
            for value in values:
                if not value and self.args.tc_adv_req_exclude_null_params:
                    self.tcex.log.warning(
                        f'Query parameter {param} has a null/empty value '
                        'and will not be added to the request.'
                    )
                else:
                    self.params.setdefault(param, []).append(str(value))

    @ReadArg(
        'tc_adv_req_http_method',
        fail_on=[None, ''],
        fail_enabled=True,
        fail_msg='Invalid method provide for request',
        strip_values=True,
    )
    @ReadArg(
        'tc_adv_req_path',
        fail_on=[None, ''],
        fail_enabled=True,
        fail_msg='Invalid path provide for request',
        strip_values=True,
    )
    def request(self, tc_adv_req_http_method: str, tc_adv_req_path: str):
        """Make the HTTP request.

        Args:
            tc_adv_req_http_method (str): The HTTP method to use.
            tc_adv_req_path (str): The REST API endpoint/path.
        """
        # configure body
        self.configure_body(**{})

        # configure headers
        self.configure_headers(**{})

        # configure params
        self.configure_params(**{})

        # make http request
        try:
            response: object = self.session.request(
                allow_redirects=self.allow_redirects,
                data=self.data,
                headers=self.headers,
                method=tc_adv_req_http_method,
                params=self.params,
                timeout=self.timeout,
                url=tc_adv_req_path,
            )
        except requests.exceptions.RequestException as e:  # pragma: no cover
            response = None
            raise RuntimeError(f'Exception during request ({e}).')

        # write outputs as soon as they are available
        self.tcex.playbook.add_output(
            f'{self.output_prefix}.request.headers', json.dumps(dict(response.headers)), 'String'
        )
        self.tcex.playbook.add_output(
            f'{self.output_prefix}.request.ok', str(response.ok).lower(), 'String'
        )
        self.tcex.playbook.add_output(
            f'{self.output_prefix}.request.reason', response.reason, 'String'
        )
        self.tcex.playbook.add_output(
            f'{self.output_prefix}.request.status_code', response.status_code, 'String'
        )
        self.tcex.playbook.add_output(
            f'{self.output_prefix}.request.url', response.request.url, 'String'
        )

        # get response size
        response_bytes: int = len(response.content)
        response_mb: float = response_bytes / 1000000
        self.tcex.log.info(f'Response MB: {response_mb}')
        if response_mb > self.max_mb:  # pragma: no cover
            raise RuntimeError('Download was larger than maximum supported 500 MB.')

        # write content after size validation
        self.tcex.playbook.add_output(
            f'{self.output_prefix}.request.content', response.text, 'String'
        )
        self.tcex.playbook.add_output(
            f'{self.output_prefix}.request.content.binary', response.content, 'Binary'
        )

        # fail if fail_on_error is selected and not ok
        if self.args.tc_adv_req_fail_on_error and not response.ok:
            raise RuntimeError(f'Failed for status ({response.status_code})')

        return response
