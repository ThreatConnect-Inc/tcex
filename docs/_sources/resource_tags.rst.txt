.. _resources_tags:

+ Direct Access: ``resource = tcex.resources.Tag(tcex)``
+ Dynamic Access: ``resource = resource = tcex.resource('Tag')``

Retrieve All Tags
=================

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
        resource = tcex.resources.Tag(tcex)
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
        "name": "APT",
        "webLink": "https://api.threatconnect.com/auth/tags/tag.xhtml?tag=APT&owner=Acme+Corp"
    },
    {
        "name": "AutoEnriched",
        "webLink": "https://api.threatconnect.com/auth/tags/tag.xhtml?tag=AutoEnriched&owner=Acme+Corp"
    },
    {
        "name": "China",
        "webLink": "https://api.threatconnect.com/auth/tags/tag.xhtml?tag=China&owner=Acme+Corp"
    },
    {
        "name": "Crimeware",
        "webLink": "https://api.threatconnect.com/auth/tags/tag.xhtml?tag=Crimeware&owner=Acme+Corp"
    }]


Retrieve Specific Tag
=====================

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
        resource = tcex.resources.Tag(tcex)
        resource.owner = 'Acme Corp'
        resource.url = args.tc_api_path
        resource.resource_id('APT')  # Optional

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
        "name": "APT",
        "webLink": "https://api.threatconnect.com/auth/tags/tag.xhtml?tag=APT&owner=Acme+Corp"
    }


Retrieve Filtered Tags
======================

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
        resource = tcex.resource('Tag')
        resource.owner = 'Acme Corp'
        resource.url = args.tc_api_path
        resource.add_filter('name', '=', 'APT')  # Optional

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
        "name": "APT",
        "webLink": "https://api.threatconnect.com/auth/tags/tag.xhtml?tag=APT&owner=Acme+Corp"
    }]
