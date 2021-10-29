"""Proxies"""
# standard library
from typing import TYPE_CHECKING, Optional
from urllib.parse import quote

if TYPE_CHECKING:
    # first-party
    from tcex.input.field_types.sensitive import Sensitive


def proxies(
    proxy_host: Optional[str],
    proxy_port: Optional[int],
    proxy_user: Optional[str],
    proxy_pass: Optional['Sensitive'],
) -> dict:
    """Format the proxy configuration for Python Requests module.

    Generates a dictionary for use with the Python Requests module format
    when proxy is required for remote connections.

    **Example Response**
    ::

        {"http": "http://user:pass@10.10.1.10:3128/"}
    """
    _proxies = {}
    if proxy_host is not None and proxy_port is not None:
        proxy_auth = ''
        if proxy_user is not None and proxy_pass is not None:
            proxy_user = quote(proxy_user, safe='~')
            proxy_pass = quote(proxy_pass.value, safe='~')

            # proxy url with auth
            proxy_auth = f'{proxy_user}:{proxy_pass}@'

        proxy_url = f'{proxy_auth}{proxy_host}:{proxy_port}'
        _proxies = {'http': f'http://{proxy_url}', 'https': f'http://{proxy_url}'}
    return _proxies
