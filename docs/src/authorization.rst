.. _authorization:

===========================
Authorization (Token/HMAC)
===========================
The TcEx module use the :py:meth:`~tcex.tcex.TcEx.authorization` method to automatically determine whether Token based authorization or HMAC authorization should be used when connection to the ThreatConnect API.  It determines which authorization to use by checking if the ``tc_token`` arg was passed to the app or if ``api_access_id`` and ``api_secret_key`` are provided.

For HMAC authorization the :py:meth:`~tcex.tcex.TcEx.authorization_hmac` method will be used.  HMAC authorization is typically used when the app is running on the **integration server**.  All apps should support running in ThreatConnect Exchange or the ThreatConnect Integration server.

Using Token base authorization requires that the token be refreshed before expiration.  The TcEx module automatically handles token refresh using the :py:meth:`~tcex.tcex.TcEx._authorization_token_renew` method.