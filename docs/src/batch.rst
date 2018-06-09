.. include:: <isonum.txt>
.. _batch:

=====
Batch
=====

.. important:: The Batch module required ThreatConnect 5.6 or higher.

The ThreatConnect |trade| TcEx Framework provides the :py:mod:`~tcex.tcex_batch_v2.TcExBatch` module to create, delete, and update both Groups and Indicator in the ThreatConnect Platform. The App developer can dynamically build a data objects and the Batch module will handle writing the data to the ThreatConnect API.

External ID (xid)
=================
The batch JSON data requires a xid value for all Groups and Indicators.  The XID is used internally in ThreatConnect for associations and for updating existing Groups.

For Interface 1 and 2 the xid is optional, if not provided or set to True a unique xid based off the group "type-name" or indicator "type-value" will be auto-generated.  If xid is set to False a random xid will be generated. A string value can also be passed if the xid is a known value (e.g., the id field from an remote source). Passing in an xid when possible is best practice and allows Groups and Indicators to be easily updated.

.. note:: For Groups when using a unique xid value generated using "type-name" support of duplicate group name is not possible.  If having duplicate group names is a requirement then a xid should be provided for each group.

Groups
======
There are three interfaces to add Group Threat Intelligence data to the Batch Module.

Interface 1
-----------
The first interface is for type specific access.  This interface allows for passing all the data in the method call or only the required fields with optional fields being set via property setters. All metadata (e.g., Attributes, Security Labels, and Tags) can be added to the group instance directly.

The example below passes all supported fields to adversary().

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2-5

    batch = tcex.batch('MyOrg')
    adversary = batch.adversary('adversary-001' 'my-xid-000')
    adversary.attribute('Description', 'Example Description', True)
    adversary.tag('Example Tag')
    adversary.security_label('TLP Green')

The example below passes only the required fields to document().  The optional properties can then be set whenever required. The same interface is used for the attribute.  The required attribute properties are set first and then optional values can be added.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2-5,6-7,9,11-13

    batch = tcex.batch('MyOrg')
    document = batch.document('document-001', 'example.txt')
    document.malware = True
    document.password = 'test'
    document.file_content = 'example file content'
    # Add Attribute
    attr = document.attribute('Description', 'Example Description')
    attr.displayed = True
    # Add Tag
    document.tag('Example Tag')
    # Add Label
    label = document.security_label('My Label')
    label.color = 'ffffff'
    label.description = 'Security label description.'

.. important:: The **file_content** parameter for documents and reports will accept multiple types of data as well as a callback method.  The callback method will be passed the xid of the documents and expects a single response containing the contents of the file.  If loading a large number of documents it best practice to not load them in memory, but instead us the callback method so that the files can be processed one at a time.

Interface 2
-----------
The second more dynamic interface uses the more generic :py:meth:`~tcex.tcex_batch_v2.TcExBatch.group` method.  In this interface the group type, group name and optional xid are the only allowed fields.  For type specific field such as **eventDate** for an Event Group the :py:meth:`~tcex.tcex_batch_v2.Group.add_key_value` method is available. The field name must be exactly what the batch API expects.  Adding metadata behaves the same as in Interface 1.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2-6

    batch = tcex.batch('MyOrg')
    event = batch.group('Event', 'event-001', 'my-xid-0001')
    event.add_key_value('eventDate', 'yesterday')
    event.add_key_value('status', 'New')
    event.attribute('Description', 'Example Description 2', True, 'source')
    event.tag('Example Tag')

Interface 3
-----------
The third interface accept the raw data formatted as a dictionary.  This method required that an xid be provided.  All metadata should be included with in the data.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2-18

    batch = tcex.batch('MyOrg')
    batch.add_group({
        'name': 'document-002',
        'fileName': 'test2.txt',
        'fileContent': 'example content 2',
        'type': 'Document',
        'xid': 'my-xid-002',
        "associatedGroupXid": [
            "my-xid-001"
        ],
        'attribute': [{
            "displayed": True,
            "type": "Description",
            "value": "Example Description"
        }],
        'tag': [{
            'name': 'SafeToDelete'
        }]
    })

Indicators
==========
There are three interfaces to add Indicator Threat Intelligence data to the Batch Module.

