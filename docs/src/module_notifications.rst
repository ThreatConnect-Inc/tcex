.. include:: <isonum.txt>
.. _module_notifications:

======================
Module: Notifications
======================
The ThreatConnect TcEx App Framework provides a simple interface for creating Notifications within ThreatConnect.  For more information on ThreatConnect Notifications, see the documents at https://docs.threatconnect.com/en/latest/rest_api/notifications/notifications.html.

Notification Instance
=====================
The :py:meth:`~tcex.notification.Notification` method has no required fields and creates a local Notification object.  As there are two main ways that Notifications are used in ThreatConnect, there are two main methods and a send method.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    notification = tcex.notification()

Recipients
==========
The :py:meth:`~tcex.notification.Notification.recipients` method is used when sending to a distinct set of ThreatConnect users. It requires fields of **type** and **recipients**. It also accepts an optional field for **priority**.  If no priority is provided, the value of **Low** is used. Within the ThreatConnect UI, **type** is a free formed text field that is used for filtering **Recipients** is a comma-separated list of ThreatConnect UserIDs.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    notification.recipients('Import Success', 'devOps@mycompany.net,jsmith@mycompany.net', 'Medium')


Organization
============
The :py:meth:`~tcex.notification.Notification.org` method is used when sending to the organization related to the **user** that is employed when connecting to ThreatConnect. It requires a **type** field.  It also accepts an optional field for **priority**.  If no priority is provided, the value of **Low** is used. Within the ThreatConnect UI, **type** is a free-formed text field tha is used for filtering.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    notification.org('Import Success', 'High')


Send
====
The :py:meth:`~tcex.notification.Notification.send` method is used to send the actual Notification. It requires a field of **message**, which is a free-formed text field containing the message shown in the ThreatConnect UI.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    status = notification.send('Import was successful')
