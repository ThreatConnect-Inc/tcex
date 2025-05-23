"""TcEx Framework Module"""

# standard library
import re
from base64 import b64decode

# third-party
import requests

# first-party
from tcex.util.requests_to_curl import RequestsToCurl


class TestRequestToCurl:
    """Test Suite"""

    requests_to_curl = RequestsToCurl()

    def test_curl_get(self):
        """Test Case"""
        r = requests.get('https://www.google.com', timeout=60)
        r_curl = self.requests_to_curl.convert(r.request)
        r_curl_expected = re.compile(
            r'''curl -X GET -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' '''
            '''-H 'Connection: keep-alive' -H 'User-Agent: '''
            r'''python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' https://www\.google\.com/'''
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_get_insecure(self):
        """Test Case"""
        r = requests.get('https://www.google.com', timeout=60)
        r_curl = self.requests_to_curl.convert(r.request, verify=False)
        r_curl_expected = re.compile(
            r'''curl -X GET -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' '''
            r'''-H 'Connection: keep-alive' -H 'User-Agent: '''
            r'''python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' --insecure '''
            r'''https://www\.google\.com/'''
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_get_mask(self):
        """Test Case"""
        headers = {
            'authorization': 'sensitive information that should not be readable',
            'pytest': 'mask',
        }
        r = requests.get('https://www.google.com', headers=headers, timeout=60)
        r_curl = self.requests_to_curl.convert(
            r.request, mask_headers=True, mask_patterns=['pytest'], verify=False
        )
        r_curl_expected = re.compile(
            r'''curl -X GET -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' '''
            r'''-H 'Connection: keep-alive' -H 'User-Agent: '''
            r'''python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' -H 'authorization: s\*\*\*\*e' '''
            r'''-H 'pytest: m\*\*\*\*k' --insecure https://www\.google\.com/'''
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_get_proxies(self):
        """Test Case"""
        headers = {'authorization': 'sensitive information that should not be readable'}
        r = requests.get('https://www.google.com', headers=headers, timeout=60)
        r_curl = self.requests_to_curl.convert(
            r.request, proxies={'https': 'https://www.google.com:3128'}, verify=False
        )
        r_curl_expected = re.compile(
            r'''curl -X GET -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' '''
            r'''-H 'Connection: keep-alive' -H 'User-Agent: '''
            r'''python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' -H 'authorization: s\*\*\*\*e' '''
            r'''--proxy www\.google\.com:3128 --insecure https://www\.google\.com/'''
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_get_proxies_with_auth(self):
        """Test Case"""
        headers = {'authorization': 'sensitive information that should not be readable'}
        r = requests.get('https://www.google.com', headers=headers, timeout=60)
        r_curl = self.requests_to_curl.convert(
            r.request, proxies={'https': 'https://user:pass@www.google.com'}, verify=False
        )
        r_curl_expected = re.compile(
            r'''curl -X GET -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' '''
            r'''-H 'Connection: keep-alive' -H 'User-Agent: '''
            r'''python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' -H 'authorization: s\*\*\*\*e' '''
            r'''--proxy www\.google\.com --proxy-user user:xxxxx --insecure '''
            r'''https://www\.google\.com/'''
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_post(self):
        """Test Case"""
        r = requests.post('https://www.google.com', data='test', timeout=60)
        r_curl = self.requests_to_curl.convert(r.request)
        r_curl_expected = re.compile(
            r'''curl -X POST -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' '''
            r'''-H 'Connection: keep-alive' -H 'Content-Length: 4' -H 'User-Agent: '''
            r'''python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' -d \"test\" '''
            r'''https://www\.google\.com/'''
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_mask_body(self):
        """Test Case"""
        r = requests.post('https://www.google.com', data='test', timeout=60)
        r_curl = self.requests_to_curl.convert(r.request, mask_body=True)
        r_curl_expected = re.compile(
            r'''curl -X POST -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' '''
            r'''-H 'Connection: keep-alive' -H 'Content-Length: 4' -H 'User-Agent: '''
            '''python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' -d \"t\\*\\*\\*\\*t\" '''
            r'''https://www\.google\.com/'''
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_post_bytes(self):
        """Test Case"""
        r = requests.post('https://www.google.com', data=b'test', timeout=60)
        r_curl = self.requests_to_curl.convert(r.request)
        r_curl_expected = re.compile(
            r'''curl -X POST -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' '''
            r'''-H 'Connection: keep-alive' -H 'Content-Length: 4' -H 'User-Agent: '''
            r'''python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' --data-binary @/tmp/body-file '''
            r'''https://www\.google\.com/'''
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_post_bytes_binary(self):
        """Test Case"""
        data = b64decode(
            'UEsDBAoAAAAAACSE+FBT/FFnAgAAAAIAAAAEABwAYmxhaFVUCQADk1MbX5RTG191eAsAAQT2AQAABBQAAAAxC'
            'lBLAQIeAwoAAAAAACSE+FBT/FFnAgAAAAIAAAAEABgAAAAAAAEAAAC0gQAAAABibGFoVVQFAAOTUxtfdXgLAA'
            'EE9gEAAAQUAAAAUEsFBgAAAAABAAEASgAAAEAAAAAAAA=='
        )
        r = requests.post('https://www.google.com', data=data, timeout=60)
        r_curl = self.requests_to_curl.convert(r.request)
        filename = re.search(r'(@\/tmp\/[a-z0-9].+)\s(?:http)', r_curl)
        if filename is None:
            assert False, 'Could not find filename in curl command'
        filename = filename[1]
        r_curl_expected = re.compile(
            r'''curl -X POST -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' '''
            r'''-H 'Connection: keep-alive' -H 'Content-Length: 160' -H 'User-Agent: '''
            r'''python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' '''
            rf'''--data-binary {filename} https://www\.google\.com/'''
        )
        assert r_curl_expected.match(r_curl) is not None
