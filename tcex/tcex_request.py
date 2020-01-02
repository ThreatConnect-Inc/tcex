# -*- coding: utf-8 -*-
""" TcEx Framework Request Module """
import json
from base64 import b64encode

from requests import Session, adapters, packages
from requests.packages.urllib3.util.retry import Retry  # pylint: disable=E0401

packages.urllib3.disable_warnings()  # pylint: disable=E1101


def session_retry(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
    """Add retry to Requests Session

    https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#urllib3.util.retry.Retry
    """
    session = session or Session()
    retries = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    # mount all https requests
    session.mount('https://', adapters.HTTPAdapter(max_retries=retries))
    return session


class TcExRequest:
    """Wrapper on Python Requests Module with API logging."""

    def __init__(self, tcex, session=None):
        """Initialize the Class properties."""
        self.tcex = tcex

        self._basic_auth = None
        self._body = None
        self._content_type = None
        self._headers = {}
        self._http_method = 'GET'
        self._json = None
        self._payload = {}
        self._url = None
        self._files = None
        self._timeout = 300

        # session
        self.session = session_retry()
        if session is not None:
            self.session = session
        self.session.headers.update({'User-Agent': 'TcEx'})

    #
    # Body
    #

    @property
    def body(self):
        """Return the POST/PUT body content for this request."""
        return self._body

    @body.setter
    def body(self, data):
        """Set the POST/PUT body content for this request."""
        if data is not None:
            self._body = data
            self.add_header('Content-Length', str(len(self._body)))

    @property
    def json(self):
        """Return the POST/PUT body content in JSON format for this request."""
        return self._body

    @json.setter
    def json(self, data):
        """Set the POST/PUT body content in JSON format for this request."""
        if data is not None:
            self._body = json.dumps(data)
            self.add_header('Content-Type', 'application/json')

    #
    # HTTP Headers
    #

    @property
    def headers(self):
        """Return the header values for this request."""
        return self._headers

    def reset_headers(self):
        """Reset header dictionary for this request."""
        self._headers = {}

    def add_header(self, key, val):
        """Add a key value pair to header for this request.

        Args:
            key (str): The header key
            val (str): The header value
        """
        self._headers[key] = str(val)

    @property
    def authorization(self):
        """The "Authorization" header value for this request."""
        return self._headers.get('Authorization')

    @authorization.setter
    def authorization(self, data):
        """The "Authorization" header value for this request."""
        self.add_header('Authorization', data)

    @property
    def basic_auth(self):
        """The basic auth settings for this request."""
        return self._basic_auth

    @basic_auth.setter
    def basic_auth(self, data):
        """The basic auth settings for this request."""
        self._basic_auth = data

    @property
    def content_type(self):
        """The Content-Type header value for this request."""
        return self._headers.get('Content-Type')

    @content_type.setter
    def content_type(self, data):
        """The Content-Type header value for this request."""
        self._content_type = str(data)
        self.add_header('Content-Type', str(data))

    def set_basic_auth(self, username, password):
        """Manually set basic auth in the header when normal method does not work."""
        credentials = str(b64encode(f'{username}:{password}'.encode('utf-8')), 'utf-8')
        self.authorization = f'Basic {credentials}'

    @property
    def user_agent(self):
        """The the User-Agent header value for this request."""
        return self._headers.get('User-agent')

    @user_agent.setter
    def user_agent(self, data):
        """The the User-Agent header value for this request."""
        self.add_header('User-agent', data)

    #
    # HTTP Payload
    #

    @property
    def payload(self):
        """The payload values for this request."""
        return self._payload

    def reset_payload(self):
        """Reset payload dictionary"""
        self._payload = {}

    def add_payload(self, key, val, append=False):
        """Add a key value pair to payload for this request.

        Args:
            key (str): The payload key.
            val (str): The payload value.
            append (bool, default:False): Indicate whether the value should be appended or
                overwritten.
        """
        if append:
            self._payload.setdefault(key, []).append(val)
        else:
            self._payload[key] = val

    #
    # HTTP Method
    #

    @property
    def http_method(self):
        """The HTTP method for this request."""
        return self._http_method

    @http_method.setter
    def http_method(self, data):
        """The HTTP method for this request."""
        data = data.upper()
        if data in ['DELETE', 'GET', 'POST', 'PUT']:
            self._http_method = data

            # set content type for commit methods (best guess)
            if self._headers.get('Content-Type') is None and data in ['POST', 'PUT']:
                self.add_header('Content-Type', 'application/json')
        else:
            raise AttributeError(f'Request Object Error: {data} is not a valid HTTP method.')

    #
    # Set Properties
    #

    @property
    def proxies(self):
        """Return the proxy settings for the session."""
        return self.session.proxies

    @proxies.setter
    def proxies(self, proxy_settings):
        """Set the proxy settings for the session."""
        self.session.proxies = proxy_settings

    @property
    def timeout(self):
        """The HTTP timeout value for this request."""
        return self._timeout

    @timeout.setter
    def timeout(self, data):
        """The HTTP timeout value for this request."""
        if isinstance(data, int):
            self._timeout = data

    @property
    def verify_ssl(self):
        """Return the SSL validation setting for the session."""
        return self.session.verify

    @verify_ssl.setter
    def verify_ssl(self, verify):
        """Set the SSL validation setting for the session.

        Args:
            verify (str or bool): A boolean for enable/disable or the server PEM file.
        """
        self.session.verify = verify

    @property
    def files(self):
        """Files setting for this request"""
        return self._files

    @files.setter
    def files(self, data):
        """Files setting for this request"""
        if isinstance(data, dict):
            self._files = data

    #
    # Send
    #

    def send(self, stream=False):
        """Send the HTTP request via Python Requests modules.

        This method will send the request to the remote endpoint.  It will try to handle
        temporary communications issues by retrying the request automatically.

        Args:
            stream (bool): Boolean to enable stream download.

        Returns:
            Requests.Response: The Request response
        """
        #
        # api request (gracefully handle temporary communications issues with the API)
        #
        try:
            response = self.session.request(
                self._http_method,
                self._url,
                auth=self._basic_auth,
                data=self._body,
                files=self._files,
                headers=self._headers,
                params=self._payload,
                stream=stream,
                timeout=self._timeout,
            )
        except Exception as e:
            err = f'Failed making HTTP request ({e}).'
            raise RuntimeError(err)

        # self.tcex.log.info(f'URL ({self._http_method}): {response.url}')
        self.tcex.log.info(f'Status Code: {response.status_code}')
        return response

    #
    # URL
    #

    @property
    def url(self):
        """The URL for this request."""
        return self._url

    @url.setter
    def url(self, data):
        """The URL for this request."""
        self._url = data

    def __str__(self):
        """Print this request instance configuration."""
        printable_string = f"\n{'Request'!s:_^80}\n"

        #
        # http settings
        #
        printable_string += f"\n{'HTTP Settings'!s:40}\n"
        printable_string += f"  {'HTTP Method'!s:<29}{self.http_method!s:<50}\n"
        printable_string += f"  {'Request URL'!s:<29}{self.url!s:<50}\n"
        printable_string += f"  {'Content Type'!s:<29}{self.content_type!s:<50}\n"
        printable_string += f"  {'Body'!s:<29}{self.body!s:<50}\n"

        #
        # headers
        #
        if self.headers:
            printable_string += f"\n{'Headers'!s:40}\n"
            for k, v in self.headers.items():
                printable_string += f'  {k!s:<29}{v!s:<50}\n'

        #
        # payload
        #
        if self.payload:
            printable_string += f"\n{'Payload'!s:40}\n"
            for k, v in self.payload.items():
                printable_string += f'  {k!s:<29}{v!s:<50}\n'

        return printable_string
