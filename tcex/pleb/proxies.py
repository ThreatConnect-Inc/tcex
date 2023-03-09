"""Proxies"""
# standard library
from urllib.parse import quote

# first-party
from tcex.input.field_type.sensitive import Sensitive  # TYPE-CHECKING


def proxies(
    proxy_host: str | None,
    proxy_port: int | None,
    proxy_user: str | None,
    proxy_pass: Sensitive | str | None,
) -> dict:
    """Format the proxy configuration for Python Requests module.

    Generates a dictionary for use with the Python Requests module format
    when proxy is required for remote connections.

    **Example Response**
    ::

        {
            "http": "http://user:pass@10.10.1.10:3128/",
            "https": "http://user:pass@10.10.1.10:3128/"
        }
    """
    _proxies = {}
    if proxy_host is not None and proxy_port is not None:
        proxy_auth = ''
        if proxy_user is not None and proxy_pass is not None:
            proxy_user = quote(proxy_user, safe='~')
            if isinstance(proxy_pass, Sensitive):
                proxy_pass_ = quote(proxy_pass.value, safe='~')
            else:
                proxy_pass_ = quote(proxy_pass, safe='~')

            # proxy url with auth
            proxy_auth = f'{proxy_user}:{proxy_pass_}@'

        proxy_url = f'{proxy_auth}{proxy_host}:{proxy_port}'
        _proxies = {'http': f'http://{proxy_url}', 'https': f'http://{proxy_url}'}
    return _proxies
