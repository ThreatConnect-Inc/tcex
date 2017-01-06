.. _message_tc:

===========
Message TC
===========
All ThreatConnect Exchange and Playbook Apps should write to :py:meth:`~tcex.tcex.TcEx.message_tc` before exiting.  The contents of message_tc are shown in the ThreatConnect UI and should provide a meaning message to the user.

.. Hint:: A successful execution might output: ``132 Indicators written to Acme Corp.``

.. Hint:: A failed execution might output: ``Invalid API key provided for remote service.``