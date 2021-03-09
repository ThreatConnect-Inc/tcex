"""A httpx request to curl Module"""
# standard library
import re
from typing import List, Optional, Union
from urllib.parse import urlsplit

# third-party
import httpx


class RequestToCurl:
    """Convert httpx request object to curl command."""

    def __init__(
        self,
        mask_headers: Optional[bool] = True,
        mask_patterns: List[str] = None,
        **kwargs: Union[bool, dict],
    ) -> None:
        """Initialize class properties."""
        self.mask_headers = mask_headers
        self.mask_patterns = mask_patterns

        # kwargs
        self.body_limit = kwargs.get('body_limit', 100)
        self.proxies = kwargs.get('proxies', {})
        self.mask_body = kwargs.get('mask_body', False)
        self.verify = kwargs.get('verify', True)
        self.write_file = kwargs.get('write_file', False)

    @staticmethod
    def _printable_cred(
        cred: str,
        visible: Optional[int] = 1,
        mask_char: Optional[str] = '*',
        mask_char_count: Optional[int] = 4,
    ) -> str:
        """Return a printable (masked) version of the provided credential.

        Args:
            cred: The cred to print.
            visible: The number of characters at the beginning and ending of the cred to not mask.
            mask_char: The character to use in the mask.
            mask_char_count: How many mask character to insert (obscure cred length).

        Returns:
            str: The reformatted token.
        """
        mask_char = mask_char or '*'
        if cred is not None and len(cred) >= visible * 2:
            cred = f'{cred[:visible]}{mask_char * mask_char_count}{cred[-visible:]}'
        return cred

    @staticmethod
    def _truncate_string(
        t_string: str,
        length: int,
        append_chars: Optional[str] = '',
        spaces: Optional[bool] = False,
    ) -> str:
        """Truncate a string to a given length.

        Args:
            t_string: The input string to truncate.
            length: The length of the truncated string.
            append_chars: Any character that should be appended to the
                string. Typically used for ellipsis (e.g. ...).
            spaces: If True truncation will be done at the
                nearest space before the truncation length to avoid chopping words.

        Returns:
            str: The truncated string.
        """
        if t_string is None:
            t_string = ''

        if length is None:
            length = len(t_string)

        if len(t_string) <= length:
            return t_string

        # set sane default for append_chars
        append_chars = str(append_chars or '')

        # ensure append_chars is not longer than length
        if len(append_chars) > length:  # pragma: no cover
            raise RuntimeError('Append chars cannot exceed the truncation length.')

        output = t_string[0 : length - len(append_chars)]  # noqa: E203
        if spaces is True:
            if not output.endswith(' '):
                # split output on spaces and drop last item to terminate string on word
                output = ' '.join(output.split(' ')[:-1])

        return f'{output.rstrip()}{append_chars}'

    def _process_body(self, body):
        """Process requests body."""
        try:
            if isinstance(body, bytes):
                body = body.decode('utf-8')

            if self.mask_body:
                # mask_body
                body = self._printable_cred(body)
            else:
                # truncate body
                body = self._truncate_string(
                    t_string=body, length=self.body_limit, append_chars='...'
                )
            body_data = f'-d "{body}"'
        except Exception:
            # TODO: this needs some work
            # set static filename so that when running a large job
            # App thousands of files do no get created.
            body_data = '--data-binary @/tmp/body-file'
            # if self.write_file is True:
            #     temp_file: str = write_temp_binary_file(content=body, filename='curl-body')
            #     body_data = f'--data-binary @{temp_file}'
        return body_data

    def _process_headers(self, headers):
        """Process requests headers."""
        h = []
        for k, v in sorted(list(dict(headers).items())):
            if self.mask_headers is True:
                patterns = [
                    'authorization',
                    'cookie',
                    'password',
                    'secret',
                    'session',
                    'username',
                    'token',
                ]
                if isinstance(self.mask_patterns, list):
                    # add user defined mask patterns
                    patterns.extend(self.mask_patterns)

                for p in patterns:
                    if re.match(rf'.*{p}.*', k, re.IGNORECASE):
                        v: str = self._printable_cred(v)

                # using gzip in Accept-Encoding with CURL on the CLI produces
                # the warning "Binary output can mess up your terminal."
                if k.lower() == 'accept-encoding':
                    encodings = [e.strip() for e in v.split(',')]
                    for encoding in list(encodings):
                        if encoding in ['gzip']:
                            encodings.remove(encoding)
                    v: str = ', '.join(encodings)
            h.append(f"-H '{k}: {v}'")
        return h

    @staticmethod
    def _process_proxies(proxies):
        """Process requests proxies."""
        p = []
        if proxies is not None and proxies.get('https'):
            # parse formatted string {'https': 'bob:pass@https://localhost:4242'}
            proxy_url: Optional[str] = proxies.get('https')
            proxy_data = urlsplit(proxy_url)

            # auth
            if proxy_data.username:
                p.extend(['--proxy-user', f'{proxy_data.username}:xxxxx'])

            # server
            proxy_server = proxy_data.hostname
            if proxy_data.port:
                proxy_server = f'{proxy_data.hostname}:{proxy_data.port}'
            p.extend(['--proxy', proxy_server])
        return p

    @staticmethod
    def _process_verify(verify):
        """Process requests verify."""
        if verify is False:
            # add insecure flag to curl command
            return '--insecure'
        return ''

    def to_curl(self, request: httpx.Request) -> str:
        """Return converted PreparedRequest to a curl command."""
        # APP-79 - adding the ability to log request as curl commands
        cmd = ['curl', '-X', request.method]

        # process headers
        cmd.extend(self._process_headers(request.headers))

        # process body
        # TODO: how do you get body from request object?
        # if False:
        #     cmd.append(self._process_body(request.read()))

        # process proxies
        cmd.extend(self._process_proxies(self.proxies))

        # process verify
        cmd.append(self._process_verify(self.verify))

        # add url to curl command
        cmd.append(str(request.url))

        return ' '.join(cmd)
