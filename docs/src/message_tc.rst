.. include:: <isonum.txt>
.. _message_tc:

==========
Message TC
==========
All ThreatConnect |trade| Exchange Apps should write an exit message on successful or failed execution.  The TcEx Frameworks provides the :py:meth:`~tcex.tcex.TcEx.message_tc` method to handle writing this message.  The contents of message_tc are shown in the ThreatConnect UI and should provide a meaning message to the user.

.. Warning:: The Message TC exit message only supports up to 255 characters.  All data added after that will be truncated.

.. Hint:: A successful execution might output: ``A total of 132 Indicators were written to Acme Corp.``

.. Hint:: A failed execution might output: ``Invalid API key provided for remote service.``

**Example Exit Message**

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 9,14

    tcex = TcEx()

    <...snipped>

    try:
        with open(datafile, 'r') as fh:
            data = fh.read()
    except:
        tcex.message_tc('Failed to open datafile for reading.')
        tcex.exit_code(1)

    <snipped...>

    tcex.message_tc('File successfully read.')
    tcex.exit()