.. include:: <isonum.txt>
.. _module_batch:

==============
Module - Batch
==============

.. important:: The Batch module requires ThreatConnect version 5.6 or higher.

The ThreatConnect |copy| TcEx Framework provides the :py:mod:`~tcex.tcex_ti_batch.TcExBatch` module to create, delete, and update both Groups and Indicators in the ThreatConnect Platform. The App developer can dynamically build a data objects and the Batch module will handle writing the data to the ThreatConnect API.

External ID (xid)
=================
The batch JSON data requires a xid value for all Groups and Indicators.  The XID is used internally in ThreatConnect for associations and for updating existing Groups.  The XID **must** be unique for the entire instance of ThreatConnect.

The :py:mod:`~tcex.tcex_ti_batch.TcExBatch` module provides the :py:meth:`~tcex.tcex_ti_batch.TcExBatch.generate_xid` method to assist in generating 2 types of xid. The first type of xid is a unique xid based on UUID4.  No input is required to produce a unique xid.  The second type is a unique and reproducible xid value.  This is the **preferred** xid type as it allows for a Group to have the same xid on subsequent runs of the App.  To generate a unique and reproducible xid either a string or array of value can be passed to the method (e.g., myapp-adversary-5 or ['myapp', 'adversary', '222']).

For Interface 1 and 2 the xid is optional, if not provided a unique xid (UUID4) will be auto-generated.  A string value can also be passed if the xid is a known value (e.g., the id field from an remote source). Passing in an xid when possible is **best practice** and allows Groups and Indicators to be easily updated.

.. important:: It is best practice to provide a unique and reproducible XID value when creating Groups. If the XID created for a new Group matches the XID for an existing Group the existing Group will be overwritten.

.. note:: In all of the examples below, the code to create the content is removed. You can read more about how to create the content in the `submit section <https://docs.threatconnect.com/en/latest/tcex/batch.html#submit>`__.

Groups
======
There are three interfaces to add Group Threat Intelligence data to the Batch Module.

Group Interface 1
-----------------
The first interface is for type specific access.  This interface allows for passing all the data in the method call or only the required fields with optional fields being set via property setters. All metadata (e.g., Attributes, Security Labels, and Tags) can be added to the group instance directly.

The example below passes all supported fields to the``adversary()`` method.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2-5,7

    batch = tcex.batch('MyOrg')
    adversary = batch.adversary('adversary-001', xid='my-xid-000')
    adversary.attribute('Description', 'Example Description', True)
    adversary.tag('Example Tag')
    adversary.security_label('TLP Green')
    # optional save method
    batch.save(adversary)

The example below passes only the required fields to document().  The optional properties can then be set whenever required. The same interface is used for the attribute.  The required attribute properties are set first and then optional values can be added.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2-5,6-7,9,11-13,15

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
    # optional save method
    batch.save(document)

.. note:: The optional ``batch.save()`` method will write the group or indicator to disk.  When processing large amounts of data this is the preferred method in order to save on the memory usage of the App.

.. important:: The **file_content** parameter for documents and reports will accept multiple types of data as well as a callback method.  The callback method will be passed the xid of the documents/report and expects a single response containing the contents of the file.  If loading a large number of documents it is best practice to not load the contents in memory, but instead use the callback method so that the files can be processed one at a time.

Group Interface 2
-----------------
The second more dynamic interface uses the more generic :py:meth:`~tcex.tcex_ti_batch.TcExBatch.group` method.  In this interface the group type, group name and optional xid are the only allowed fields.  For type specific field such as **eventDate** for an Event Group the :py:meth:`~tcex.tcex_ti_group.Group.add_key_value` method is available. The field name must be exactly what the batch API expects (which are listed `here <https://docs.threatconnect.com/en/latest/rest_api/groups/groups.html#group-fields>`__).  Adding metadata behaves the same as in Interface 1.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2-6

    batch = tcex.batch('MyOrg')
    event = batch.group('Event', date_added='event-001', xid='my-xid-0001')
    event.add_key_value('eventDate', 'yesterday')
    event.add_key_value('status', 'New')
    event.attribute('Description', 'Example Description 2', True, 'source')
    event.tag('Example Tag')

