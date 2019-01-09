.. include:: <isonum.txt>
.. _proxies:

=======
Proxies
=======
The ThreatConnect |copy| TcEx App Framework provides the :py:const:`~tcex.tcex.TcEx.proxies` property to automatically create a dictionary with the properly formatted proxy settings used by the Python Requests module.

.. Note:: When using the :py:meth:`~tcex.tcex_resources` module or :py:const:`~tcex.tcex.TcEx.session` property the proxies are automatically configured.

.. Hint:: The :py:const:`~tcex.tcex.TcEx.proxies` property can be helpful when using the :py:mod:`~tcex.tcex_request.TcExRequest` module.

Example Request using Proxy
---------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2,3

    r = tcex.request
    if args.tc_proxy_external:
        r.proxies = tcex.proxies
    r.url = 'https://remote_api.example'
    r.add_payload('api_key', 'abc123')
    response = r.send()
