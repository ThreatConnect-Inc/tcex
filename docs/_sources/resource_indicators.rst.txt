.. _resources_indicators:

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| Indicator Direct       | resource = tcex.resources.Indicator(tcex)                |
+------------------------+----------------------------------------------------------+
| Indicator Dynamic      | resource = tcex.resource('Indicator')                    |
+------------------------+----------------------------------------------------------+
| Address Direct         | resource = tcex.resources.Address(tcex)                  |
+------------------------+----------------------------------------------------------+
| Address Dynamic        | resource =  tcex.resource('Address')                     |
+------------------------+----------------------------------------------------------+
| EmailAddress Direct    | resource = tcex.resources.EmailAddress(tcex)             |
+------------------------+----------------------------------------------------------+
| EmailAddress Dynamic   | resource = tcex.resource('EmailAddress')                 |
+------------------------+----------------------------------------------------------+
| File Direct            | resource = tcex.resources.File(tcex)                     |
+------------------------+----------------------------------------------------------+
| File Dynamic           | resource = tcex.resource('File')                         |
+------------------------+----------------------------------------------------------+
| Host Direct            | resource = tcex.resources.Host(tcex)                     |
+------------------------+----------------------------------------------------------+
| Host Dynamic           | resource = tcex.resource('Host')                         |
+------------------------+----------------------------------------------------------+
| URL Direct             | resource = tcex.resources.URL(tcex)                      |
+------------------------+----------------------------------------------------------+
| URL Dynamic            | resource = tcex.resource('URL')                          |
+------------------------+----------------------------------------------------------+

.. Note:: Custom Indicator types can only be accessed via the Dynamic method.

Retrieve All Indicators
=======================

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
        resource = tcex.resources.Indicator(tcex)
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
        "rating": 5.0,
        "confidence": 100,
        "dateAdded": "2017-02-23T20:23:59Z",
        "description": "Create via Playbook",
        "threatAssessConfidence": 100.0,
        "lastModified": "2017-03-02T19:05:03Z",
        "threatAssessRating": 5.0,
        "webLink": "https://app.threatconnect.com/auth/indicators/details/address.xhtml?address=1.1.1.4&owner=Acme+Corp",
        "summary": "1.1.1.4",
        "ownerName": "Acme Corp",
        "type": "Address",
        "id": 632128
    },
    {
        "rating": 5.0,
        "confidence": 100,
        "dateAdded": "2017-02-21T16:52:15Z",
        "description": "Test Description #5",
        "threatAssessConfidence": 77.5,
        "lastModified": "2017-02-21T00:00:00Z",
        "threatAssessRating": 5.0,
        "webLink": "https://app.threatconnect.com/auth/indicators/details/customIndicator.xhtml?id=603903&owner=Acme+Corp",
        "summary": "HKEY_LOCAL_MACHINE : my-registry-key : REG_DWORD",
        "ownerName": "Acme Corp",
        "type": "Registry Key",
        "id": 603903
    },
    <... snipped>
    ]


Retrieve Specific Indicator
===========================

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
        resource = tcex.resource('Address')
        resource.owner = 'Acme Corp'
        resource.url = args.tc_api_path
        resource.resource_id('1.1.1.4')  # Optional

        results = resource.request()
        print(json.dumps(results.get('data'), indent=4))

    if __name__ == "__main__":
        main()

Response
--------

.. code-block:: javascript
    :linenos:
    :lineno-start: 1

    {
        "rating": 5.0,
        "confidence": 100,
        "dateAdded": "2017-02-23T20:23:59Z",
        "description": "Create via Playbook",
        "threatAssessConfidence": 100.0,
        "lastModified": "2017-03-02T19:05:03Z",
        "threatAssessRating": 5.0,
        "webLink": "https://app.threatconnect.com/auth/indicators/details/address.xhtml?address=1.1.1.4&owner=Acme+Corp",
        "ip": "1.1.1.4",
        "owner": {
            "type": "Organization",
            "id": 2,
            "name": "Acme Corp"
        },
        "id": 632128
    }

