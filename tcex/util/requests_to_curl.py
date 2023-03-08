"""TcEx Utilities Request to Curl Module"""
# standard library
import re
from urllib.parse import urlsplit

# third-party
from pydantic import BaseModel, Field
from requests import PreparedRequest  # TYPE-CHECKING

# first-party
from tcex.util.util import Util


class CurlModel(BaseModel):
    """Model Definition"""

    body_limit: int = Field(100, description='The size limit for the body value.')
    mask_body: bool = Field(False, description='If True the body will be masked.')
    proxies: dict[str, str] | None = Field(
        None, description='A dict containing the proxy configuration.'
    )
    verify: bool | str = Field(
        True, description='If False the curl command will include --insecure flag.'
    )
    write_file: bool = Field(
        False, description='If True and the body is binary it will be written as a temp file.'
    )


class RequestsToCurl:
    """TcEx Utilities Request to Curl Class"""

    def __init__(self):
        """Initialize the Class properties."""
        self.util = Util()

    def _process_body(self, body: bytes | str | None, curl_model: CurlModel) -> list[str]:
        """Process body and return a list of curl commands."""
        _body = []
        if body is None:
            return _body

        # add body to the curl command
        if isinstance(body, str):
            if curl_model.mask_body is True:
                body = self.util.printable_cred(body)  # mask the body
            else:
                body = self.util.truncate_string(
                    string=body, length=curl_model.body_limit, append_chars='...'
                )
            _body.append(f'-d "{body}"')
        elif isinstance(body, bytes):
            _body.append('--data-binary @/tmp/body-file')
        return _body

    def _process_headers(
        self, headers: dict, mask_headers: bool, mask_patterns: list[str] | None
    ) -> list[str]:
        """Process headers and return a list of curl commands."""
        _headers = []
        for k, v in sorted(list(dict(headers).items())):
            if mask_headers is True:
                patterns = [
                    'authorization',
                    'cookie',
                    'password',
                    'secret',
                    'session',
                    'token',
                    'username',
                ]
                if isinstance(mask_patterns, list):
                    # add user defined mask patterns
                    patterns.extend(mask_patterns)

                for p in patterns:
                    if re.match(rf'.*{p}.*', k, re.IGNORECASE):
                        v: str = self.util.printable_cred(v)

                # using gzip in Accept-Encoding with CURL on the CLI produces
                # the warning "Binary output can mess up your terminal."
                if k.lower() == 'accept-encoding':
                    encodings = [e.strip() for e in v.split(',')]
                    for encoding in list(encodings):
                        if encoding in ['gzip']:
                            encodings.remove(encoding)
                    v: str = ', '.join(encodings)

            _headers.append(f"-H '{k}: {v}'")
        return _headers

    def _process_proxies(self, proxies: dict[str, str] | None) -> list[str]:
        """Process proxies and return a list of curl commands."""
        _proxies = []
        if proxies is None or proxies.get('https') is None:
            return _proxies

        # parse formatted string {'https': 'bob:pass@https://localhost:4242'}
        proxy_url = proxies.get('https')
        proxy_data = urlsplit(proxy_url)

        # server
        proxy_server = proxy_data.hostname
        # do not process if server is None or bytes
        if isinstance(proxy_server, str):
            if proxy_data.port:
                proxy_server = f'{proxy_data.hostname}:{proxy_data.port}'
            _proxies.extend(['--proxy', proxy_server])

            # only append auth if server name is str
            if proxy_data.username:
                _proxies.extend(['--proxy-user', f'{proxy_data.username}:xxxxx'])

        return _proxies

    def convert(
        self,
        request: PreparedRequest,
        mask_headers: bool = True,
        mask_patterns: list[str] | None = None,
        **kwargs,
    ) -> str:
        """Return converted Prepared Request to a curl command.

        Args:
            request: The response.request object.
            mask_headers: If True then values for certain header key will be masked.
            mask_patterns: A list of patterns if found in headers the value will be masked.
        """
        # build curl model from kwargs
        curl_model = CurlModel(**kwargs)

        # APP-79 - adding the ability to log request as curl commands
        cmd = ['curl', '-X', request.method]

        # add headers to curl command
        cmd.extend(self._process_headers(dict(request.headers), mask_headers, mask_patterns))

        # add body to the curl command
        cmd.extend(self._process_body(request.body, curl_model))

        # add proxies to curl command
        cmd.extend(self._process_proxies(curl_model.proxies))

        if curl_model.verify is not True:
            # add insecure flag to curl command
            cmd.append('--insecure')

        # add url to curl command
        cmd.append(request.url)

        return ' '.join(cmd)