Interface 1
-----------
The first interface is for type specific access.  This interface allows for passing all the data in the method call or only the required fields with optional fields being set via property setters. All metadata (e.g., Attributes, Security Labels, and Tags) can be added to the indicator instance directly.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2-5

    batch = tcex.batch('MyOrg')
    address = batch.address('123.124.125.126', '5.0', '100')
    address.attribute('Description', 'Example Description', True)
    address.tag('Example Tag')
    address.security_label('TLP Green')

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2-4,6-7,9,11-13,15-18

    batch = tcex.batch('MyOrg')
    file_hash = batch.file('43c3609411c83f363e051d455ade78a6')
    file_hash.rating = 5.0
    file_hash.confidence = 100
    # Add Attribute
    attr = file_hash.attribute('Description', 'Example Description')
    attr.displayed = True
    # Tag
    file_hash.tag('Example Tag')
    # Add Label
    label = file_hash.security_label('My Label')
    label.color = 'ffffff'
    label.description = 'Security label description.'
    # Add Occurrence
    occurrence = file_hash.occurrence()
    occurrence.file_name = 'drop1.exe'
    occurrence.path = 'C:\\test\\'
    occurrence.date = '2017-02-02 01:02:03'

Interface 2
-----------
The second more dynamic interface uses the more generic :py:meth:`~tcex.tcex_batch_v2.TcExBatch.indicator` method.  In this interface the indicator type, indicator value, optional rating, optional confidence, and optional xid are the only allowed fields.  For type specific field such as **size** for a File indicator the :py:meth:`~tcex.tcex_batch_v2.Indicator.add_key_value` method is available. The field name must be exactly what the batch API expects.  Adding metadata behaves the same as in Interface 1.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2-6

    batch = tcex.batch('MyOrg')
    host = batch.indicator('Host', 'www.badguys2.com', '5.0', '100')
    host.add_key_value('dnsActive', True)
    host.add_key_value('whoisActive', True)
    host.attribute('Description', 'Example Description 2', True, 'source')
    host.tag('Example Tag')

File Occurrence
---------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    # <... snipped>
    file_hash.occurrence('drop1.exe', 'C:\\test\\', '2017-02-02 01:02:03')
    # <snipped ...>

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2-5

    # <... snipped>
    occurrence = file_hash.occurrence()
    occurrence.file_name = 'drop1.exe'
    occurrence.path = 'C:\\test\\'
    occurrence.date = '2017-02-02 01:02:03'
    # <snipped ...>

Associations
============
Associations are supported as Group -> Group or Indicator -> Group.  Using Interface 1 or 2 the behavior is the same for Group and Indicators.  However, for Interface 3 the structure is slightly different as displayed below.

Group
-----
Example of Group -> Group association.

.. code-block:: javascript
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 5-7

    {
        "name": "document-002",
        "type": "Document",
        "xid": "my-xid-002",
        "associatedGroupXid": [
            "my-xid-001"
        ]
    }

Indicator
---------
Example of Indicator -> Group association.

.. code-block:: javascript
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2-6

    {
        "associatedGroups": [
            {
                "groupXid": "my-xid-001"
            }
        ],
        "summary": "HKEY_LOCAL_MACHINE\system : TRUE : REG_DWORD",
        "type": "Registry Key",
        "xid": "ba60d2d6-8049-4080-9c5c-2b33d8d97767"
    }

Submit
======
There are two options for submitting the batch job, both with an option to halt_on_error.  Option 1 :py:meth:`~tcex.tcex_batch_v2.TcExBatch.submit` provides a simple interface that will perform all the individual step by default (e.g., request batch job, submit data, poll for status, and submit files).  If enabled it will also retrieve any batch errors.  However, handling errors using option 1 is limited.  In Option 2 each step is done individually and allows for greater control of the submit process.  You can request a batch job using :py:meth:`~tcex.tcex_batch_v2.TcExBatch.submit_job` , submit data using :py:meth:`~tcex.tcex_batch_v2.TcExBatch.submit_data` and then go retrieve data from remote endpoint while ThreatConnect processes the batch job.  Then poll using :py:meth:`~tcex.tcex_batch_v2.TcExBatch.poll` for status and submit the next job request. If batch errors are reported in the Batch status the :py:meth:`~tcex.tcex_batch_v2.TcExBatch.errors` method can be used to retrieve the errors.

Option 1
--------
Submit the job and wait for completion. In the example any error messages are requested to be returned as well.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 1

    batch_data = batch.submit(errors=True)
    errors = batch_data.get('errors')
    if errors:
        tcex.exit(1, 'Errors during Batch: {}'.format(errors))

Option 2
--------
Call each step in submitting the batch job manually.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2,5,8,13,17

    # submit batch job request
    batch_id = batch.submit_job()

    # submit the batch data
    batch.submit_data(batch_id)

    # poll for batch status
    batch_status = batch.poll(batch_id)

    # check for errors
    if batch_status.get('data', {}).get('batchStatus', {}).get('errorCount', 0) > 0:
        # retrieve errors
        errors = batch.errors(batch_id)
        print(errors)

    # submit any documents or reports
    upload_status = batch.submit_files()
