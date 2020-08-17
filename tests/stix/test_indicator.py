from tcex.stix.indicator.indicator import Indicator


class TestStixIndicator:

    @staticmethod
    def test_indicator():
        ind = {

            "type": "indicator",

            "spec_version": "2.1",

            "id": "indicator--8e2e2d2b-17d4-4cbf-938f-98ee46b3cd3f",

            "created_by_ref": "identity--f431f809-377b-45e0-aa1c-6a4751cae5ff",

            "created": "2016-04-06T20:03:48.000Z",

            "modified": "2016-04-06T20:03:48.000Z",

            "indicator_types": ["malicious-activity"],

            "name": "Poison Ivy Malware",

            "description": "This file is part of Poison Ivy",

            "pattern": "[ file:hashes.'SHA-256' = '4bac27393bdd9777ce02453256c5577cd02275510b2227f473d03f533924f877' ]",

            "valid_from": "2016-01-01T00:00:00Z"

        }
        i = Indicator()

        list(i.consume(ind))

    @staticmethod
    def test_indicator2():
        ind = {

            "type": "indicator",

            "spec_version": "2.1",

            "id": "indicator--8e2e2d2b-17d4-4cbf-938f-98ee46b3cd3f",

            "created_by_ref": "identity--f431f809-377b-45e0-aa1c-6a4751cae5ff",

            "created": "2016-04-06T20:03:48.000Z",

            "modified": "2016-04-06T20:03:48.000Z",

            "indicator_types": ["malicious-activity"],

            "name": "Poison Ivy Malware",

            "description": "This file is part of Poison Ivy",

            "pattern": """(
                  [ipv4-addr:value = '198.51.100.1/32' OR
                   ipv4-addr:value = '203.0.113.33/32' OR
                   ipv6-addr:value = '2001:0db8:dead:beef:dead:beef:dead:0001/128']
                
                  FOLLOWEDBY [
                    domain-name:value = 'example.com']
                
                ) WITHIN 600 SECONDS
                """,

            "valid_from": "2016-01-01T00:00:00Z"

        }
        i = Indicator()

        l = list(i.consume(ind))
        print(l)

    @staticmethod
    def test_indicator3():
        ind = {

            "type": "indicator",

            "spec_version": "2.1",

            "id": "indicator--8e2e2d2b-17d4-4cbf-938f-98ee46b3cd3f",

            "created_by_ref": "identity--f431f809-377b-45e0-aa1c-6a4751cae5ff",

            "created": "2016-04-06T20:03:48.000Z",

            "modified": "2016-04-06T20:03:48.000Z",

            "indicator_types": ["malicious-activity"],

            "name": "Poison Ivy Malware",

            "description": "This file is part of Poison Ivy",

            "pattern": """
                [ file:hashes.'SHA-256' = '4bac27393bdd9777ce02453256c5577cd02275510b2227f473d03f533924f877' 
                OR file:hashes.'SHA-1' = '2fd4e1c67a2d28fced849ee1bb76e7391b93eb12' 
                OR file:hashes.'MD5' = 'd9729feb74992cc3482b350163a1a010']
            """,

            "valid_from": "2016-01-01T00:00:00Z"

        }
        i = Indicator()

        l = list(i.consume(ind))
        print(l)