The code below demonstrates how to create a Document using this interface (and the same principle applies for Reports and any other groups to which file contents can be added):

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 3-7

    batch = tcex.batch('MyOrg')
    document = batch_job.group('Document', 'document-001', xid='my-xid-0001')
    document.add_file('test.txt', 'Document content here...')
    document.add_key_value('fileName', 'test.txt')
    document.attribute('Description', 'Example Description', True, 'Attribute source')
    document.tag('Example Tag')
    document.security_label('TLP Green')

Group Interface 3
-----------------
The third interface accepts the raw data formatted as a dictionary.  This method requires that an xid be provided.  All metadata should be included with in the JSON object.  You can view the required fields for each group type `here <https://docs.threatconnect.com/en/latest/rest_api/groups/groups.html#group-fields>`__.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 3-20

    batch = tcex.batch('MyOrg')
    xid = batch.generate_xid(['my', 'adversary', '123'])
    batch.add_group({
        'name': 'document-002',
        'fileName': 'test2.txt',
        'fileContent': 'example content 2',
        'type': 'Document',
        'xid': xid,
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

Indicator Interface 1
---------------------
The first interface is for type specific access.  This interface allows for passing all the data in the method call or only the required fields with optional fields being set via property setters. All metadata (e.g., Attributes, Security Labels, and Tags) can be added to the indicator instance directly.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2-5

    batch = tcex.batch('MyOrg')
    address = batch.address('123.124.125.126', rating='5.0', confidence='100')
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

Indicator Interface 2
---------------------
The second more dynamic interface uses the more generic :py:meth:`~tcex.tcex_ti_batch.TcExBatch.indicator` method.  In this interface the indicator type, indicator value, optional rating, optional confidence, and optional xid are the only allowed fields.  For type specific field such as **size** for a File indicator the :py:meth:`~tcex.tcex_ti_indicator.Indicator.add_key_value` method is available. The field name must be exactly what the batch API expects (which are listed `here <https://docs.threatconnect.com/en/latest/rest_api/indicators/indicators.html#indicator-fields>`__).  Adding metadata behaves the same as in Interface 1.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2-6

    batch = tcex.batch('MyOrg')
    host = batch.indicator('Host', 'www.badguys2.com', rating='5.0', confidence='100')
    host.add_key_value('dnsActive', True)
    host.add_key_value('whoisActive', True)
    host.attribute('Description', 'Example Description 2', True, 'source')
    host.tag('Example Tag')

.. note:: The case of the indicator type (the first argument provided to the `batch.indicator()` function) should be the same as the `name` key provided when retrieving the `indicator types <https://docs.threatconnect.com/en/latest/rest_api/indicators/indicators.html#retrieve-available-indicator-types>`__.

Indicator Interface 3
---------------------
The third interface accepts the raw data formatted as a dictionary. This method requires that an xid be provided. All metadata should be included with in the data. You can view the required fields for each indicator type `here <https://docs.threatconnect.com/en/latest/rest_api/indicators/indicators.html#indicator-fields>`__.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2-25

    batch = tcex.batch('MyOrg')
    batch.add_indicator({
        "type": "File",
        "rating": 5.00,
        "confidence": 50,
        "summary": "53c3609411c83f363e051d455ade78a7 : 57a49b478310e4313c54c0fee46e4d70a73dd580 : db31cb2a748b7e0046d8c97a32a7eb4efde32a0593e5dbd58e07a3b4ae6bf3d7",
        "associatedGroups": [
            {
                "groupXid": "e336e2dd-5dfb-48cd-a33a-f8809e83e904"
            }
        ],
        "attribute": [{
            "type": "Source",
            "displayed": True,
            "value": "Malware Analysis provided by external AMA."
        }],
        "fileOccurrence": [{
            "fileName": "drop1.exe",
            "date": "2017-03-03T18:00:00-06:00"
        }],
        "tag": [{
            "name": "China"
        }],
        "xid": "e336e2dd-5dfb-48cd-a33a-f8809e83e904:170139"
    })

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
        "associatedGroups": [{
            "groupXid": "my-xid-001"
        }],
        "summary": "HKEY_LOCAL_MACHINE\system : TRUE : REG_DWORD",
        "type": "Registry Key",
        "xid": "ba60d2d6-8049-4080-9c5c-2b33d8d97767"
    }

Submit
======
There are few options for submitting the batch job, all with an option to halt_on_error.  The most common option :py:meth:`~tcex.tcex_ti_batch.TcExBatch.submit_all` provides a simple interface that will perform all the individual step by default (e.g., request create and upload, poll for status, retrieve errors, and submit files).  When using this method it is possible to control the halt_on_error behavior for each step using global overrides.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 1

    batch = tcex.batch('MyOrg')
    # defaults to true or uses the provided value passed to the submit method. this value controls the behavior
    # for errors when creating batch job and submitting the data.
    batch.halt_on_batch_error = False

    # defaults to true or uses the provided value passed to the submit method. this value controls the behavior
    # for errors when submitting files. if set to True a single file upload error would cause the batch module
    # to raise and exception and potentially cause the job to fail.
    batch.halt_on_file_error = False

    # defaults to true or uses the provided value passed to the submit method. this value controls the behavior
    # for errors when polling batch status.
    batch.halt_on_poll_error = False

    if errors:
        tcex.exit(1, 'Errors during Batch: {}'.format(errors))

In some cases handling errors may require more control.  For these cases the submit method can be called with some or all of the additional features (e.g., polling, retrieving errors, and uploading files) disabled. It is also possible to call each method individually.  A possible workflow could be to use :py:meth:`~tcex.tcex_ti_batch.TcExBatch.submit_create_and_upload` and then go retrieve data from remote endpoint while ThreatConnect processes the batch job.  Next poll using :py:meth:`~tcex.tcex_ti_batch.TcExBatch.poll` for status and when the job is Completed the next job request can be submitted. If batch errors are reported in the Batch status the :py:meth:`~tcex.tcex_ti_batch.TcExBatch.errors` method can be used to retrieve the errors.  Submitting files for Documents and Reports can be done using the :py:meth:`~tcex.tcex_ti_batch.TcExBatch.submit_files` method.

.. note:: The setting **synchronousBatchSaveLimit** in the ThreatConnect UI -> System Settings controls the synchronous processing of batch jobs. If the batch job is smaller than the defined value the batch data will be processed synchronously and the batch status will be returned on completion without the need to poll. The :py:meth:`~tcex.tcex_ti_batch.TcExBatch.submit` method provides logic for handling this so the developer is not required to check if the job was queued.

Option 1
--------
Submit the job and wait for completion. In the example any error messages are requested to be returned as well.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 1

    batch_data = batch.submit_all()
    errors = batch_data.get('errors')
    if errors:
        tcex.exit(1, 'Errors during Batch: {}'.format(errors))

Option 2
--------
Call each step in submitting the batch job manually. A check for batch_id will indicate whether the job was processed asynchronously.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2,5-14,17

    # submit batch job create and upload request
    batch_data = batch.submit_create_and_upload().get('data').get('batchStatus')

    # check if job requires polling
    batch_id = batch_data.get('id')
    if batch_id is not None:
        # poll for batch status
        batch_status = batch.poll(batch_id)

        # check for errors
        if batch_status.get('data', {}).get('batchStatus', {}).get('errorCount', 0) > 0:
            # retrieve errors
            errors = batch.errors(batch_id)
            print(errors)

    # submit any documents or reports
    upload_status = batch.submit_files()
