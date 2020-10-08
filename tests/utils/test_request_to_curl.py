"""Test the TcEx Utils Module."""
# standard library
import re
from base64 import b64decode

# third-party
import requests


# pylint: disable=no-self-use
class TestRequestToCurl:
    """Test the TcEx Utils Module."""

    def test_curl_get(self, tcex):
        """Test an IPv4 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        r = requests.get('https://www.google.com')
        r_curl = tcex.utils.requests_to_curl(r.request)
        r_curl_expected = re.compile(
            r'''curl -X GET -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' '''
            '''-H 'Connection: keep-alive' -H 'User-Agent: '''
            '''python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' https://www.google.com/'''
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_get_insecure(self, tcex):
        """Test an IPv4 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        r = requests.get('https://www.google.com')
        r_curl = tcex.utils.requests_to_curl(r.request, verify=False)
        r_curl_expected = re.compile(
            r'''curl -X GET -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' '''
            '''-H 'Connection: keep-alive' -H 'User-Agent: '''
            '''python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' --insecure '''
            '''https://www.google.com/'''
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_get_mask(self, tcex):
        """Test an IPv4 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        headers = {
            'authorization': 'sensitive information that should not be readable',
            'pytest': 'mask',
        }
        r = requests.get('https://www.google.com', headers=headers)
        r_curl = tcex.utils.requests_to_curl(
            r.request, mask_headers=True, mask_patterns=['pytest'], verify=False
        )
        r_curl_expected = re.compile(
            r'''curl -X GET -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' '''
            '''-H 'Connection: keep-alive' -H 'User-Agent: '''
            r'''python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' -H 'authorization: s\*\*\*\*e' '''
            r'''-H 'pytest: m\*\*\*\*k' --insecure https://www.google.com/'''
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_get_proxies(self, tcex):
        """Test an IPv4 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        headers = {'authorization': 'sensitive information that should not be readable'}
        r = requests.get('https://www.google.com', headers=headers)
        r_curl = tcex.utils.requests_to_curl(
            r.request, proxies={'https': 'https://www.google.com'}, verify=False
        )
        r_curl_expected = re.compile(
            r'''curl -X GET -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' '''
            '''-H 'Connection: keep-alive' -H 'User-Agent: '''
            r'''python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' -H 'authorization: s\*\*\*\*e' '''
            '''--proxy www.google.com --insecure https://www.google.com/'''
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_get_proxies_with_auth(self, tcex):
        """Test an IPv4 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        headers = {'authorization': 'sensitive information that should not be readable'}
        r = requests.get('https://www.google.com', headers=headers)
        r_curl = tcex.utils.requests_to_curl(
            r.request, proxies={'https': 'https://user:pass@www.google.com'}, verify=False
        )
        r_curl_expected = re.compile(
            r'''curl -X GET -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' '''
            '''-H 'Connection: keep-alive' -H 'User-Agent: '''
            r'''python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' -H 'authorization: s\*\*\*\*e' '''
            '''--proxy-user user:xxxxx --proxy www.google.com --insecure '''
            '''https://www.google.com/'''
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_post(self, tcex):
        """Test an IPv4 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        r = requests.post('https://www.google.com', data='test')
        r_curl = tcex.utils.requests_to_curl(r.request)
        r_curl_expected = re.compile(
            r'''curl -X POST -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' '''
            '''-H 'Connection: keep-alive' -H 'Content-Length: 4' -H 'User-Agent: '''
            '''python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' -d \"test\" '''
            '''https://www.google.com/'''
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_mask_body(self, tcex):
        """Test an IPv4 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        r = requests.post('https://www.google.com', data='test')
        r_curl = tcex.utils.requests_to_curl(r.request, mask_body=True)
        r_curl_expected = re.compile(
            r'''curl -X POST -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' '''
            '''-H 'Connection: keep-alive' -H 'Content-Length: 4' -H 'User-Agent: '''
            '''python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' -d \"t\\*\\*\\*\\*t\" '''
            '''https://www.google.com/'''
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_post_bytes(self, tcex):
        """Test an IPv4 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        r = requests.post('https://www.google.com', data=b'test')
        r_curl = tcex.utils.requests_to_curl(r.request)
        r_curl_expected = re.compile(
            r'''curl -X POST -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' '''
            '''-H 'Connection: keep-alive' -H 'Content-Length: 4' -H 'User-Agent: '''
            '''python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' -d \"test\" '''
            '''https://www.google.com/'''
        )
        assert r_curl_expected.match(r_curl)

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
        r = requests.post('https://www.google.com', data=data)
        r_curl = tcex.utils.requests_to_curl(r.request)
        filename = re.search(r'(@\/tmp\/[a-z0-9].+)\s(?:http)', r_curl)[1]
        r_curl_expected = re.compile(
            r'''curl -X POST -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' '''
            '''-H 'Connection: keep-alive' -H 'Content-Length: 160' -H 'User-Agent: '''
            f'''python-requests/[0-9]{{1,2}}.[0-9]{{1,2}}.[0-9]{{1,3}}' --data-binary {filename} '''
            '''https://www.google.com/'''
        )
        assert r_curl_expected.match(r_curl) is not None
