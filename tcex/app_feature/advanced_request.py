# -*- coding: utf-8 -*-
"""ThreatConnect Exchange App Feature Advanced Request Module"""
import json
from mimetypes import MimeTypes
import requests

from ..decorators import ReadArg


class AdvancedRequest:
    """App Feature Advanced Request Module"""

    def __init__(self, args, output_prefix, session, tcex, timeout=600):
        """Initialize class properties."""
        self.args = args
        self.output_prefix = output_prefix
        self.session = session
        self.tcex = tcex

        # properties
        self.allow_redirects = True
        self.data = None
        self.headers = {}
        self.max_mb = 500
        self.mt = MimeTypes()
        self.params = {}
        self.timeout = timeout or 600

    @ReadArg('tc_adv_req_body')
    def configure_body(self, tc_adv_req_body):
        """Configure Body"""
        self.data = tc_adv_req_body
        if self.data is not None:
            # INT-1386
            try:
                self.data = self.data.encode('utf-8')
            except AttributeError:
                pass  # Binary Data

        if self.args.tc_adv_req_urlencode_body:
            try:
                self.data = json.loads(self.data)
            except ValueError:
                self.tcex.log.error('Failed loading body as JSON data.')

    @ReadArg('tc_adv_req_headers', array=True)
    def configure_headers(self, tc_adv_req_headers):
        """Configure Headers"""
        for header_data in tc_adv_req_headers:
            self.headers[str(header_data.get('key'))] = header_data.get('value')

    @ReadArg('tc_adv_req_params', array=True)
    def configure_params(self, tc_adv_req_params):
        """Configure Params"""
        for param_data in tc_adv_req_params:
            param = str(param_data.get('key'))
            values = param_data.get('value')
            if not isinstance(values, list):
                values = [values]
            for value in values:
                if not value and self.args.tc_adv_req_exclude_null_params:
                    self.tcex.log.warning(
                        'Query parameter {} has a null/empty value and will not be added to the '
                        'request.'.format(param)
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
    def request(self, tc_adv_req_http_method, tc_adv_req_path):
        """Make HTTP request."""
        # configure body
        self.configure_body(**{})

        # configure headers
        self.configure_headers(**{})

        # configure params
        self.configure_params(**{})

        # make http request
        try:
            response = self.session.request(
                allow_redirects=self.allow_redirects,
                data=self.data,
                headers=self.headers,
                method=tc_adv_req_http_method,
                params=self.params,
                timeout=self.timeout,
                url=tc_adv_req_path,
            )
        except requests.exceptions.RequestException as e:
            err = 'Exception during request ({}).'.format(e)
            self.tcex.exit(1, err)

        # get response size
        response_bytes = len(response.content)
        response_mb = response_bytes / 1000000
        self.tcex.log.info('Response MB: {}'.format(response_mb))
        if response_mb > self.max_mb:
            self.tcex.exit(1, 'Download was larger than maximum supported 500 MB.')

        # fail if fail_on_error is selected and not ok
        if self.args.tc_adv_req_fail_on_error and not response.ok:
            self.tcex.exit(1, 'Failed for status ({})'.format(response.status_code))

        # write outputs
        self.write_output(response)

    def write_output(self, response):
        """Write the Playbook output variables."""
        self.tcex.playbook.create_output(
            f'{self.output_prefix}.request.content', response.text, 'String'
        )
        self.tcex.playbook.create_output(
            f'{self.output_prefix}.request.content.binary', response.content, 'Binary'
        )
        self.tcex.playbook.create_output(
            f'{self.output_prefix}.request.headers', json.dumps(dict(response.headers)), 'String'
        )
        self.tcex.playbook.create_output(
            f'{self.output_prefix}.request.ok', str(response.ok).lower()
        )
        self.tcex.playbook.create_output(f'{self.output_prefix}.request.reason', response.reason)
        self.tcex.playbook.create_output(
            f'{self.output_prefix}.request.status_code', response.status_code
        )
        self.tcex.playbook.create_output(f'{self.output_prefix}.request.url', response.request.url)
