.. include:: <isonum.txt>
.. _jobs:

=====
Jobs
=====
The ThreatConnect |trade| TcEx Framework provides the :py:mod:`~tcex.tcex_job.TcExJob` module to automate writing certain data types to the ThreatConnect API. The App developer can dynamically build a JSON data object and the Job module will handle writing the data to the ThreatConnect API.

Once all the data has been added to the job a call to the :py:meth:`~tcex.tcex_job.TcExJob.process` method will attempt to write the data to the ThreatConnect API.

.. Note:: Any failures will set the :py:meth:`~tcex.tcex.TcEx.exit_code` to **3** or partial failure, unless the error is defined as a critical failure (defined in the __init__ method of :py:meth:`~tcex.tcex_job.TcExJob`.

Groups
-------
The :py:meth:`~tcex.tcex_job.TcExJob.group` method accepts the following data structure. All required fields are highlighted.

.. code-block:: javascript
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 8,13

    {
      'attribute': [
        {
          'type': 'Description',
          'value': 'Test Description'
        }
      ],
      'name': 'Robin Sparkles',
      'tag': [
        'APT',
        'Crimeware'
      ],
      'type': 'Adversary'
    }

.. Note:: The Jobs module will make multiple API calls to push all this data to the ThreatConnect API.

Group Associations
-------------------
The :py:meth:`~tcex.tcex_job.TcExJob.group_association` method accepts the following data structure. All required fields are highlighted.

.. code-block:: javascript
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2-5

    {
      'group_name': 'Robin Sparkles',
      'group_type': 'Adversary',
      'indicator': '1.1.1.1',
      'indicator_type': 'Address'
    }

.. Warning:: If more than on Group exist with the same name the association created using
             :py:meth:`~tcex.tcex_job.TcExJob.group_association` will only associate the indicator
             to the first group found with the name.

Indicators
-----------
The :py:meth:`~tcex.tcex_job.TcExJob.indicator` method accepts the following data structure. All required fields are highlighted.

.. code-block:: javascript
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 14,22

    {
      'associatedGroup': [
        '1',
        '8'
      ],
      'attribute': [
        {
          'type': 'Description',
          'value': 'Test Description'
        }
      ],
      'confidence': 5,
      'rating': '3',
      'summary': '1.1.1.1',
      'tag': [
        {
          'name': 'APT'
        },{
          'name': 'Crimeware'
        }
      ],
      'type': 'Address'
    }

File Occurrence
----------------
The :py:meth:`~tcex.tcex_job.TcExJob.file_occurrence` method accepts the following data structure. All required fields are highlighted.

.. code-block:: javascript
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 3

    {
        "date" : "2014-11-03T00:00:00-05:00",
        "fileName" : "win999301.dll",
        "hash": "BE7DE2F0CF48294400C714C9E28ECD01",
        "path" : "C:\\Windows\\System"
    }

Sample Job Flow
-----------------
The key method calls are highlighted in the following code sample.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 12,18,24,32,34-37

    from tcex import TcEx
    tcex = TcEx()

    # Get TcEx parser
    parser = tcex.parser
    parser.add_argument('--owner', help='ThreatConnect Owner', required=True)

    # Get parsed args
    args = tcex.args

    # add indicator
    tcex.jobs.indicator({
        'summary': '1.2.3.4',
        'type': 'Address'
    })

    # add group
    tcex.jobs.group({
        'name': 'Robin Sparkles',
        'type': 'Adversary'
    })

    # add associations
    tcex.jobs.group_association({
        'group_name': 'Robin Sparkles',
        'group_type': 'Adversary',
        'indicator': '1.2.3.4',
        'indicator_type': 'Address
    })

    # process job
    tcex.jobs.process(args.owner)

    tcex.message_tc(
        '{} group, {} indicator and {} association added.'.format(
        tcex.jobs.group_len, tcex.jobs.indicator_len, tcex.jobs.group_association_len))
    tcex.exit()


.. Note:: The Batch API call allows for Group Associations via the ``associatedGroup`` field using
          the Group Id. However, if Groups are being added in the Job the Group Id will not be known
          until after the Group is added.  The :py:meth:`~tcex.tcex_job.TcExJob.group_association`
          method allows the Group named to be used instead of the Group Id. If the Group Id is
          already known it can be associated using the ``associatedGroup`` field.