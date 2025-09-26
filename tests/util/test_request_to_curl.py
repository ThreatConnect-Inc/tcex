"""TestRequestToCurl for HTTP request to cURL conversion functionality.

Test suite for the RequestsToCurl utility class that converts HTTP requests to
equivalent cURL commands with various options like masking, proxies, and verification.

Classes:
    TestRequestToCurl: Test suite for request to cURL conversion

TcEx Module Tested: tcex.util.requests_to_curl
"""


import re
from base64 import b64decode


import pytest
import requests


from tcex.util.requests_to_curl import RequestsToCurl


class TestRequestToCurl:
    """TestRequestToCurl for HTTP request to cURL conversion functionality.

    Test suite for the RequestsToCurl utility class that converts HTTP requests to
    equivalent cURL commands with various options like masking, proxies, and
    verification.
    """

    requests_to_curl = RequestsToCurl()

    def test_curl_get(self):
        """Test basic GET request to cURL conversion.

        Test case for converting a simple GET request to its equivalent cURL
        command with default headers and verification.
        """
        r = requests.get('https://www.google.com', timeout=60)
        r_curl = self.requests_to_curl.convert(r.request)
        r_curl_expected = re.compile(
            r"curl -X GET -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' "
            "-H 'Connection: keep-alive' -H 'User-Agent: "
            r"python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' https://www\.google\.com/"
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_get_insecure(self):
        """Test GET request to cURL conversion with insecure flag.

        Test case for converting a GET request to cURL command with SSL
        verification disabled (--insecure flag).
        """
        r = requests.get('https://www.google.com', timeout=60)
        r_curl = self.requests_to_curl.convert(r.request, verify=False)
        r_curl_expected = re.compile(
            r"curl -X GET -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' "
            r"-H 'Connection: keep-alive' -H 'User-Agent: "
            r"python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' --insecure "
            r'https://www\.google\.com/'
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_get_mask(self):
        """Test GET request to cURL conversion with header masking.

        Test case for converting a GET request to cURL command with sensitive
        header information masked using pattern matching.
        """
        headers = {
            'authorization': 'sensitive information that should not be readable',
            'pytest': 'mask',
        }
        r = requests.get('https://www.google.com', headers=headers, timeout=60)
        r_curl = self.requests_to_curl.convert(
            r.request, mask_headers=True, mask_patterns=['pytest'], verify=False
        )
        r_curl_expected = re.compile(
            r"curl -X GET -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' "
            r"-H 'Connection: keep-alive' -H 'User-Agent: "
            r"python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' -H 'authorization: s\*\*\*\*e' "
            r"-H 'pytest: m\*\*\*\*k' --insecure https://www\.google\.com/"
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_get_proxies(self):
        """Test GET request to cURL conversion with proxy support.

        Test case for converting a GET request to cURL command with proxy
        configuration and header masking.
        """
        headers = {'authorization': 'sensitive information that should not be readable'}
        r = requests.get('https://www.google.com', headers=headers, timeout=60)
        r_curl = self.requests_to_curl.convert(
            r.request, proxies={'https': 'https://www.google.com:3128'}, verify=False
        )
        r_curl_expected = re.compile(
            r"curl -X GET -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' "
            r"-H 'Connection: keep-alive' -H 'User-Agent: "
            r"python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' -H 'authorization: s\*\*\*\*e' "
            r'--proxy www\.google\.com:3128 --insecure https://www\.google\.com/'
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_get_proxies_with_auth(self):
        """Test GET request to cURL conversion with authenticated proxy.

        Test case for converting a GET request to cURL command with proxy
        authentication and header masking.
        """
        headers = {'authorization': 'sensitive information that should not be readable'}
        r = requests.get('https://www.google.com', headers=headers, timeout=60)
        r_curl = self.requests_to_curl.convert(
            r.request, proxies={'https': 'https://user:pass@www.google.com'}, verify=False
        )
        r_curl_expected = re.compile(
            r"curl -X GET -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' "
            r"-H 'Connection: keep-alive' -H 'User-Agent: "
            r"python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' -H 'authorization: s\*\*\*\*e' "
            r'--proxy www\.google\.com --proxy-user user:xxxxx --insecure '
            r'https://www\.google\.com/'
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_post(self):
        """Test POST request to cURL conversion.

        Test case for converting a POST request with data to its equivalent
        cURL command.
        """
        r = requests.post('https://www.google.com', data='test', timeout=60)
        r_curl = self.requests_to_curl.convert(r.request)
        r_curl_expected = re.compile(
            r"curl -X POST -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' "
            r"-H 'Connection: keep-alive' -H 'Content-Length: 4' -H 'User-Agent: "
            r"python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' -d \"test\" "
            r'https://www\.google\.com/'
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_mask_body(self):
        """Test POST request to cURL conversion with body masking.

        Test case for converting a POST request to cURL command with request
        body content masked for security.
        """
        r = requests.post('https://www.google.com', data='test', timeout=60)
        r_curl = self.requests_to_curl.convert(r.request, mask_body=True)
        r_curl_expected = re.compile(
            r"curl -X POST -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' "
            r"-H 'Connection: keep-alive' -H 'Content-Length: 4' -H 'User-Agent: "
            "python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' -d \"t\\*\\*\\*\\*t\" "
            r'https://www\.google\.com/'
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_post_bytes(self):
        """Test POST request to cURL conversion with bytes data.

        Test case for converting a POST request with bytes data to cURL command
        using --data-binary with temporary file.
        """
        r = requests.post('https://www.google.com', data=b'test', timeout=60)
        r_curl = self.requests_to_curl.convert(r.request)
        r_curl_expected = re.compile(
            r"curl -X POST -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' "
            r"-H 'Connection: keep-alive' -H 'Content-Length: 4' -H 'User-Agent: "
            r"python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' --data-binary @/tmp/body-file "
            r'https://www\.google\.com/'
        )
        assert r_curl_expected.match(r_curl)

    def test_curl_post_bytes_binary(self):
        """Test POST request to cURL conversion with binary data.

        Test case for converting a POST request with binary data to cURL command
        using --data-binary with base64 encoded content.
        """
        data = b64decode(
            'UEsDBAoAAAAAACSE+FBT/FFnAgAAAAIAAAAEABwAYmxhaFVUCQADk1MbX5RTG191eAsAAQT2AQAABBQAAAAxC'
            'lBLAQIeAwoAAAAAACSE+FBT/FFnAgAAAAIAAAAEABgAAAAAAAEAAAC0gQAAAABibGFoVVQFAAOTUxtfdXgLAA'
            'EE9gEAAAQUAAAAUEsFBgAAAAABAAEASgAAAEAAAAAAAA=='
        )
        r = requests.post('https://www.google.com', data=data, timeout=60)
        r_curl = self.requests_to_curl.convert(r.request)
        filename_match = re.search(r'(@\/tmp\/[a-z0-9].+)\s(?:http)', r_curl)
        if filename_match is None:
            pytest.fail('Could not find filename in curl command')
        filename = filename_match[1]
        r_curl_expected = re.compile(
            r"curl -X POST -H 'Accept: \*/\*' -H 'Accept-Encoding: deflate' "
            r"-H 'Connection: keep-alive' -H 'Content-Length: 160' -H 'User-Agent: "
            r"python-requests/[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,3}' "
            rf'--data-binary {filename} https://www\.google\.com/'
        )
        assert r_curl_expected.match(r_curl) is not None
