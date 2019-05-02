.. include:: <isonum.txt>
.. _authorization:

============================
Authorization (Token/HMAC)
============================
In general, when communicating with the ThreatConnect API using the TcEx Framework, the App developer does not need to handle authorization.  If using any of the Resource Classes in :py:mod:`~tcex.tcex_resources`, the authorization headers are automatically added.  This allows the App to run from within the ThreatConnect platform or the Integration server without having to change any code.

The :py:meth:`~tcex.tcex` module also has the :py:mod:`~tcex.tcex.TcEx.session` property, which is a Python Requests Session (http://docs.python-requests.org/en/master/user/advanced/#session-objects) with ThreatConnect authorization added.  API calls to the ThreatConnect API can be made with the native Requests interface with authorization and token renewal built in.

.. Note:: The latest version of the ThreatConnect platform supports both token-based and HMAC authorization.  The ThreatConnect Environment server supports HMAC or token-based authorization, depending on the version.

Token Refresh
--------------
Token-ased authorization requires that the token be renewed upon expiration.  The ThreatConnect platform passes the ``tc_token`` and ``tc_token_expires`` arguments to the App.  The TcEx Framework automatically handles the token refresh when using :py:mod:`~tcex.tcex.TcEx.session`.

HMAC Authorization
------------------
HMAC authorization is typically only used for running Apps outside the ThreatConnect platform.  Generation of the authorization headers when using HMAC will utilize the ``api_access_id`` and ``api_secret_key`` arguments.  These arguments are not automatically sent by the ThreatConnect platform and are required to be added to the **:ref:install_json** file.  In the ThreatConnect UI, these inputs will  automatically be hidden in favor of token-based authorization.  However, on certain versions of the Environment server these arguments may be required. 

Example **install.json** param section::

    <...snipped>
    {
      "label": "ThreatConnect API Access ID",
      "name": "api_access_id",
      "required": true,
      "sequence": 1,
      "type": "String",
      "validValues": [
        "${USER:TEXT}",
        "${ORGANIZATION:TEXT}"
      ]
    }, {
      "encrypt": true,
      "label": "Local ThreatConnect API Secret Key",
      "name": "api_secret_key",
      "required": true,
      "sequence": 2,
      "type": "String",
      "validValues": [
        "${USER:KEYCHAIN}",
        "${ORGANIZATION:KEYCHAIN}"
        ]
    }
    <snipped...>

For proper HMAC authorization, the HTTP method and the Uniform Resource Identifier (URI) with query string arguments are required when building the authorization string.  Therefore, the authorization string has to be built after the URI and query parameters are built and before the request is sent.
