.. include:: <isonum.txt>
.. _authorization:

============================
Authorization (Token / HMAC)
============================
In general when communication with the ThreatConnect |trade| API using the TcEx Framework the App developer does not need to handle authorization.  If using any of the Resource Classes in :py:mod:`~tcex.tcex_resources` the authorization headers are automatically added.  This allows the App to run from within the ThreatConnect Platform or the Integration Server without have to change any code.

.. Note:: The latest version of the ThreatConnect Platform supports both Token based and HMAC authorization.  The Integration Server only supports HMAC authorization.  Apps should be written to run on both platforms.

If **not** using one of the Resource Classes in :py:mod:`~tcex.tcex_resources` for communications with the ThreatConnect API the :py:meth:`~tcex.tcex.TcEx.authorization` method can still be used to return a Python dictionary containing the required header values for proper authorization via Token or HMAC. The :py:meth:`~tcex.tcex.TcEx.authorization` method expects a prepared request from the Python Requests module (http://docs.python-requests.org/en/master/user/advanced/#prepared-requests).

Token Refresh
--------------
Token based authorization required that the Token be renewed upon token expiration.  The ThreatConnect Platform passes the ``tc_token`` and ``tc_token_expires`` arguments to the App.  The TcEx Framework automatically handles the Token refresh when using the :py:meth:`~tcex.tcex.TcEx.authorization` method.

HMAC Authorization
------------------
Generation of the Authorization headers when using HMAC will utilize the ``api_access_id`` and ``api_secret_key`` arguments.  These arguments are not automatically sent by the ThreatConnect Platform and are required to be added to the :ref:install_json file.  In the ThreatConnect UI these inputs will be automatically hidden in favor of Token based authorization.  However, on the Integration Server these arguments should be required.

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

For proper HMAC authorization the HTTP Method and URI with query string arguments are required when building the authorization string.  Therefore the authorization string has to be built immediately before the request is sent.  The :py:meth:`~tcex.tcex.TcEx.authorization_hmac` method will build the authorization string when passed a *Python Requests* prepared request.