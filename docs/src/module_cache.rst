.. include:: <isonum.txt>
.. _module_cache:

=============
Module: Cache
=============
The ThreatConnect TcEx App Framework provides a simple interface for caching data in Apps utilizing the ThreatConnect DataStore feature.  The :py:mod:`~tcex.datastore.Cache` module provides an interface to get, add, update, and delete cache data.



DataStore Instance
==================
The ``tcex.cache()`` module provides persistent storage for Apps. The domain value specifies access level for the data as described in the following section.

-------
Domains
-------
* local - limited to the specific App.
* organization - limited to the current Org.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    cache = self.tcex.cache(domain='local', data_type='myDnsData', ttl_seconds='180')

Add Record
==========
The ``add()`` method allows record data to be added. The **rid** (resource id) is an identifier for the provided data.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    cache = self.tcex.cache(domain='local', data_type='myDnsData', ttl_seconds='180')
    response = cache.add(rid='one', data={'one': 1})


Delete Record
=============
The ``delete()`` method allows record data to be deleted using the **rid** (resource id) value.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    cache = self.tcex.cache(domain='local', data_type='myDnsData', ttl_seconds='180')
    response = cache.delete(rid='one')


Get Record
==========
The ``get()`` method allows record data to be retrieved using the **rid** (resource id) value.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    cache = self.tcex.cache(domain='local', data_type='myDnsData', ttl_seconds='180')
    response = cache.get(rid='one', raise_on_error=True)

The ``get()`` method also allows a callback to be provided, which will be called if the cached data is expired to automatically update the cache. In the following example if the cached data is expired the callback method will be called passing the **rid** (resource id).

.. note:: The callback method should return a dict value to be cached.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    def expired_data_callback(rid: str) -> dict:
        """Return dummy data for cache callback."""
        sample_data = {'my_data': {'data': 'updated data to cache'}}
        return sample_data.get(rid)

    cache = self.tcex.cache(domain='local', data_type='myDnsData', ttl_seconds='180')
    response = cache.get(rid='one', data_callback=expired_data_callback, raise_on_error=True)

Update Record
=============
The ``update()`` method allows record data to be updated/overwritten with new data.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    cache = self.tcex.cache(domain='local', data_type='myDnsData', ttl_seconds='180')
    response = cache.update(rid='one', data={'one': 1})
