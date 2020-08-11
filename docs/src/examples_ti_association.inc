.. _examples_ti_associations:

----------------------------------------
Create Indicator to Group Association 1
----------------------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1


    # Creating a Indicator and Group to insure that a association can be made.
    indicator_kwargs = {'ip': '1.1.1.1', 'rating': 0, 'confidence': 0 }
    group_kwargs = { 'fileName': 'rand_filename', 'name': 'rand_name' }
    indicator = self.ti.indicator('address', self.owner, **indicator_kwargs)
    group = self.ti.group('document', self.owner, **group_kwargs)
    # Can be done this way as well:
    # indicator = self.ti.address(self.owner, **indicator_kwargs)
    # group = self.ti.document(self.owner, **group_kwargs)
    indicator.create()
    group.create()

    # indicator to associate
    indicator.add_association(group)

----------------------------------------
Create Indicator to Group Association 2
----------------------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1


    # Creating a Indicator and Group to insure that a association can be made.
    indicator_kwargs = {'ip': '1.1.1.1', 'rating': 0, 'confidence': 0 }
    group_kwargs = { 'fileName': 'rand_filename', 'name': 'rand_name' }
    indicator = self.ti.indicator('address', self.owner, **indicator_kwargs)
    group = self.ti.group('document', self.owner, **group_kwargs)
    indicator.create()
    group.create()

    # Create indicators/groups representing the indicators/groups in TC
    indicator = self.ti.indicator('address', self.owner, ip='1.1.1.1')
    group = self.ti.group('document', self.owner, id=group.unique_id)
    # Can be done this way as well:
    # indicator = self.ti.address(self.owner, '1.1.1.1')
    # group = self.ti.document(self.owner, id=group.unique_id)

    # indicator to associate
    indicator.add_association(group)

----------------------------------------
Retrieve Indicator to Group Associations
----------------------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1


    # Creating a Indicator to make sure group associations can be retrieved.
    indicator_kwargs = {'ip': '1.1.1.1', 'rating': 0, 'confidence': 0 }
    indicator = self.ti.address(owner=self.owner, ip='1.1.1.1', 'rating': 0, 'confidence': 0)
    indicator.create()

    for association in indicator.group_associations():
        print(association)


----------------------------------------
Retrieve Group to Indicator Associations
----------------------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1


    # Creating a Indicator to make sure group associations can be retrieved.
    group_kwargs = { 'fileName': 'rand_filename', 'name': 'rand_name' }
    group = self.ti.document(owner=self.owner, **group_kwargs)
    group.create()

    for association in group.indicator_associations():
        print(association)
