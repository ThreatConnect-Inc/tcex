.. include:: <isonum.txt>

======
 TcEx
======

------------------------------------------------------------------
ThreatConnect Exchange App Framework
------------------------------------------------------------------

Release |version|.

.. toctree::
   :caption:  Table of Contents
   :maxdepth: 2

   authorization
   exit
   install_json
   jobs
   logging
   message_tc
   parser
   playbook
   proxies
   request
   resource
   results_tc
   release_notes

Overview
---------
The ThreatConnect |trade| TcEx App Framework provides commonly used Classes and Methods for writing ThreatConnect Exchange Apps.  The Framework is intended to speed up the development process and ensure Apps contains the core functionality required.

This documenation provides a detailed level view of the TcEx Framework as well as some App overviews.  The Building Apps section is a good place to start when working on your first app.  The section overviews are intended to provide details of the core functionality of an App and the code references should provide further information for more in depth questions.

Features
---------

+ Automatic authorization for HMAC and Token base authentication when using :ref:`resources` functionality.  This allow the app to work seemlessly on both ThreatConnect Exchange and the ThreatConnect Integration Server.
+ App logger that supports both filesystem and API logging (:ref:`logging`).
+ Batch add through job interface (:ref:`jobs`).
+ Common methods for proper execution exit codes (:ref:`exit`)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`