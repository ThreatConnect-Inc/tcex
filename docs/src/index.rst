======
 TcEx
======

------------------------------------------------------------------
Python helper module for ThreatConnect Exchange and Playbook Apps
------------------------------------------------------------------

Release v\ |version|.

.. toctree::
   :caption:  Table of Contents
   :maxdepth: 2

   authorization
   exit
   jobs
   logging
   message_tc
   parser
   playbook
   proxies
   request
   resource
   results_tc

Overview
---------
The :py:class:`~tcex.tcex.TcEx` Class provides method for common functionality used in ThreatConnect Exchange or ThreatConnect Playbook apps.

Features
---------

+ Automatic authorization for HMAC and Token base authentication when using :ref:`resources` functionality.  This allow the app to work seemlessly on both ThreatConnect Exchange and the ThreatConnect Integration Server.
+ App logger that supports both filesystem and API logging (:ref:`logging`).
+ Batch add through job interface (:ref:`jobs`).

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`