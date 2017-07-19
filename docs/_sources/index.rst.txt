.. include:: <isonum.txt>

===========================================
ThreatConnect Exchange App Framework (TcEx)
===========================================

Release |version|.

.. toctree::
   :caption:  Table of Contents
   :maxdepth: 2

   authorization
   building_apps
   data_filter
   development_tools
   exit
   examples
   install_json
   jobs
   logging
   message_tc
   tcex_docs/modules
   parser
   playbook
   proxies
   request
   resource
   results_tc
   release_notes

Overview
--------
The ThreatConnect |trade| TcEx App Framework provides commonly used Classes and Methods for writing ThreatConnect Exchange Apps.  The Framework is intended to speed up the development process and ensure Apps contains the core functionality required.

This documentation provides a detailed level view of the TcEx Framework as well as some App overviews.  The Building Apps section is a good place to start when working on your first app.  The section overviews are intended to provide details of the core functionality of an App and the code references should provide further information for more in depth questions.

Features
--------

+ Automatic authorization for HMAC and Token base authentication when using :ref:`resources` functionality.  This allows the App to work seamlessly on both ThreatConnect Exchange Platform and the ThreatConnect Integration Server.
+ App logger that supports both filesystem and API logging (:ref:`logging`).
+ Batch add through :ref:`jobs` job module.
+ Common methods for proper App execution: exit codes (:ref:`exit`); exit messages (:ref:`message_tc`) and more

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`