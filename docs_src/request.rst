.. _requests:

=========
Requests
=========
The :py:class:`~tcex.tcex.TcEx` Class provides the :py:mod:`~tcex.tcex_request.TcExRequest` module to accessed using the ``tcex.request`` property.

Example Request
----------------
::

    r = tcex.request
    r.url = 'https://remote_api.example'
    r.add_header('Content-Type', 'application/json')
    r.add_payload('api_key', 'abc123')
    r.http_method = 'POST'
    r.body = '{"data": "xyz321"}'
    response = r.send()