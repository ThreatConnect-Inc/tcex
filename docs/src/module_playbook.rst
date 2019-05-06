.. include:: <isonum.txt>
.. _module_playbooks:

==================
Module: Playbooks
==================
The ThreatConnect TcEx App Framework provides common *helper* methods to write a Playbooks App.  The :py:mod:`~tcex.tcex_playbook.TcExPlaybook` module provides all required methods to communicate with upstream and downstream Apps.

Understanding Playbooks
-----------------------
A Playbook App is a single component of a Playbook.  These Apps are intended to be reusable, standalone components with minimum functionality to solve a single purpose.  Multiple Playbook Apps will make up a Playbook that solves a use case.  For more information on Playbook methodology and functionality, refer to the Playbooks documentation at: https://docs.threatconnect.com/en/latest/rest_api/playbooks/playbooks.html.

Playbook Flow
-------------
As a Playbook starts execution, each App will have input and output variables.  The input variables can be user-provided data or output from an upstream App.  The App's input and output variables are defined in the :ref:`app_deployment_configuration` file of the App.  A downstream App has access to all output variables from any upstream Apps.

.. Note:: An upstream App is an App that has completed execution prior to the current App's execution.


Input Variables
---------------
Inputs to an App can be static user data or dynamic output variables from a trigger or upstream App.  The :py:mod:`~tcex.tcex_playbook.TcExPlaybook` module provides the :py:mod:`~tcex.tcex_playbook.TcExPlaybook.read` method for pulling dynamic data from an upstream App. The :py:mod:`~tcex.tcex_playbook.TcExPlaybook.read` method will automatically determine the variable type for the App developer. If user data was passed instead of the output variable, the :py:mod:`~tcex.tcex_playbook.TcExPlaybook.read` will return the unaltered string.

.. Tip:: The :py:mod:`~tcex.tcex_playbook.TcExPlaybook.read` method will also handle mixed-type data by automatically calling the :py:mod:`~tcex.tcex_playbook.TcExPlaybook.read_embedded` method when a mixed-type variable is identified.

Output Variables
----------------
Playbook Apps write output variables for downstream Apps.  The :py:mod:`~tcex.tcex_playbook.TcExPlaybook` module provides the :py:mod:`~tcex.tcex_playbook.TcExPlaybook.create` method for writing output variables.  However, output variables should only be written when requested by a downstream App.  The requested variables are passed in the ``args.tc_playbook_out_variables`` argument as a CSV string.  The :py:mod:`~tcex.tcex_playbook.TcExPlaybook` module provides the :py:mod:`~tcex.tcex_playbook.TcExPlaybook.create_output` method that will validate that a downstream App requested the output variable before writing.

.. Hint:: In most cases, the :py:mod:`~tcex.tcex_playbook.TcExPlaybook.create_output` method is the best way to write output variables.

Variable Types
--------------
When output variables are passed to the input of an App, the variable type is defined.  In some cases it is useful to know the type of variable passed. The :py:mod:`~tcex.tcex_playbook.TcExPlaybook` module provides the :py:mod:`~tcex.tcex_playbook.TcExPlaybook.variable_type` method that will return the variable type.


+ Binary
+ BinaryArray
+ KeyValue
+ KeyValueArray
+ String
+ StringArray
+ TCEntity
+ TCEntityArray

.. Note:: For more information on Playbook variable types or updated types, see the Playbooks documentation.
