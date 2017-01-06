.. _jobs:

=====
Jobs
=====
The TcEx module provides the :py:meth:`~tcex.tcex_job.TcExJob` module to automate writing certain data types to the ThreatConnect API. The App developer can dynamically build a JSON data object and the Job module will handle writing the data to the ThreatConnect API.

Once all the data has been added to the job the :py:meth:`~tcex.tcex_job.TcExJob.process` method will attempt to write the data to the ThreatConnect API.  Any failures will set the exit code to 3 (partial failure) unless the error is defined as a critical failure.

Groups
-------
The :py:meth:`~tcex.tcex_job.TcExJob.group` method accepts the following data structure.

::

    {
      'attribute': [
        {
          'type': 'Description',
          'value': 'Test Description'
        }
      ],
      'name': 'adversary-001',
      'tag': [
        'APT',
        'Crimeware'
      ],
      'type': 'Adversary'
    }


Group Associations
-------------------
The :py:meth:`~tcex.tcex_job.TcExJob.group_association` method accepts the following data structure.

::

    {
      'group_name': 'adversary-001',
      'group_type': 'Adversary',
      'indicator': '1.1.1.1',
      'indicator_type': 'Address'
    }

Indicator Structure
--------------------
The :py:meth:`~tcex.tcex_job.TcExJob.indicator` method accepts the following data structure.

::

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
        'APT',
        'Crimeware'
      ],
      'type': 'Address'
    }