"""TestIndicatorTransform for TcEx API TC TI Transform Module Testing.

This module contains comprehensive test cases for the TcEx API TC TI Transform Module,
specifically testing indicator transform functionality including regression testing,
file occurrence transforms, attribute transforms, and proper configuration behavior
across different data formats and validation scenarios for ThreatConnect indicator
transformation and processing.

Classes:
    TestIndicatorTransform: Test class for TcEx API TC TI Transform Module functionality

TcEx Module Tested: api.tc.ti_transform
"""


import json
from pathlib import Path
from typing import Any


import deepdiff


from tcex import TcEx
from tcex.api.tc.ti_transform.model.transform_model import IndicatorTransformModel


class TestIndicatorTransform:
    """TestIndicatorTransform for TcEx API TC TI Transform Module Testing.

    This class provides comprehensive testing for the TcEx API TC TI Transform Module,
    covering various indicator transform scenarios including regression testing,
    file occurrence transforms, attribute transforms, and proper configuration
    behavior for ThreatConnect indicator transformation and processing.
    """

    def transform(self, tcex: TcEx) -> IndicatorTransformModel:
        """Create transform for indicator regression test.

        This method creates a comprehensive indicator transform configuration
        for testing various transformation scenarios including type mapping,
        confidence and rating transforms, associated groups, attributes,
        and file occurrences.

        Parameters:
            tcex: The TcEx instance for API access

        Returns:
            IndicatorTransformModel: Configured transform model for testing
        """
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
                        'value': {
                            'path': 'actors[].slug',
                            'transform': {
                                'for_each': str,
                                'kwargs': {'ti_type': 'actor'},
                            },
                        }
                    },
                    {
                        'value': {
                            'path': 'reports[].slug',
                            'transform': {
                                'for_each': str,
                                'kwargs': {'ti_type': 'report'},
                            },
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
                                'method': tcex.util.any_to_datetime,
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
                                'for_each': str,
                            },
                        },
                        'type': 'Additional Analysis and Context',
                    },
                    {
                        'value': {
                            'path': 'created_date',
                            'transform': {
                                'method': tcex.util.any_to_datetime,
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
                                'for_each': lambda v: f'Domain Type: {v}',
                            },
                        },
                    },
                    {
                        'value': {
                            'path': 'ip_address_types[]',
                            'transform': [
                                {
                                    'for_each': 'Address Type: {}'.format,
                                }
                            ],
                        },
                    },
                    {
                        'value': {
                            'path': 'labels[]',
                            'transform': [
                                {
                                    'for_each': str,
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
                                    'for_each': 'Target: {}'.format,
                                }
                            ],
                        },
                    },
                    {
                        'value': {
                            'path': 'threat_types[]',
                            'transform': [
                                {
                                    'for_each': 'Threat Type: {}'.format,
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
                            'path': "relations[?type == 'filename'] | null_leaf(@, 'indicator')",
                        },
                        'date': {
                            'path': "relations[?type == 'filename'] | null_leaf(@, 'created_date')",
                            'transform': [
                                {'for_each': tcex.util.any_to_datetime},
                                {'for_each': lambda d: d.strftime('%Y-%m-%dT%H:%M:%SZ')},
                            ],
                        },
                    }
                ],
            }
        )

    def test_indicators_regression(self, tcex: TcEx) -> None:
        """Test Indicators Regression for TcEx API TC TI Transform Module.

        This test case verifies that the indicator transform functionality
        produces consistent results across large datasets, ensuring that
        regression testing validates transform stability and consistency
        for ThreatConnect indicator processing.

        Parameters:
            tcex: The TcEx instance for API access

        This test validates the regression stability and consistency
        of indicator transform processing across large datasets.
        """
        current_path = Path(__file__).parent
        with (
            (current_path / 'data' / 'input_indicators.json').open() as input_,
            (current_path / 'data' / 'transformed_indicators.json').open() as output,
        ):
            transforms = tcex.api.tc.ti_transforms(json.load(input_), [self.transform(tcex)])
            tcex.log.warning(json.dumps(transforms.batch))
            assert not deepdiff.DeepDiff(transforms.batch, json.load(output)), (
                f'transform results ({transforms.batch}) do not match expected output'
            )

    def test_indicators_file_occurrence(self, tcex: TcEx) -> None:
        """Test Indicators File Occurrence for TcEx API TC TI Transform Module.

        This test case verifies that the file occurrence transform functionality
        works correctly by testing path, date, and file name transformations,
        ensuring proper handling of file occurrence data in indicator transforms.

        Parameters:
            tcex: The TcEx instance for API access

        This test validates the file occurrence transform capabilities
        and data processing for indicator transformation.
        """
        data = [
            {
                'summary': '032AA7E4C76F747BE6ABFC8345FDDBB2FFB591AF',
                'type': 'File',
                'relations': [
                    {'path': '/foo/bar', 'when': 'Jan 12 2002'},
                    {'name': 'bad.exe'},
                    {'path': '/bash/bang'},
                ],
            }
        ]

        def _transform_date(val: Any) -> Any:
            """Transform date value for testing.

            This helper function transforms date values for testing
            file occurrence transform functionality.
            """
            tcex.log.warning(val)
            return val

        transform = tcex.api.tc.indicator_transform(
            {
                'value1': {'path': 'summary'},
                'type': {'path': 'type'},
                'file_occurrences': [
                    {
                        'path': {
                            'path': "relations[] | null_leaf(@, 'path')",
                        },
                        'date': {
                            'path': "relations[] | null_leaf(@, 'when')",
                            'transform': [
                                {'for_each': tcex.util.any_to_datetime},
                                {
                                    'for_each': lambda d: d.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                },
                            ],
                        },
                        'file_name': {
                            'path': "relations[] | null_leaf(@, 'name')",
                        },
                    }
                ],
            }
        )

        transforms = tcex.api.tc.ti_transforms(data, [transform])

        expected_result = {
            'group': [],
            'indicator': [
                {
                    'fileOccurrence': [
                        {'path': '/foo/bar', 'date': '2002-01-12T00:00:00Z'},
                        {'fileName': 'bad.exe'},
                        {'path': '/bash/bang'},
                    ],
                    'summary': '032AA7E4C76F747BE6ABFC8345FDDBB2FFB591AF',
                    'type': 'File',
                }
            ],
        }

        assert not deepdiff.DeepDiff(transforms.batch, expected_result), (
            f'transform results ({transforms.batch}) do not match expected ({expected_result})'
        )

    def test_indicators_attributes(self, tcex: TcEx) -> None:
        """Test Indicators Attributes for TcEx API TC TI Transform Module.

        This test case verifies that the attribute transform functionality
        works correctly by testing type and value transformations,
        ensuring proper handling of attribute data in indicator transforms.

        Parameters:
            tcex: The TcEx instance for API access

        This test validates the attribute transform capabilities
        and data processing for indicator transformation.
        """
        data = [
            {
                'summary': '032AA7E4C76F747BE6ABFC8345FDDBB2FFB591AF',
                'type': 'File',
                'attributes': {
                    'data': [
                        {
                            'type': 'Description',
                            'value': 'Imported from bad list',
                        },
                        {
                            'type': 'Foo',
                            'value': 'Bar',
                        },
                    ]
                },
            }
        ]

        def _transform_date(val: Any) -> Any:
            """Transform date value for testing.

            This helper function transforms date values for testing
            attribute transform functionality.
            """
            tcex.log.warning(val)
            return val

        transform = tcex.api.tc.indicator_transform(
            {
                'value1': {'path': 'summary'},
                'type': {'path': 'type'},
                'attributes': [
                    {
                        'type': {
                            'path': "attributes.data[] | null_leaf(@, 'type')",
                        },
                        'value': {
                            'path': "attributes.data[] | null_leaf(@, 'type')",
                        },
                    }
                ],
            }
        )

        transforms = tcex.api.tc.ti_transforms(data, [transform])

        tcex.log.warning(transforms.batch)

        expected_result = {
            'group': [],
            'indicator': [
                {
                    'attribute': [
                        {'type': 'Description', 'value': 'Description'},
                        {'type': 'Foo', 'value': 'Foo'},
                    ],
                    'summary': '032AA7E4C76F747BE6ABFC8345FDDBB2FFB591AF',
                    'type': 'File',
                }
            ],
        }

        assert not deepdiff.DeepDiff(transforms.batch, expected_result), (
            f'transform results ({transforms.batch}) do not match expected ({expected_result})'
        )
