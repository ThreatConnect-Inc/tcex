==============
Parser / Args
==============

The :py:meth:`~tcex.tcex.TcEx` module provides the :py:meth:`~tcex.tcex.TcEx.parser` property which returns and instance of :py:meth:`~tcex.argparser`. This argparser instance is an extension of the Python argparser method with predefined arguments specifically for ThreatConnect Exchange apps..

Default Arguments
------------------

+------------------------+----------------------------------------------------------+
| Section                | Values                                                   |
+========================+==========================================================+
| API                    | :py:meth:`~tcex.argparser.ArgParser._api_arguments`      |
+------------------------+----------------------------------------------------------+
| Batch                  | :py:meth:`~tcex.argparser.ArgParser._batch_arguments`    |
+------------------------+----------------------------------------------------------+
| Playbook               | :py:meth:`~tcex.argparser.ArgParser._playbook_arguments` |
+------------------------+----------------------------------------------------------+
| Standard               | :py:meth:`~tcex.argparser.ArgParser._standard_arguments` |
+------------------------+----------------------------------------------------------+

Custom Argument Example
------------------------
::

    from tcex import TcEx

    tcex = TcEx()
    parser = tcex.parser
    parser.add_argument('--myarg', help='My Custom Argument', required=True)
    args = tcex.args