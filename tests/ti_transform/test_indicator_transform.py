"""Test TI Transforms for indicators."""
# standard library
import json
from pathlib import Path

# third-party
import deepdiff

# first-party
from tcex import TcEx


def transform(tcex: TcEx):
    """Create transform for indicator regression test."""
    return tcex.api.tc.indicator_transform(
        {
            'value1': {'path': 'indicator'},
            'type': {
                'path': 'type',
                'transform': [
                    {
                        'static_map': {
                            'domain': 'Host',
                            'email_address': 'EmailAddress',
                            'email_subject': 'Email Subject',
                            'hash_md5': 'File',
                            'hash_sha1': 'File',
                            'hash_sha256': 'File',
                            'ip_address': 'Address',
                            'ip_address_block': 'CIDR',
                            'mutex_name': 'Mutex',
                            'registry': 'Registry Key',
                            'url': 'URL',
                            'user_agent': 'User Agent',
                        },
                        'kwargs': {},
                    }
                ],
            },
            'confidence': {
                'default': 0,
                'path': 'malicious_confidence',
                'transform': [
                    {
                        'static_map': {'high': 95, 'medium': 75, 'low': 40, 'unverified': 10},
                    }
                ],
            },
            'rating': {
                'default': 0,
                'path': 'malicious_confidence',
                'transform': [
                    {
                        'static_map': {'high': 5, 'medium': 4, 'low': 2, 'unverified': 1},
                    },
                ],
            },
            'associated_groups': [
                {
                    'path': 'actors[].slug',
                    'transform': {
                        'method': lambda a: a,
                        'kwargs': {'ti_type': 'actor'},
                    },
                },
                {
                    'path': 'reports[].slug',
                    'transform': {
                        'method': lambda a: a,
                        'kwargs': {'ti_type': 'report'},
                    },
                },
            ],
            'attributes': [
                {
                    'value': {
                        'path': 'id',
                    },
                    'type': 'External ID',
                },
                {
                    'value': {
                        'path': 'last_update',
                        'transform': {
                            'method': tcex.utils.any_to_datetime,
                        },
                    },
                    'type': 'External Date Last Modified',
                },
                {
                    'value': {
                        'path': 'kill_chains[]',
                        'transform': [
                            {
                                'static_map': {
                                    'actions_and_objectives': 'Actions on Objectives',
                                    'actiononobjectives': 'Actions on Objectives',
                                    'c2': 'C2',
                                    'command_and_control': 'C2',
                                    'delivery': 'Delivery',
                                    'exploitation': 'Exploitation',
                                    'installation': 'Installation',
                                    'reconnaissance': 'Reconnaissance',
                                    'weaponization': 'Weaponization',
                                }
                            },
                        ],
                    },
                    'type': 'Phase of Intrusion',
                },
                {
                    'value': {
                        'path': 'labels[]',
                        'transform': {
                            'method': lambda a: a,
                        },
                    },
                    'type': 'Additional Analysis and Context',
                },
                {
                    'value': {
                        'path': 'created_date',
                        'transform': {
                            'method': tcex.utils.any_to_datetime,
                        },
                    },
                    'type': 'External Date Created',
                },
                {
                    'value': {
                        'path': 'targets[]',
                    },
                    'type': 'Targeted Industry Sector',
                },
            ],
            'date_added': {'path': 'published_date'},
            'last_modified': {'path': 'last_updated'},
            'tags': [
                {
                    'value': {
                        'path': 'domain_types[]',
                        'transform': {
                            'method': lambda values: [f'Domain Type: {v}' for v in values],
                        },
                    },
                },
                {
                    'value': {
                        'path': 'ip_address_types[]',
                        'transform': [
                            {
                                'method': lambda values: [f'Address Type: {v}' for v in values],
                            }
                        ],
                    },
                },
                {
                    'value': {
                        'path': 'labels[]',
                        'transform': [
                            {
                                'method': lambda a: a,
                            }
                        ],
                    },
                },
                {
                    'value': {
                        'path': 'malware_families[]',
                    },
                },
                {
                    'value': {
                        'path': 'targets[]',
                        'transform': [
                            {
                                'method': lambda values: [f'Target: {v}' for v in values],
                            }
                        ],
                    },
                },
                {
                    'value': {
                        'path': 'threat_types[]',
                        'transform': [
                            {
                                'method': lambda values: [f'Threat Type: {v}' for v in values],
                            }
                        ],
                    },
                },
                {
                    'value': {
                        'path': 'vulnerabilities[]',
                    },
                },
            ],
            'xid': {
                'path': 'id',
            },
            'file_occurrences': [
                {
                    'file_name': {
                        'path': "relations[?type == 'filename'].indicator",
                    },
                    'date': {
                        'path': "relations[?type == 'filename'].created_date",
                        'transform': [
                            {'method': lambda a: map(tcex.utils.any_to_datetime, a)},
                            {
                                'method': lambda d: map(
                                    lambda a: a.strftime('%Y-%m-%dT%H:%M:%SZ'), d
                                )
                            },
                        ],
                    },
                }
            ],
        }
    )


def test_indicators_regression(tcex: TcEx):
    """Test large data set to ensure results have not changed."""
    current_path = Path(__file__).parent
    with open(current_path / 'data' / 'input_indicators.json') as input_, open(
        current_path / 'data' / 'transformed_indicators.json'
    ) as output:
        transforms = tcex.api.tc.ti_transforms(json.load(input_), transform(tcex))
        assert not deepdiff.DeepDiff(transforms.batch, json.load(output))
