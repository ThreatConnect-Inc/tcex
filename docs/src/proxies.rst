.. _proxies:

========
Proxies
========

The :py:class:`~tcex.tcex.TcEx` Class provides the :py:const:`~tcex.tcex.TcEx.proxies` property to automatically create a dictionary with the properly formatted proxy settings used by the Python Requests module.

The :py:const:`~tcex.tcex.TcEx.proxies` property is helpful when using the :py:mod:`~tcex.tcex_request.TcExRequest` module.

Example Request using Proxy
----------------------------
::

    r = tcex.request
    if args.tc_proxy_external:
        r.proxies = tcex.proxies
    r.url = 'https://remote_api.example'
    r.add_payload('api_key', 'abc123')
    response = r.send()