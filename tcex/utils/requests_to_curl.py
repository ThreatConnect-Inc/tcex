"""TcEx Utilities Request to Curl Module"""
# standard library
import re
from typing import TYPE_CHECKING, List, Optional, Union
from urllib.parse import urlsplit

# first-party
from tcex.utils.utils import Utils

if TYPE_CHECKING:
    # third-party
    from requests import Request


class RequestsToCurl:
    """TcEx Utilities Request to Curl Class"""

    def __init__(self):
        """Initialize the Class properties."""
        self.utils = Utils()

    def convert(
        self,
        request: 'Request',
        mask_headers: Optional[bool] = True,
        mask_patterns: List[str] = None,
        **kwargs: Union[bool, dict],
    ) -> str:
        """Return converted Prepared Request to a curl command.

        Args:
            request: The response.request object.
            mask_headers: If True then values for certain header key will be masked.
            mask_patterns: A list of patterns if found in headers the value will be masked.
            body_limit: The size limit for the body value.
            mask_body: If True the body will be masked.
            proxies: A dict containing the proxy configuration.
            verify: If False the curl command will include --insecure flag.
            write_file: If True and the body is binary it will be written as a temp file.
        """
        body_limit: int = kwargs.get('body_limit', 100)
        proxies: dict = kwargs.get('proxies', {})
        verify: bool = kwargs.get('verify', True)
        # write_file: bool = kwargs.get('write_file', False)

        # APP-79 - adding the ability to log request as curl commands
        cmd = ['curl', '-X', request.method]

        # add headers to curl command
        for k, v in sorted(list(dict(request.headers).items())):
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
                        v: str = self.utils.printable_cred(v)

                # using gzip in Accept-Encoding with CURL on the CLI produces
                # the warning "Binary output can mess up your terminal."
                if k.lower() == 'accept-encoding':
                    encodings = [e.strip() for e in v.split(',')]
                    for encoding in list(encodings):
                        if encoding in ['gzip']:
                            encodings.remove(encoding)
                    v: str = ', '.join(encodings)

            cmd.append(f"-H '{k}: {v}'")

        if request.body:
            # add body to the curl command
            body = request.body
            try:
                if isinstance(body, bytes):
                    body = body.decode('utf-8')

                if kwargs.get('mask_body', False):
                    # mask_body
                    body = self.utils.printable_cred(body)
                else:
                    # truncate body
                    body = self.utils.truncate_string(
                        t_string=body, length=body_limit, append_chars='...'
                    )
                body_data = f'-d "{body}"'
            except Exception:
                # set static filename so that when running a large job App thousands of files do
                # no get created.
                body_data = '--data-binary @/tmp/body-file'
                # TODO: [super-low] - this is only useful for local testing.
                # if write_file is True:
                #     temp_file: str = self.utils.write_temp_binary_file(
                #         content=body, filename='curl-body'
                #     )
                #     body_data = f'--data-binary @{temp_file}'
            cmd.append(body_data)

        if proxies is not None and proxies.get('https'):
            # parse formatted string {'https': 'bob:pass@https://localhost:4242'}
            proxy_url: Optional[str] = proxies.get('https')
            proxy_data = urlsplit(proxy_url)

            # auth
            if proxy_data.username:
                cmd.extend(['--proxy-user', f'{proxy_data.username}:xxxxx'])

            # server
            proxy_server = proxy_data.hostname
            if proxy_data.port:
                proxy_server = f'{proxy_data.hostname}:{proxy_data.port}'
            cmd.extend(['--proxy', proxy_server])

        if not verify:
            # add insecure flag to curl command
            cmd.append('--insecure')

        # add url to curl command
        cmd.append(request.url)

        return ' '.join(cmd)