Retrieve Filtered Indicators
============================

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 14,17-18,20

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
        resource = tcex.resource('Indicator')
        resource.owner = 'Acme Corp'
        resource.url = args.tc_api_path
        resource.add_filter('rating', '>', 1)
        resource.add_filter('confidence', '>', 50)

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
        "rating": 5.0,
        "confidence": 100,
        "dateAdded": "2017-02-23T20:23:59Z",
        "description": "Create via Playbook",
        "threatAssessConfidence": 100.0,
        "lastModified": "2017-03-02T19:05:03Z",
        "threatAssessRating": 5.0,
        "webLink": "https://app.threatconnect.com/auth/indicators/details/address.xhtml?address=1.1.1.4&owner=Acme+Corp",
        "summary": "1.1.1.4",
        "ownerName": "Acme Corp",
        "type": "Address",
        "id": 632128
    },
    {
        "rating": 5.0,
        "confidence": 100,
        "dateAdded": "2017-02-21T16:52:15Z",
        "description": "Test Description #5",
        "threatAssessConfidence": 77.5,
        "lastModified": "2017-02-21T00:00:00Z",
        "threatAssessRating": 5.0,
        "webLink": "https://app.threatconnect.com/auth/indicators/details/customIndicator.xhtml?id=603903&owner=Acme+Corp",
        "summary": "HKEY_LOCAL_MACHINE : my-registry-key : REG_DWORD",
        "ownerName": "Acme Corp",
        "type": "Registry Key",
        "id": 603903
    },
    <... snipped>
    ]

Indicator Associations
======================

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 14,17-18,20

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
        resource = tcex.resource('Indicator')
        resource.owner = 'Acme Corp'
        resource.url = args.tc_api_path
        resource.add_filter('rating', '>', 1)
        resource.add_filter('confidence', '>', 50)

        for results in resource:  # pagination
            if results.get('status') == 'Success':
                for indicator_data in results.get('data', []):
                    print(indicator_data.get('summary'))

                    iocs = [x for x in resource.indicators(i)]  # get all iocs if more than 1
                    ioc = iocs[0].get('value')  # only need the first one

                    # Get new Resource Object of Indicator Type
                    i_resource = tcex.resource(indicator_data.get('type'))
                    i_resource.resource_id(ioc)  # set resource ID

                    ar = tcex.resource('Adversary')  # Get Adversaries Instance
                    associations_resource = i_resource.associations(ar)
                    associations_results = associations_resource.request()
                    print(json.dumps(associations_results.get('data', []), indent=4))

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
        "rating": 5.0,
        "confidence": 100,
        "dateAdded": "2017-02-23T20:23:59Z",
        "description": "Create via Playbook",
        "threatAssessConfidence": 100.0,
        "lastModified": "2017-03-02T19:05:03Z",
        "threatAssessRating": 5.0,
        "webLink": "https://app.threatconnect.com/auth/indicators/details/address.xhtml?address=1.1.1.4&owner=Acme+Corp",
        "summary": "1.1.1.4",
        "ownerName": "Acme Corp",
        "type": "Address",
        "id": 632128
    },
    {
        "rating": 5.0,
        "confidence": 100,
        "dateAdded": "2017-02-21T16:52:15Z",
        "description": "Test Description #5",
        "threatAssessConfidence": 77.5,
        "lastModified": "2017-02-21T00:00:00Z",
        "threatAssessRating": 5.0,
        "webLink": "https://app.threatconnect.com/auth/indicators/details/customIndicator.xhtml?id=603903&owner=Acme+Corp",
        "summary": "HKEY_LOCAL_MACHINE : my-registry-key : REG_DWORD",
        "ownerName": "Acme Corp",
        "type": "Registry Key",
        "id": 603903
    },
    <... snipped>
    ]