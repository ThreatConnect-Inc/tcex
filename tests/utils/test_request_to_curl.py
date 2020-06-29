# -*- coding: utf-8 -*-
"""Test the TcEx Utils Module."""
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
            '''curl -X GET -H 'Accept: */*' -H 'Accept-Encoding: gzip, deflate' '''
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
            '''curl -X GET -H 'Accept: */*' -H 'Accept-Encoding: gzip, deflate' '''
            '''-H 'Connection: keep-alive' -H 'User-Agent: python-requests/2.23.0' '''
            '''--insecure https://www.threatconnect.com/'''
        )

    def test_curl_get_mask(self, tcex):
        """Test an IPv4 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        headers = {'authorization': 'sensitive information that should not be readable'}
        r = requests.get('https://www.threatconnect.com', headers=headers)
        r_curl = tcex.utils.requests_to_curl(r.request, verify=False)
        assert r_curl == (
            '''curl -X GET -H 'Accept: */*' -H 'Accept-Encoding: gzip, deflate' '''
            '''-H 'Connection: keep-alive' -H 'User-Agent: python-requests/2.23.0' '''
            '''-H 'authorization: s****e' --insecure https://www.threatconnect.com/'''
        )

    def test_curl_post(self, tcex):
        """Test an IPv4 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        r = requests.post('https://www.threatconnect.com', data='test')
        r_curl = tcex.utils.requests_to_curl(r.request)
        assert r_curl == (
            '''curl -X POST -H 'Accept: */*' -H 'Accept-Encoding: gzip, deflate' '''
            '''-H 'Connection: keep-alive' -H 'Content-Length: 4' -H 'User-Agent: '''
            '''python-requests/2.23.0' -d test https://www.threatconnect.com/'''
        )

    def test_curl_post_bytes(self, tcex):
        """Test an IPv4 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        r = requests.post('https://www.threatconnect.com', data=b'test')
        r_curl = tcex.utils.requests_to_curl(r.request)
        assert r_curl == (
            '''curl -X POST -H 'Accept: */*' -H 'Accept-Encoding: gzip, deflate' '''
            '''-H 'Connection: keep-alive' -H 'Content-Length: 4' -H 'User-Agent: '''
            '''python-requests/2.23.0' -d test https://www.threatconnect.com/'''
        )
