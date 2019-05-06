.. include:: <isonum.txt>
.. _module_requests:

=================
Module: Requests
=================
The ThreatConnect TcEx Framework provides the :py:mod:`~tcex.tcex_request.TcExRequest` module accessed using the ``tcex.request`` property.  This module is a wrapper around the Python Requests module with API logging and custom authorization functionality.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    r = tcex.request
    r.url = 'https://remote_api.example'
    r.add_header('Content-Type', 'application/json')
    r.add_payload('api_key', 'abc123')
    r.body = '{"data": "xyz321"}'
    r.http_method = 'POST'
    response = r.send()

Request External
----------------
The TcEx Framework provides the :py:meth:`~tcex.tcex.TcEx.request_external` method that returns a TcExRequest instance with the proxy information automatically configured.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    r = tcex.request_external()
    r.url = 'https://remote_api.example'
    r.add_header('Content-Type', 'application/json')
    r.add_payload('api_key', 'abc123')
    r.basic_auth = (user, pass)
    r.body = '{"data": "xyz321"}'
    r.http_method = 'POST'
    response = r.send()

Request TC
----------
The TcEx Framework provides the :py:meth:`~tcex.tcex.TcEx.request_tc` method that returns a TcExRequest instance with the proxy and authorization information automatically configured.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    r = tcex.request_tc()
    r.url = 'https://api.threatconnect.com/v2/indicators/addresses'
    r.add_header('Content-Type', 'application/json')
    r.add_payload('owner', 'Acme Corp')
    r.body = '{"ip": "1.1.1.1"}'
    r.http_method = 'POST'
    response = r.send()
