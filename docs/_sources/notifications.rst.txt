.. include:: <isonum.txt>
.. _notifications:

=============
Notifications
=============
The ThreatConnect |trade| TcEx App Framework provides a simple interface for creating Notifications within ThreatConnect.  For more information on ThreatConnect Notifications see the docs at https://docs.threatconnect.com

Notification Instance
=====================
The ``tcex.notification()`` method has no required fields and creates a local notification object.  As there are two main ways that notifications are used in ThreatConnect, there are 2 main methods and a send method.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    notification = tcex.notification()

Recipients
==========
The ``recipients()`` method is used when sending to a distinct set of ThreatConnect users. It requires fields of **type** and **recipients**. It also accepts an optional field for **priority**.  If no priority is provided the value of 'Low' is used. **type** is a free formed text field used for filtering within the ThreatConnect UI. Recipients is a comma separated list of ThreatConnect UserIDs.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    notification.recipients('Import Success', 'devOps@mycompany.net,jsmith@mycompany.net', 'Medium')


Organization
============
The ``org()`` method is used when sending to the Org related to the 'user' used in connecting to ThreatConnect. It requires a **type** field.  It also accepts an optional field for **priority**.  If no priority is provided the value of 'Low' is used. **type** is a free formed text field used for filtering within the ThreatConnect UI.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    notification.org('Import Success', 'High')


Send
====
The ``send()`` method is used to send the actual notification. It requires a field of **message** which is a free formed text field containing the message shown in the ThreatConnect UI.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    status = notification.send('Import was successful')
