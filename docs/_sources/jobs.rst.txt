.. include:: <isonum.txt>
.. _jobs:

====
Jobs
====
The ThreatConnect |trade| TcEx Framework provides the :py:mod:`~tcex.tcex_job.TcExJob` module to automate writing certain data types to the ThreatConnect API. The App developer can dynamically build a JSON data object and the Job module will handle writing the data to the ThreatConnect API.

Once all the data has been added to the job a call to the :py:meth:`~tcex.tcex_job.TcExJob.process` method will attempt to write the data to the ThreatConnect API.

.. Note:: Any failures will set the :py:meth:`~tcex.tcex.TcEx.exit_code` to **3** or partial failure, unless the error is defined as a critical failure (defined in the __init__ method of :py:meth:`~tcex.tcex_job.TcExJob`.

Groups
------
The :py:meth:`~tcex.tcex_job.TcExJob.group` method accepts the following data structure. All required fields are highlighted.

.. code-block:: javascript
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 8,16

    {
      "attribute": [
        {
          "type": "Description",
          "value": "Test Description"
        }
      ],
      "name": "Robin Sparkles",
      "tag": [
        {
          "name": "APT"
        },{
          "name": "CrimeWare"
        }
      ],
      "type": "Adversary"
    }

.. Note:: The Jobs module will make multiple API calls to push all this data to the ThreatConnect API.

The module provides the :py:mod:`~tcex.tcex_job.TcExJob.group_results` property to get the status of each Group submitted.

.. code-block:: javascript
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2-5,8

    {
        "cached": [],
        "failed": [],
        "not_saved": [],
        "saved": [
            "Robin Sparkles",
        ],
        "submitted": [
            "Robin Sparkles",
        ]
    }

+ Cached - The Group already existed in ThreatConnect and was pulled from cache.
+ Failed - The Group add encountered an error when submitting to the API.
+ Not Saved - The Group was not saved either due to a failure or "Halt on Error" was selected and a previous Group failed.
+ Saved - The Group was saved to ThreatConnect via the API.
+ Submitted - The complete list of submitted Group Names.

Group Associations
------------------
The :py:meth:`~tcex.tcex_job.TcExJob.group_association` method accepts the following data structure. All required fields are highlighted.

.. code-block:: javascript
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2-5

    {
      "group_name": "Robin Sparkles",
      "group_type": "Adversary",
      "indicator": "1.1.1.1",
      "indicator_type": "Address"
    }

.. Warning:: If more than one Group exist with the same name the association created using
             :py:meth:`~tcex.tcex_job.TcExJob.group_association` will only associate the indicator
             to the first group found with the name.

Indicators
----------
The :py:meth:`~tcex.tcex_job.TcExJob.indicator` method accepts the following data structure. All required fields are highlighted.

.. code-block:: javascript
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 14,22

    {
      "associatedGroup": [
        "1",
        "8"
      ],
      "attribute": [
        {
          "type": "Description",
          "value": "Test Description"
        }
      ],
      "confidence": 5,
      "rating": "3",
      "summary": "1.1.1.1",
      "tag": [
        {
          "name": "APT"
        },{
          "name": "CrimeWare"
        }
      ],
      "type": "Address"
    }

.. note:: To create file indicators using the ``tcex.tcex_job.indicator()`` function, the ``summary`` should be a string with each file hash (md5, sha1, and/or sha256) separated by ``<space>:<space>``. For example, the following json would create a file indicator with the md5 hash ``905ad8176a569a36421bf54c04ba7f95``, sha1 hash ``a52b6986d68cdfac53aa740566cbeade4452124e`` and sha256 hash ``25bdabd23e349f5e5ea7890795b06d15d842bde1d43135c361e755f748ca05d0``:

    .. code-block:: javascript
    
        {
          "summary": "905ad8176a569a36421bf54c04ba7f95 : a52b6986d68cdfac53aa740566cbeade4452124e : 25bdabd23e349f5e5ea7890795b06d15d842bde1d43135c361e755f748ca05d0",
          "type": "File"
        }

The module provides the :py:mod:`~tcex.tcex_job.TcExJob.indicator_results` property to get the status of each Indicator submitted.

.. code-block:: javascript
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2,5,8,14

    {
        "failed": [
            "905ad8176a569a36421bf54c04ba7f95 : a52b6986d68cdfac53aa740566cbeade4452124e : 25bdabd23e349f5e5ea7890795b06d15d842bde1d43135c361e755f748ca05d0"
        ],
        "not_saved": [
            "905ad8176a569a36421bf54c04ba7f95 : a52b6986d68cdfac53aa740566cbeade4452124e : 25bdabd23e349f5e5ea7890795b06d15d842bde1d43135c361e755f748ca05d0"
        ],
        "saved": [
            "1.2.3.4",
            "1.2.3.5",
            "https://www.moonmoon.com/whotripme",
            "HKEY_LOCAL_MACHINE : my-registry-key : REG_DWORD"
        ],
        "submitted": [
            "1.2.3.4",
            "1.2.3.5",
            "https://www.moonmoon.com/whotripme",
            "905ad8176a569a36421bf54c04ba7f95 : a52b6986d68cdfac53aa740566cbeade4452124e : 25bdabd23e349f5e5ea7890795b06d15d842bde1d43135c361e755f748ca05d0",
            "HKEY_LOCAL_MACHINE : my-registry-key : REG_DWORD"
        ]
    }

+ Failed - The Indicator add encountered an error when submitting to the API.
+ Not Saved - The Indicator was not saved either due to a failure or "Halt on Error" was selected and a previous Indicator failed.
+ Saved - The Indicator was saved to ThreatConnect via the API.
+ Submitted - The complete list of submitted Indicator Names.

Indicator to Indicator Associations
-----------------------------------
The :py:meth:`~tcex.tcex_job.TcExJob.association` method accepts the following data structure to create custom, `Indicator to Indicator Associations <https://docs.threatconnect.com/en/latest/rest_api/indicators/indicators.html#indicator-to-indicator-associations>`__. All required fields are highlighted.

.. code-block:: javascript
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2-6

    {
      "association_value": "ASN1234",
      "association_type": tcex.safe_rt("ASN"),
      "resource_value": "1.2.3.4",
      "resource_type": "Address",
      "custom_association_name": "ASN to Address"
    }

The required ``custom_association_name`` key provides the name of the association you would like to use. These names can be found using the `associationTypes <https://docs.threatconnect.com/en/latest/rest_api/associations/associations.html#retrieving-available-associations>`__ API endpoint.

File Occurrence
---------------
The :py:meth:`~tcex.tcex_job.TcExJob.file_occurrence` method accepts the following data structure. All required fields are highlighted.

.. code-block:: javascript
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 4

    {
        "date" : "2014-11-03T00:00:00-05:00",
        "fileName" : "win999301.dll",
        "hash": "BE7DE2F0CF48294400C714C9E28ECD01",
        "path" : "C:\\Windows\\System"
    }

.. Note:: The hash value is not part of the File Occurrence body and will be stripped out before
          the POST.  It is used to indicate which File Indicator to add the occurrence.

Sample Job Flow
---------------
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
          method allows the Group name to be used instead of the Group Id. If the Group Id is
          already known it can be associated using the ``associatedGroup`` field.