# -*- coding: utf-8 -*-
"""Test the TcEx Utils Module."""
import re
from base64 import b64decode

import requests


# pylint: disable=no-self-use
class TestRequestToCurl:
    """Test the TcEx Utils Module."""

    def test_curl_get(self, tcex):
        """Test an IPv4 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        r = requests.get('https://www.threatconnect.com')
        r_curl = tcex.utils.requests_to_curl(r.request)
        assert r_curl == (
            '''curl -X GET -H 'Accept: */*' -H 'Accept-Encoding: deflate' '''
            '''-H 'Connection: keep-alive' -H 'User-Agent: python-requests/2.23.0' '''
            '''https://www.threatconnect.com/'''
        )

    def test_curl_get_insecure(self, tcex):
        """Test an IPv4 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        r = requests.get('https://www.threatconnect.com')
        r_curl = tcex.utils.requests_to_curl(r.request, verify=False)
        assert r_curl == (
            '''curl -X GET -H 'Accept: */*' -H 'Accept-Encoding: deflate' '''
            '''-H 'Connection: keep-alive' -H 'User-Agent: python-requests/2.23.0' '''
            '''--insecure https://www.threatconnect.com/'''
        )

    def test_curl_get_mask(self, tcex):
        """Test an IPv4 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        headers = {
            'authorization': 'sensitive information that should not be readable',
            'pytest': 'mask',
        }
        r = requests.get('https://www.threatconnect.com', headers=headers)
        r_curl = tcex.utils.requests_to_curl(
            r.request, mask_headers=True, mask_patterns=['pytest'], verify=False
        )
        assert r_curl == (
            '''curl -X GET -H 'Accept: */*' -H 'Accept-Encoding: deflate' '''
            '''-H 'Connection: keep-alive' -H 'User-Agent: python-requests/2.23.0' '''
            '''-H 'authorization: s****e' -H 'pytest: m****k' '''
            '''--insecure https://www.threatconnect.com/'''
        )

    def test_curl_get_proxies(self, tcex):
        """Test an IPv4 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        headers = {'authorization': 'sensitive information that should not be readable'}
        r = requests.get('https://www.threatconnect.com', headers=headers)
        r_curl = tcex.utils.requests_to_curl(
            r.request, proxies={'https': 'https://www.google.com'}, verify=False
        )
        assert r_curl == (
            '''curl -X GET -H 'Accept: */*' -H 'Accept-Encoding: deflate' '''
            '''-H 'Connection: keep-alive' -H 'User-Agent: python-requests/2.23.0' '''
            '''-H 'authorization: s****e' --proxy www.google.com '''
            '''--insecure https://www.threatconnect.com/'''
        )

    def test_curl_get_proxies_with_auth(self, tcex):
        """Test an IPv4 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        headers = {'authorization': 'sensitive information that should not be readable'}
        r = requests.get('https://www.threatconnect.com', headers=headers)
        r_curl = tcex.utils.requests_to_curl(
            r.request, proxies={'https': 'user:pass@https://www.google.com'}, verify=False
        )
        assert r_curl == (
            '''curl -X GET -H 'Accept: */*' -H 'Accept-Encoding: deflate' '''
            '''-H 'Connection: keep-alive' -H 'User-Agent: python-requests/2.23.0' '''
            '''-H 'authorization: s****e' --proxy-user user:xxxxx --proxy www.google.com '''
            '''--insecure https://www.threatconnect.com/'''
        )

    def test_curl_post(self, tcex):
        """Test an IPv4 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        r = requests.post('https://www.threatconnect.com', data='test')
        r_curl = tcex.utils.requests_to_curl(r.request)
        assert r_curl == (
            '''curl -X POST -H 'Accept: */*' -H 'Accept-Encoding: deflate' '''
            '''-H 'Connection: keep-alive' -H 'Content-Length: 4' -H 'User-Agent: '''
            '''python-requests/2.23.0' -d "test" https://www.threatconnect.com/'''
        )

    def test_curl_post_bytes(self, tcex):
        """Test an IPv4 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        r = requests.post('https://www.threatconnect.com', data=b'test')
        r_curl = tcex.utils.requests_to_curl(r.request)
        assert r_curl == (
            '''curl -X POST -H 'Accept: */*' -H 'Accept-Encoding: deflate' '''
            '''-H 'Connection: keep-alive' -H 'Content-Length: 4' -H 'User-Agent: '''
            '''python-requests/2.23.0' -d "test" https://www.threatconnect.com/'''
        )

    def test_curl_post_bytes_binary(self, tcex):
        """Test an IPv4 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        data = b64decode(
            'UEsDBAoAAAAAACSE+FBT/FFnAgAAAAIAAAAEABwAYmxhaFVUCQADk1MbX5RTG191eAsAAQT2AQAABBQAAAAxC'
            'lBLAQIeAwoAAAAAACSE+FBT/FFnAgAAAAIAAAAEABgAAAAAAAEAAAC0gQAAAABibGFoVVQFAAOTUxtfdXgLAA'
            'EE9gEAAAQUAAAAUEsFBgAAAAABAAEASgAAAEAAAAAAAA=='
        )
        r = requests.post('https://www.threatconnect.com', data=data)
        r_curl = tcex.utils.requests_to_curl(r.request)
        filename = re.search(r'(@log\/[a-z0-9].+)\s(?:http)', r_curl)[1]
        assert r_curl == (
            '''curl -X POST -H 'Accept: */*' -H 'Accept-Encoding: deflate' '''
            '''-H 'Connection: keep-alive' -H 'Content-Length: 160' -H 'User-Agent: '''
            f'''python-requests/2.23.0' --data-binary {filename} '''
            '''https://www.threatconnect.com/'''
        )
