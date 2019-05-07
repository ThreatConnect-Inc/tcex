.. include:: <isonum.txt>
.. _module_ti:

===========================
Module: Threat Intelligence
===========================

The ThreatConnect TcEx Framework provides the :py:mod:`~tcex.tcex_ti.TcExTi` module to create, delete, get and update Groups, Indicators, Tasks, and Victims, provides the ability to get Groups, Indicators, and Victims based on Tags, and provides the ability to get Owners available to the api user in the ThreatConnect platform. The TI module returns a Python Requests Response object when requesting to create/delete/get/update a single ThreatConnect objects, and yields the ThreatConnect object entity when requesting multiple objects. The Response object has the status code, headers, and body (response.text or response.json()) of the response, while the ThreatConnect object entity format will vary depending on the type of object.

Groups
======


Get Groups by Type
------------------
To retrieve all group of a specific type from the ThreatConnect REST API the group_type can be provided to the ``group()`` method. Once the group object is initialized the ``many()`` method allows pagination over all groups.

The example below retrieves all groups of type Adversary.

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
To retrieve all group with a specific Tag from the ThreatConnect REST API the tag name can be provided to the ``tag()`` method. Once the tag object is initialized the ``groups()`` method retrieves all groups with the tag and allows pagination them.

The example below retrieves all groups of type Adversary.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 1-3
    
    parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
    tag = self.tcex.ti.tag('group_tag')
    for group in tag.groups(params=parameters):
        self.tcex.log.debug('group: {}'.format(group))

Get Groups by Filter
------------------
To retrieve all group of a using a filter from the ThreatConnect REST API the filters can be provided to the ``many()`` method. Calling ``many()`` method allows pagination over all groups matching the provided filter(s).

The example below retrieves all groups where name equals ``my_name_filter``.

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

Get Group by Id
---------------
To retrieve a group from the ThreatConnect REST API the group unique id is required. Once the group object is initialize the ``single`` method will return the group data from the API.

The example below retrieves a single Adversary with id 416 if it exists.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 1-3

    parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
    ti = self.tcex.ti.group(group_type='Adversary', owner='MyOrg', unique_id=416)
    response = ti.single(params=parameters)

Get Group Metadata
------------------
There are 6 methods to retrieve metadata for a group: ``group_associations()``, ``indicator_associations()``, ``attributes()``, ``attributes()``, ``tags()``, and ``labels()``.  This data can also be retrieved in the initial API call by using the ``include`` query parameters.

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
Creating a Group, adding association and metadata are all separate API calls and each have their own response object.

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
Updating a group is similar to creating a group with the addition of providing the group Id.  The Group metadata can be updated using the same methods as were used in the Group Create example.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.group(group_type='Campaign', name='camp-3', owner='MyOrg', first_seen='2019-04-02', unique_id=4127)
    response = ti.update()

Delete a Group
--------------
Deleting a group is similar to creating a group with the addition of providing the group Id.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.group(group_type='Campaign', unique_id=4127)
    response = ti.delete()

Indicators
==========
There are three interfaces to add Indicator Threat Intelligence data to the Batch Module.

Get Indicator by Type
---------------------
To retrieve all indicators of a specific type from the ThreatConnect REST API the indicator_type can be provided to the ``indicator()`` method. Once the indicator object is initialized the ``many()`` method allows pagination over all indicators.

The example below retrieves all indicators of type Address.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 1-3

    parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
    indicators = self.tcex.ti.indicator(indicator_type='Address', owner='MyOrg')
    for indicator in indicators.many(params=parameters):
        self.tcex.log.debug('indicator: {}'.format(indicator))

Get Indicators by Tag
------------------
To retrieve all group with a specific Tag from the ThreatConnect REST API the tag name can be provided to the ``tag()`` method. Once the tag object is initialized the ``indicators()`` method retrieves all indicators with the tag and allows pagination them.

The example below retrieves all groups of type Adversary.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 1-3
    
    parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
    tag = self.tcex.ti.tag('indicator_tag')
    for indicator in tag.indicators(params=parameters):
        self.tcex.log.debug('indicator: {}'.format(indicator))

Get Indicators by Filter
------------------
To retrieve all group of a using a filter from the ThreatConnect REST API the filters can be provided to the ``many()`` method. Calling ``many()`` method allows pagination over all groups matching the provided filter(s).

The example below retrieves all groups where name equals ``my_name_filter``.

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
To retrieve an indicator from the ThreatConnect REST API the indicator unique value and owner is required. Once the indicator object is initialize the ``single`` method will return the indicator data from the API.

The example below retrieves a single Address with value 1.1.1.1 if it exists.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 1-3

    parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
    ti = self.tcex.ti.indicator(indicator_type='Address', owner='MyOrg', unique_id='1.1.1.1')
    response = ti.single(params=parameters)

Get Indicator Metadata
----------------------
There are 6 methods to retrieve metadata for an indicator: ``group_associations()``, ``indicator_associations()``, ``attributes()``, ``attributes()``, ``tags()``, and ``labels()``.  This data can also be retrieved in the initial API call by using the ``include`` query parameters.

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
Creating an Indicator, adding association and metadata are all separate API calls and each have their own response object.

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
Updating an indicator is similar to creating an indicator with the addition of providing the indicator value.  The Indicator metadata can be updated using the same methods as were used in the Indicator Create example.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.indicator(indicator_type='Address', owner='MyOrg', ip='12.13.14.15')
    response = ti.update()

Delete an Indicator
-------------------
Deleting an indicator is similar to creating a indicator with the addition of providing the indicator value.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.indicator(indicator_type='Address', owner='MyOrg', ip='12.13.14.15')
    response = ti.delete()

Get Available Owners
-------------------
To retrieve all owners available from the ThreatConnect REST API the ``owner`` object can be used. Calling ``many()`` method allows pagination over all owners available.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.owner()
    for owner in ti.many():
        self.tcex.log.debug('owner: {}'.format(owner))

Get My Owners
-------------------
To retrieve all owners you currently own from the ThreatConnect REST API the ``owner`` object can be used. Calling ``mine()`` method allows pagination over all owners available.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.owner()
    for owner in ti.mine():
        self.tcex.log.debug('owner: {}'.format(owner))

Get My Members
-------------------
To retrieve all members currently in owners you own from the ThreatConnect REST API the ``owner`` object can be used. Calling ``members()`` method allows pagination over all members available.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.owner()
    for member in ti.members():
        self.tcex.log.debug('member: {}'.format(member))

Get Metrics
-------------------
To retrieve all metrics from the ThreatConnect REST API the ``owner`` object can be used. Calling ``metrics()`` method allows pagination over all metrics available.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.owner()
    for metric in ti.metrics():
        self.tcex.log.debug('metric: {}'.format(metric))
