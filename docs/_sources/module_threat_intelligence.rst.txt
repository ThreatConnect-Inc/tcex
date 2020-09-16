.. include:: <isonum.txt>
.. _module_ti:

===========================
Module: Threat Intelligence
===========================

The ThreatConnect TcEx Framework provides the :py:mod:`~tcex.threat_intelligence.threat_intelligence.ThreatIntelligence` module which provides the following functionality:

* Create - Groups, Indicators, Tasks, and Victims.
* Delete - Groups, Indicators, Tasks, and Victims.
* Get - Groups, Indicators, Tasks, and Victims.
* Update - Groups, Indicators, Tasks, and Victims.
* Get by Tag
* All Create, Get, and Update methods include TI metadata (e.g., attributes, security labels, and tags).

Single Results
==============

When using the create, delete, get, or update methods for a single object the module returns a Python Request Response Object (https://2.python-requests.org/en/v1.1.0/api/#requests.Response). The Python Requests Response object has the following common properties: status_code, headers, response.text, response.content. To get a Python dict from the response the ``response.json()`` method can be used.

Multiple Results
================

When working with multiple objects the modules yields the ThreatConnect object entity as a Python dict. The ThreatConnect entity dict format varies depending on the type and matches the **data** response from the API.

Groups
======

Get Groups by Type
------------------
To retrieve all Groups of a specific type from the ThreatConnect REST API, the group_type can be provided to the ``group()`` method. Once the Group object is initialized, the ``many()`` method allows pagination over all Groups.

The example below retrieves all Groups of type Adversary.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 1-3

    parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
    groups = self.tcex.ti.group(group_type='Adversary', owner='MyOrg')
    for group in groups.many(params=parameters):
        self.tcex.log.debug('group: {}'.format(group))

Get Groups by Tag
------------------
To retrieve all Groups with a specific Tag from the ThreatConnect REST API, the Tag name can be provided to the ``tag()`` method. Once the Tag object is initialized, the ``groups()`` method retrieves all Groups with that Tag and allows pagination over them.

The example below retrieves all Groups with a group of Crimeware.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 1-3

    parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
    tag = self.tcex.ti.tag('Crimeware')
    for group in tag.groups(params=parameters):
        self.tcex.log.debug('group: {}'.format(group))

Get Groups by Filter
--------------------
To retrieve all Groups using a Filter from the ThreatConnect REST API, the `Group Filters <https://docs.threatconnect.com/en/latest/rest_api/groups/retrieve.html#filtering-groups>`_ can be provided to the ``many()`` method. The calling  ``many()`` method allows pagination over all Groups matching the provided Filter(s). The filters added should be the same filter parameters as the REST API expects.

The example below retrieves all Groups where the name equals ``my_name_filter``.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 1-3

    parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
    groups = self.tcex.ti.group(owner='MyOrg')
    filters = self.tcex.ti.filters()
    filters.add_filter('name', '=', 'my_name_filter')
    for group in groups.many(filters=filters, params=parameters):
        self.tcex.log.debug('group: {}'.format(group))

Get Group by ID
---------------
To retrieve a Group from the ThreatConnect REST API, the Group's unique ID is required. Once the Group object is initialized, the ``single`` method will return the Group data from the API.

The example below retrieves a single Adversary with ID 416, if it exists.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 1-3

    parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
    ti = self.tcex.ti.group(group_type='Adversary', owner='MyOrg', unique_id=416)
    response = ti.single(params=parameters)
    group = response.json().get("data", {})

Get Group Metadata
------------------
There are six methods that retrieve metadata for a Group: ``group_associations()``, ``indicator_associations()``, ``victim_asset_associations()``, ``attributes()``, ``tags()``, and ``labels()``.  Attributes, Labels, and Tags can also be retrieved in the initial API call by using the ``include`` query parameters.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.group(group_type='Adversary', owner='MyOrg', unique_id=416)

    # get group associations
    for association in ti.group_associations():
        self.tcex.log.debug('association: {}'.format(association))

    # get indicator associations
    for association in ti.indicator_associations():
        self.tcex.log.debug('association: {}'.format(association))

    # get victim asset associations
    for association in ti.victim_asset_associations():
        self.tcex.log.debug('association: {}'.format(association))

    # get attributes
    for attribute in ti.attributes():
        self.tcex.log.debug('attribute: {}'.format(attribute))

    # get tags
    for tag in ti.tags():
        self.tcex.log.debug('tag: {}'.format(tag))

    # get security labels
    for label in ti.labels():
        self.tcex.log.debug('label: {}'.format(label))

Create a Group
--------------
Creating a Group and adding Associations and metadata constitute separate API calls, and each have their own Response object.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.group(group_type='Campaign', name='camp-3', owner='MyOrg', first_seen='2019-04-02')
    response = ti.create()

    # add associations
    group_assoc = self.tcex.ti.group(group_type='Adversary', owner='MyOrg', unique_id=417)
    response = ti.add_association(target=group_assoc)

    # add attributes
    response = ti.add_attribute(attribute_type='Description', attribute_value='Example Description.')

    # add security label
    response = ti.add_label(label='TLP:GREEN')

    # add tag
    response = ti.add_tag(name='Crimeware')

To create a Group, you will need to provide a keyword argument with the each of the required `group fields <https://docs.threatconnect.com/en/latest/rest_api/groups/groups.html#group-fields>`_ for the type of Group you would like to create.

Group Creation Examples
^^^^^^^^^^^^^^^^^^^^^^^

Here are examples creating each Group type:

Adversary:

.. code-block:: python
    :linenos:
    :lineno-start: 1

    group_object = self.tcex.ti.group(group_type='Adversary', name='Adversary 1', owner='MyOrg')
    response = group_object.create()

Campaign:

.. code-block:: python
    :linenos:
    :lineno-start: 1

    group_object = self.tcex.ti.group(group_type='Campaign', name='Campaign 1', owner='MyOrg')
    response = group_object.create()

Document:

.. code-block:: python
    :linenos:
    :lineno-start: 1

    group_object = self.tcex.ti.group(group_type='Document', name='Document 1', owner='MyOrg', file_name='test.txt'))
    response = group_object.create()
    group_object.file_content('This is the content of the document')

