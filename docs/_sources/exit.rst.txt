.. _exit:

=====
Exit
=====
All ThreatConnect Exchange and Playbook apps should deliberately provide an exit code on execution completion or failure. The TcEx module provides the :py:meth:`~tcex.tcex.TcEx.exit` and :py:meth:`~tcex.tcex.TcEx.exit_code` methods to handle exit codes.

Supported Exit Codes
---------------------

+ 0 - Successful execution of App
+ 1 - Failed execution of App
+ 3 - Parital failure of App