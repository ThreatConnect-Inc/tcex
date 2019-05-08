.. include:: <isonum.txt>
.. _module_ti:

===========================
Module: Threat Intelligence
===========================

The ThreatConnect TcEx Framework provides the :py:mod:`~tcex.tcex_ti.tcex_ti.TcExTi` module, which creates, deletes, gets, and updates Groups, Indicators, Tasks, and Victims. The Threat Intelligence (TI) module also provides the ability to get Groups, Indicators, and Victims based on Tags, and it provides the ability to get Owners available to the API user in the ThreatConnect platform. The TI module returns a Python Requests Response object when requesting to create, delete, get, or update a single ThreatConnect object, and it yields the ThreatConnect object entity when requesting multiple objects. The Response object has the status code, headers, and body (response.text or response.json()) of the response, while the ThreatConnect object entity format varies depending on the type of object.

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
To retrieve all Groups using a Filter from the ThreatConnect REST API, the Filters can be provided to the ``many()`` method. The calling  ``many()`` method allows pagination over all Groups matching the provided Filter(s).

The example below retrieves all Groups where the name equals ``my_name_filter``.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 1-3

    parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
    groups = self.tcex.ti.group(owner='MyOrg')
    filters = self.tcex.filters()
    filters.add('name', '=', 'my_name_filter')
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

Get Group Metadata
------------------
There are six methods that retrieve metadata for a Group: ``group_associations()``, ``indicator_associations()``, ``attributes()``, ``attributes()``, ``tags()``, and ``labels()``.  This data can also be retrieved in the initial API call by using the ``include`` query parameters.

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
To retrieve all Indicators using a Filter from the ThreatConnect REST API, the Filters can be provided to the ``many()`` method. Calling ``many()`` method allows pagination over all Indicators matching the provided Filter(s).

The example below retrieves all Indicators where name equals ``my_name_filter``.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 1-3

    parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
    indicators = self.tcex.ti.indicator(owner='MyOrg')
    filters = self.tcex.filters()
    filters.add('summary', '=', 'my_name_filter')
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

Get Indicator Metadata
----------------------
There are six methods that retrieve metadata for an Indicator: ``group_associations()``, ``indicator_associations()``, ``attributes()``, ``attributes()``, ``tags()``, and ``labels()``.  This data can also be retrieved in the initial API call by using the ``include`` query parameters.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.indicator(indicator_type='Address', owner='MyOrg', unique_id='1.1.1.1')

    # get group associations
    for association in ti.indicator_associations():
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

    ti = self.tcex.ti.indicator(indicator_type='Address', owner='MyOrg', ip='12.13.14.15')
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

Updating an Indicator
---------------------
Updating an Indicator is similar to creating an Indicator, with the addition of providing the Indicator value.  The Indicator metadata can be updated using the same methods as were used in the Indicator Create example.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.indicator(indicator_type='Address', owner='MyOrg', ip='12.13.14.15')
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
