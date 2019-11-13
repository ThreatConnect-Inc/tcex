.. include:: <isonum.txt>
.. _module_datastore:

=================
Module: Datastore
=================
The ThreatConnect TcEx App Framework provides a simple interface for interacting with the ThreatConnect DataStore feature in Apps.  The :py:mod:`~tcex.datastore.Datastore` module provides an interface to get, add, put, and delete data from the Datastore.



DataStore Instance
==================
The ``tcex.datastore()`` module provides persistent storage for Apps. The domain value specifies access level for the data as described in the following section.

-------
Domains
-------
* local - limited to the specific App.
* organization - limited to the current Org.
* system - available to the entire TC instance.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ds = self.tcex.datastore('local', 'myDnsData')

Add Record
==========
The ``add()`` or ``post()`` method allows record data to be added/created. The **rid** (resource id) is an optional identifier for the provided data. If left null a identifier will automatically be created and returned in the response.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ds = self.tcex.datastore('local', 'myNumbers')
    response = ds.add(rid='one', data={'one': 1})


Delete Record
=============
The ``delete()`` method allows record data to be deleted using the **rid** (resource id) value.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ds = self.tcex.datastore('local', 'myNumbers')
    response = ds.delete(rid='one')


Get Record
==========
The ``get()`` method allows record data to be retrieved using the **rid** (resource id) value.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ds = self.tcex.datastore('local', 'myNumbers')
    response = ds.get(rid='one')


------
Search
------
The ``get()`` method also allows a search to be performed.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ds = self.tcex.datastore('local', 'myNumbers')
    search = {'query': {'match_all': {}}}
    response = ds.get(rid='_search', data=search)


Update Record
=============
The ``update()`` or ``put()`` method allows record data to be updated/overwritten with new data.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ds = self.tcex.datastore('local', 'myNumbers')
    response = ds.put(rid='one', data={'one': 1})