Email:

.. code-block:: python
    :linenos:
    :lineno-start: 1

    group_object = self.tcex.ti.group(group_type='Email', name='Email 1', owner='MyOrg', subject='Foo', header='This an email header', body='This is an email body')
    response = group_object.create()

Event:

.. code-block:: python
    :linenos:
    :lineno-start: 1

    group_object = self.tcex.ti.group(group_type='Event', name='Event 1', owner='MyOrg')
    response = group_object.create()

Incident

.. code-block:: python
    :linenos:
    :lineno-start: 1

    group_object = self.tcex.ti.group(group_type='Incident', name='Incident 1', owner='MyOrg')
    response = group_object.create()

Intrusion Set:

.. code-block:: python
    :linenos:
    :lineno-start: 1

    group_object = self.tcex.ti.group(group_type='Intrusion Set' name='Intrusion Set 1', owner='MyOrg')
    response = group_object.create()

Report:

.. code-block:: python
    :linenos:
    :lineno-start: 1

    group_object = self.tcex.ti.group(group_type='Report', name='Report 1', owner='MyOrg', file_name='report.html')
    response = group_object.create()
    group_object.file_content('<h1>New report</h1>\nReport contents here...')

Signature:

.. code-block:: python
    :linenos:
    :lineno-start: 1

    signature_text = '''rule silent_banker : banker
    {
        meta:
            description = "This is just an example"
            threat_level = 3
            in_the_wild = true
        strings:
            $a = {6A 40 68 00 30 00 00 6A 14 8D 91}
            $b = {8D 4D B0 2B C1 83 C0 27 99 6A 4E 59 F7 F9}
            $c = "UVODFRYSIHLNWPEJXQZAKCBGMT"
        condition:
            $a or $b or $c
    }'''
    group_object = self.tcex.ti.group(group_type='Signature', name='s1', owner=OWNER, fileName='sig.yara', fileType='YARA', file_text=signature_text)
    response = group_object.create()

Threat:

