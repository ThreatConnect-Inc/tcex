.. _resources_data_store:

+ Direct Access: ``resource = tcex.resources.DataStore(tcex)``
+ Dynamic Access: ``resource = tcex.resource('DataStore')``

Create Entry
============

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 12-14

    import json
    from datetime import datetime

    from tcex import TcEx

    tcex = TcEx()
    args = tcex.args


    def main():
        """ """
        resource = tcex.resources.DataStore(tcex)
        body = {'one': 1}
        results = resource.create('local', 'tcex', 1, json.dumps(body))
        print(json.dumps(results.get('data'), indent=4))


    if __name__ == "__main__":
        main()

Response
--------

.. code-block:: javascript
    :linenos:
    :lineno-start: 1

    {
        "_type": "24$tcex",
        "created": true,
        "_shards": {
            "successful": 1,
            "failed": 0,
            "total": 2
        },
        "_version": 1,
        "_index": "$local",
        "_id": "1"
    }

Read Entry
==========

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 12-13

    import json
    from datetime import datetime

    from tcex import TcEx

    tcex = TcEx()
    args = tcex.args


    def main():
        """ """
        resource = tcex.resources.DataStore(tcex)
        results = resource.read('local', 'tcex', 1)
        print(json.dumps(results.get('data'), indent=4))


    if __name__ == "__main__":
        main()

Response
--------

.. code-block:: javascript
    :linenos:
    :lineno-start: 1

    {
        "_type": "24$tcex",
        "_source": {
            "one": 1
        },
        "_index": "$local",
        "_version": 1,
        "found": true,
        "_id": "1"
    }

Update Entry
============

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 12-14

    import json
    from datetime import datetime

    from tcex import TcEx

    tcex = TcEx()
    args = tcex.args


    def main():
        """ """
        resource = tcex.resources.DataStore(tcex)
        body = {'one': 1, 'two', 2}
        results = resource.update('local', 'tcex', 1, json.dumps(body))
        print(json.dumps(results.get('data'), indent=4))


    if __name__ == "__main__":
        main()

Response
--------

.. code-block:: javascript
    :linenos:
    :lineno-start: 1

    {
        "_type": "24$tcex",
        "created": false,
        "_shards": {
            "successful": 1,
            "failed": 0,
            "total": 2
        },
        "_version": 2,
        "_index": "$local",
        "_id": "1"
    }

Delete Entry
============

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 12-13

    import json
    from datetime import datetime

    from tcex import TcEx

    tcex = TcEx()
    args = tcex.args


    def main():
        """ """
        resource = tcex.resources.DataStore(tcex)
        results = resource.delete('local', 'tcex', 1)
        print(json.dumps(results.get('data'), indent=4))


    if __name__ == "__main__":
        main()

Response
--------

.. code-block:: javascript
    :linenos:
    :lineno-start: 1

    {
        "_type": "24$tcex",
        "_shards": {
            "successful": 1,
            "failed": 0,
            "total": 2
        },
        "_index": "$local",
        "_version": 3,
        "found": true,
        "_id": "1"
    }