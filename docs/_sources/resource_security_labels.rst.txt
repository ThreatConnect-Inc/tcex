.. _resources_security_labels:


+ Direct Access: ``resource = tcex.resources.SecurityLabel(tcex)``
+ Dynamic Access: ``resource = tcex.resource('SecurityLabel')``

Retrieve All Security Labels
============================

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 14,18

    """ standard """
    import json
    from datetime import datetime
    """ third party """
    """ custom """
    from tcex import TcEx

    tcex = TcEx()
    args = tcex.args


    def main():
        """ """
        resource = tcex.resources.SecurityLabel(tcex)
        resource.owner = 'Acme Corp'
        resource.url = args.tc_api_path

        for results in resource:  # pagination
            if results.get('status') == 'Success':
                print(json.dumps(results.get('data', []), indent=4))
            else:
                warn = 'Failed retrieving result during pagination.'
                tcex.log.error(warn)


        if __name__ == "__main__":
            main()

Response
--------

.. code-block:: javascript
    :linenos:
    :lineno-start: 1

    [{
        "dateAdded": "2017-01-04T20:07:00Z",
        "name": "TLP Green",
        "description": "TLP Green"
    },
    {
        "dateAdded": "2016-12-05T23:00:05Z",
        "name": "TLP Red",
        "description": "TLP Red"
    }]

Retrieve Specific Security Label
================================

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 14,17,19

    """ standard """
    import json
    from datetime import datetime
    """ third party """
    """ custom """
    from tcex import TcEx

    tcex = TcEx()
    args = tcex.args


    def main():
        """ """
        resource = tcex.resources.SecurityLabel(tcex)
        resource.owner = 'Acme Corp'
        resource.url = args.tc_api_path
        resource.resource_id('TLP Green')  # Optional

        results = resource.request()
        print(json.dumps(results.get('data', []), indent=4))


    if __name__ == "__main__":
        main()

Response
--------

.. code-block:: javascript
    :linenos:
    :lineno-start: 1

    {
        "dateAdded": "2017-01-04T20:07:00Z",
        "name": "TLP Green",
        "description": "TLP Green"
    }


Retrieve Filtered Security Labels
=================================

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 14,17,19

    """ standard """
    import json
    from datetime import datetime
    """ third party """
    """ custom """
    from tcex import TcEx

    tcex = TcEx()
    args = tcex.args


    def main():
        """ """
        resource = tcex.resource('SecurityLabel')
        resource.owner = 'Acme Corp'
        resource.url = args.tc_api_path
        resource.add_filter('name', '^', 'TLP')  # Optional

        for results in resource:  # pagination
            if results.get('status') == 'Success':
                print(json.dumps(results.get('data'), indent=4))
            else:
                warn = 'Failed retrieving result during pagination.'
                tcex.log.error(warn)


        if __name__ == "__main__":
            main()

Response
--------

.. code-block:: javascript
    :linenos:
    :lineno-start: 1


    [{
        "dateAdded": "2017-01-04T20:07:00Z",
        "name": "TLP Green",
        "description": "TLP Green"
    },
    {
        "dateAdded": "2016-12-05T23:00:05Z",
        "name": "TLP Red",
        "description": "TLP Red"
    }]