.. code-block:: python
    :linenos:
    :lineno-start: 1

    group_object = self.tcex.ti.group(group_type='Threat', name='Threat 1', owner='MyOrg')
    response = group_object.create()

Updating a Group
----------------
Updating a Group is similar to creating a Group, with the addition of providing the Group ID.  The Group metadata can be updated using the same methods as were used in the Group Create example.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.group(group_type='Campaign', name='camp-3', owner='MyOrg', first_seen='2019-04-02', unique_id=4127)
    response = ti.update()

Delete a Group
--------------
Deleting a Group is similar to creating a Group, with the addition of providing the Group ID.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.group(group_type='Campaign', unique_id=4127)
    response = ti.delete()

Indicators
==========

Get Indicator by Type
---------------------
To retrieve all Indicators of a specific type from the ThreatConnect REST API, the Indicator_type can be provided to the ``indicator()`` method. Once the Indicator object is initialized, the ``many()`` method allows pagination over all Indicators.

The example below retrieves all Indicators of type Address.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 1-3

    parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
    indicators = self.tcex.ti.indicator(indicator_type='Address', owner='MyOrg')
    for indicator in indicators.many(params=parameters):
        self.tcex.log.debug('indicator: {}'.format(indicator))

Get Indicators by Tag
---------------------
To retrieve all Indicators with a specific Tag from the ThreatConnect REST API, the tag name can be provided to the ``tag()`` method. Once the Tag object is initialized, the ``indicators()`` method retrieves all Indicators with the Tag and allows pagination over them.

The example below retrieves all indicators with a tag of Crimeware.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 1-3

    parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
    tag = self.tcex.ti.tag('Crimeware')
    for indicator in tag.indicators(params=parameters):
        self.tcex.log.debug('indicator: {}'.format(indicator))

Get Indicators by Filter
------------------------
To retrieve all Indicators using a Filter from the ThreatConnect REST API, the `Indicator Filters <https://docs.threatconnect.com/en/latest/rest_api/indicators/indicators.html#filtering-indicators>`_ can be provided to the ``many()`` method. Calling ``many()`` method allows pagination over all Indicators matching the provided Filter(s). The filters added should be the same filter parameters as the REST API expects.

The example below retrieves all Indicators where name equals ``my_name_filter``.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 1-3

    parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
    indicators = self.tcex.ti.indicator(owner='MyOrg')
    filters = self.tcex.ti.filters()
    filters.add_filter('summary', '=', 'my_name_filter')
    for indicator in indicators.many(filters=filters, params=parameters):
        self.tcex.log.debug('indicator: {}'.format(indicator))

Get Indicator by Value
----------------------
To retrieve an Indicators from the ThreatConnect REST API, the Indicator's unique Value and Owner are required. Once the Indicator object is initialized, the ``single`` method will return the Indicator data from the API.

The example below retrieves a single Address with Value 1.1.1.1, if it exists.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 1-3

    parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
    ti = self.tcex.ti.indicator(indicator_type='Address', owner='MyOrg', unique_id='1.1.1.1')
    response = ti.single(params=parameters)
    indicator = response.json().get("data", {})

Get Indicator Metadata
----------------------
There are six methods that retrieve metadata for an Indicator: ``group_associations()``, ``indicator_associations()``, ``attributes()``, ``tags()``, and ``labels()``.  Attributes, Labels, and Tags can also be retrieved in the initial API call by using the ``include`` query parameters.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.indicator(indicator_type='Address', owner='MyOrg', unique_id='1.1.1.1')

    # get group associations
    for association in ti.group_associations():
        self.tcex.log.debug('association: {}'.format(association))

    # get indicator associations
    for association in ti.indicator_associations():
        self.tcex.log.debug('association: {}'.format(association))

    # get attributes
    for attribute in ti.attributes():
        self.tcex.log.debug('attribute: {}'.format(attribute))

    # get tags
    for tag in ti.tags():
        self.tcex.log.debug('tag: {}'.format(tag))

    # get security labels
    for label in ti.labels():
        self.tcex.log.debug('label: {}'.format(label))

