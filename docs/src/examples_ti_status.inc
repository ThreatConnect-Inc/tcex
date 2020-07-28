.. _examples_ti_status:

----------------------------
Retrieve Inactive Indicators
----------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.ti.address()
    filters = self.ti.filters()
    filters.add_filter('active', '=', 'false')
    for address in ti.many(filters=filters):
        print(address)

---------------------------------------
Retrieve Active and Inactive Indicators
---------------------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.ti.address()
    filters = self.ti.filters()
    filters.add_filter('active', '=', 'true')
    filters.add_filter('active', '=', 'false')
    parameters = {'orParams': 'true'}
    for address in ti.many(filters=filters, params=parameters):
        print(address)

-------------------------------------------
Retrieve Indicators with Date Added filters
-------------------------------------------
.. code-block:: python
    :linenos:
    :lineno-start: 1

    filters = self.tcex.ti.filters()
    filters.add_filter('dateAdded', '>', '2020-01-01')
    filters.add_filter('dateAdded', '<', '2020-01-02')
    indicators = self.tcex.ti.indicator(owner='example')
    for indicator in indicators.many(filters=filters):
        print(indicator)

---------------------------------------
Retrieve Indicators Owners
---------------------------------------
.. code-block:: python
    :linenos:
    :lineno-start: 1

    # Create a example indicator
    indicator_kwargs = {'ip': '1.1.1.1', 'rating': randint(0, 5), 'confidence': randint(0, 100)}
    indicator = self.ti.indicator('address', self.owner, **indicator_kwargs)
    indicator.create()
    # Get the owners that indicator is in.
    owner = indicator.owners()
    # indicator.owners() return the response, time to get the owner data.
    owner_data = owner.get('data', {}).get('owner', [])
