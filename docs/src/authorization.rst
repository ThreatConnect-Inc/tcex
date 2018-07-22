.. include:: <isonum.txt>
.. _authorization:

============================
Authorization (Token / HMAC)
============================
In general when communication with the ThreatConnect |trade| API using the TcEx Framework the App developer does not need to handle authorization.  If using any of the Resource Classes in :py:mod:`~tcex.tcex_resources` the authorization headers are automatically added.  This allows the App to run from within the ThreatConnect Platform or the Integration Server without having to change any code.

The :py:meth:`~tcex.tcex` module also has the :py:mod:`~tcex.tcex.TcEx.session` property which is a Python Requests Session with ThreatConnect Authorization added.  API call to the ThreatConnect API can be made with the native Requests interface with authorization and token renewal built-in.

.. Note:: The latest version of the ThreatConnect Platform supports both Token based and HMAC authorization.  The MEO server supports HMAC or Token based authorization depending on the version.

Token Refresh
--------------
Token based authorization requires that the Token be renewed upon token expiration.  The ThreatConnect Platform passes the ``tc_token`` and ``tc_token_expires`` arguments to the App.  The TcEx Framework automatically handles the Token refresh when using the :py:meth:`~tcex.tcex.TcEx.authorization` or :py:mod:`~tcex.tcex.TcEx.session` features.

HMAC Authorization
------------------
Generation of the Authorization headers when using HMAC will utilize the ``api_access_id`` and ``api_secret_key`` arguments.  These arguments are not automatically sent by the ThreatConnect Platform and are required to be added to the :ref:install_json file.  In the ThreatConnect UI these inputs will be automatically hidden in favor of Token based authorization.  However, on the certain versions of the MEO server these arguments could be required.

Example install.json param section::

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

For proper HMAC authorization the HTTP Method and URI with query string arguments are required when building the authorization string.  Therefore the authorization string has to be built after the URI and query parameters are build and before the request is sent.