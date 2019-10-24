.. include:: <isonum.txt>
.. _module_requests:

.. important:: This module will be deprecated in a future release.  The ``tcex.session`` property can be used to make manual API calls to the ThreatConnect API.

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
