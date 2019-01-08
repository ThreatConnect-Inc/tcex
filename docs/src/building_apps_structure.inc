.. _building_apps_structure:

This guide is for written for development on a OSX or Linux system.  Development on a Windows system should follow similar steps.

.. Important:: This guide assumes that the workstation and ThreatConnect instance have the same version of Python installed. Writing Apps that support multiple versions of Python is supported but not covered in this quickstart.

Initializing an App
-------------------

.. code:: bash

    mkdir TCPB_-_JsonPretty
    cd TCPB_-_JsonPretty
    tcinit --action create --template playbook_utility