Create an Indicator
-------------------
Creating an Indicator and adding Associations and metadata are all separate API calls, and each have their own Response object.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.indicator(indicator_type='Host', owner='MyOrg', hostname='example.com')
    response = ti.create()

    # add associations
    group_assoc = self.tcex.ti.group(group_type='Adversary', owner='MyOrg', unique_id=417)
    response = ti.add_association(target=group_assoc)

    # add attributes
    response = ti.add_attribute(attribute_type='Description', attribute_value='Example Description.')

    # add security label
    response = ti.add_label(label='TLP:GREEN')

    # add tag
    response = ti.add_tag(name='Crimeware')

To create an Indicator, you will need to provide a keyword argument with each of the required `indicator fields <https://docs.threatconnect.com/en/latest/rest_api/indicators/indicators.html#indicator-fields>`_ for the type of Indicator you would like to create.

Indicator Creation Examples
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here are examples creating the five, basic Indicator types:

Address:

.. code-block:: python
    :linenos:
    :lineno-start: 1

    indicator_object = self.tcex.ti.indicator(indicator_type='Address', owner='MyOrg', ip='4.3.2.1')
    response = indicator_object.create()

Email Address:

.. code-block:: python
    :linenos:
    :lineno-start: 1

    indicator_object = self.tcex.ti.indicator(indicator_type='EmailAddress', owner='MyOrg', address='foo@example.org')
    response = indicator_object.create()

File:

.. code-block:: python
    :linenos:
    :lineno-start: 1

    # creation args for file indicators - at least one hash type required
    indicator_object = self.tcex.ti.indicator(indicator_type='File', owner='MyOrg', md5='a'*32, sha1="a"*40, sha256="a"*64, size=512)
    response = indicator_object.create()

Host:

.. code-block:: python
    :linenos:
    :lineno-start: 1

    indicator_object = self.tcex.ti.indicator(indicator_type='Host', owner='MyOrg', hostName='example.org')
    response = indicator_object.create()

URL:

.. code-block:: python
    :linenos:
    :lineno-start: 1

    # tcex 2.0.x uses `text` for url keyword, previous versions used `url`
    if tcex.__version__ < "2.0":
        indicator_object = self.tcex.ti.indicator(indicator_type='URL', owner='MyOrg', url='https://example.org/foo')
    else:
        indicator_object = self.tcex.ti.indicator(indicator_type='URL', owner='MyOrg', text='https://example.org/foo')

    response = indicator_object.create()

Updating an Indicator
---------------------
Updating an Indicator is similar to creating an Indicator, with the addition of providing the Indicator value.  The Indicator metadata can be updated using the same methods as were used in the Indicator Create example.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.indicator(indicator_type='Host', owner='MyOrg', hostname='example.com', dns_active=True, whois_active=True, active=True)
    response = ti.update()

Delete an Indicator
-------------------
Deleting an indicator is similar to creating an Indicator, with the addition of providing the Indicator value.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.indicator(indicator_type='Address', owner='MyOrg', ip='12.13.14.15')
    response = ti.delete()

Owners
======

Get Available Owners
--------------------
To retrieve all Owners available from the ThreatConnect REST API, the ``owner`` object can be used. The calling ``many()`` method allows pagination over all Owners available.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.owner()
    for owner in ti.many():
        self.tcex.log.debug('owner: {}'.format(owner))

Get My Owners
-------------
To retrieve all Owners that are currently owned from the ThreatConnect REST API, the ``owner`` object can be used. The calling ``mine()`` method allows pagination over all Owners available.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.owner()
    for owner in ti.mine():
        self.tcex.log.debug('owner: {}'.format(owner))

Get My Members
-------------------
To retrieve all Members currently in Owners that are owned from the ThreatConnect REST API, the ``owner`` object can be used. The calling ``members()`` method allows pagination over all Members available.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.owner()
    for member in ti.members():
        self.tcex.log.debug('member: {}'.format(member))

Get Metrics
-------------------
To retrieve all Metrics from the ThreatConnect REST API, the ``owner`` object can be used. The calling ``metrics()`` method allows pagination over all Metrics available.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.owner()
    for metric in ti.metrics():
        self.tcex.log.debug('metric: {}'.format(metric))
