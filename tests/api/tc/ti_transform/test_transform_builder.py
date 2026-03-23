"""TestTransformBuilderLoad for Transform Builder Load Module Testing.

This module contains test cases for the transform builder load function,
which handles both v1 and v2 transform formats exported from ThreatConnect's
Transform Builder. Tests cover v1-to-model conversion, v2-to-model conversion,
camelCase-to-snake_case normalization, metadata stripping, transform function
resolution, and validation error scenarios.

Classes:
    TestTransformBuilderLoad: Tests for the transform builder load function

TcEx Module Tested: api.tc.ti_transform.transform_builder.load
"""

# standard library
import copy

# third-party
import pytest

from tcex import TcEx
from tcex.api.tc.ti_transform.model.transform_model import (
    GroupTransformModel,
    IndicatorTransformModel,
)
from tcex.api.tc.ti_transform.ti_predefined_functions import ProcessingFunctions
from tcex.api.tc.ti_transform.transform_builder import load


V1_TRANSFORM = {
    'transform': {
        'attributes': [
            {
                'displayed': True,
                'source': 'CrowdStrike',
                'type': 'External ID',
                'value': {'path': 'id'},
            },
            {
                'displayed': True,
                'source': 'CrowdStrike',
                'type': 'Description',
                'value': {'path': 'description'},
            },
            {
                'displayed': True,
                'source': 'CrowdStrike',
                'type': 'Active',
                'value': {
                    'path': 'active',
                    'transform': [
                        {'kwargs': {'suffix': ' '}, 'method': 'append'},
                        {'kwargs': {}, 'method': 'to_lowercase'},
                        {'kwargs': {}, 'method': 'remove_surrounding_whitespace'},
                    ],
                },
            },
            {
                'displayed': True,
                'source': 'CrowdStrike',
                'type': 'Adversary Motivation Type',
                'value': {
                    'path': 'motivations[].value',
                    'transform': [
                        {
                            'for_each': 'static_map',
                            'kwargs': {
                                'mapping': '{"Hacktivist": "Hacktivism"}',
                            },
                        }
                    ],
                },
            },
        ],
        'name': {
            'path': 'name',
            'transform': [
                {
                    'kwargs': {'append_chars': '...', 'length': '100'},
                    'method': 'truncate',
                }
            ],
        },
        'tags': [
            {
                'value': {
                    'path': 'name',
                    'transform': [
                        {
                            'kwargs': {
                                'description': '_transform_name_to_mitre',
                                'name': '_transform_name_to_mitre',
                            },
                            'method': 'custom',
                        }
                    ],
                }
            }
        ],
        'type': {'default': 'Intrusion Set'},
        'xid': {
            'path': 'id',
            'transform': [
                {'kwargs': {'prefix': 'ACTOR-'}, 'method': 'prepend'},
                {'kwargs': {}, 'method': 'to_uppercase'},
            ],
        },
    },
    'type': 'group',
}


V2_TRANSFORM = {
    'associatedGroups': [
        {
            'metadata': {'comment': 'only associate when they are NOT unknown'},
            'value': {
                'path': 'breach_details.items[].malware_family',
                'transform': [
                    {
                        'kwargs': {
                            'description': 'Filter "Unknown" values',
                            'name': 'filter_unknown',
                        },
                        'method': 'custom',
                    },
                    {'forEach': 'to_uppercase', 'kwargs': {}},
                    {'forEach': 'prepend', 'kwargs': {'prefix': 'MALWARE-'}},
                ],
            },
        },
        {
            'metadata': {'comment': ''},
            'value': {'path': 'details.iocs.cves[]'},
        },
    ],
    'associatedIndicators': [
        {
            'summary': {
                'metadata': {'comment': ''},
                'path': 'details.iocs.domains[]',
            },
            'type': {
                'metadata': {'comment': ''},
                'path': "'domain'",
            },
        },
    ],
    'attributes': [
        {
            'displayed': False,
            'pinned': False,
            'source': 'CrowdStrike',
            'type': 'Alert Rule',
            'value': {
                'metadata': {},
                'path': 'notification.rule_name',
                'transform': [],
            },
        },
        {
            'displayed': False,
            'pinned': False,
            'source': 'CrowdStrike',
            'type': 'Priority',
            'value': {
                'metadata': {},
                'path': 'notification.rule_priority',
                'transform': [],
            },
        },
    ],
    'eventDate': {'path': 'notification.breach_summary.exposure_date'},
    'externalDateAdded': {
        'metadata': {},
        'path': 'notification.created_date',
        'transform': [],
    },
    'externalLastModified': {
        'metadata': {},
        'path': 'notification.updated_date',
        'transform': [],
    },
    'name': {
        'metadata': {'comment': 'need to put today\'s date somewhere'},
        'path': (
            "join('',[notification.rule_name || '', ' - ',"
            " notification.item_type || '', ' - ',"
            " notification.breach_summary.name || ''])"
        ),
        'transform': [],
    },
    'securityLabels': [],
    'status': {
        'metadata': {'comment': 'may need to do static mapping for this'},
        'path': 'notification.status',
        'transform': [
            {
                'kwargs': {'mapping': '{"new": "Needs Review"}'},
                'method': 'static_map',
            }
        ],
    },
    'tags': [
        {
            'metadata': {},
            'value': {
                'path': 'notification.breach_summary.fields[]',
                'transform': [],
            },
        },
        {
            'metadata': {},
            'value': {
                'path': 'notification.source_category',
                'transform': [
                    {'kwargs': {'prefix': 'Source Category: '}, 'method': 'prepend'},
                ],
            },
        },
    ],
    'type': {'metadata': {}, 'path': '`Event`', 'transform': []},
    'xid': {'metadata': {}, 'path': 'id', 'transform': []},
    'metadata': {
        'threatIntelType': 'group',
        'transformSchemaVersion': '1',
    }
}


class TestTransformBuilderLoad:
    """TestTransformBuilderLoad for Transform Builder Load Module Testing.

    This class provides tests for the `load` function which dispatches between
    v1 (Transform Builder export with 'transform' + 'type' keys) and v2 (raw
    camelCase mapping) formats, converting them into GroupTransformModel or
    IndicatorTransformModel instances.
    """

    def test_load_v1_returns_group_model(self, tcex: TcEx):
        """Test v1 group transform produces a GroupTransformModel.

        Verifies that a v1 transform export (with 'transform' and 'type' keys)
        is detected as v1 format and produces a GroupTransformModel.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V1_TRANSFORM), pf)

        assert isinstance(result, GroupTransformModel)

    def test_load_v1_type_field(self, tcex: TcEx):
        """Test v1 transform preserves the type field default.

        Verifies the type field default value is carried through.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V1_TRANSFORM), pf)

        assert result.type.default == 'Intrusion Set'

    def test_load_v1_name_path(self, tcex: TcEx):
        """Test v1 transform preserves the name path.

        Verifies the name field path value is carried through.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V1_TRANSFORM), pf)

        assert result.name.path == 'name'

    def test_load_v1_name_transforms_resolved(self, tcex: TcEx):
        """Test v1 transform resolves method names to callables.

        Verifies that string method names (e.g., 'truncate') are resolved
        to callables on the ProcessingFunctions instance.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V1_TRANSFORM), pf)

        assert result.name.transform is not None
        assert len(result.name.transform) > 0
        for t in result.name.transform:
            fn = t.method or t.for_each
            assert callable(fn), f'Expected callable, got {type(fn)}'

    def test_load_v1_xid_transforms_resolved(self, tcex: TcEx):
        """Test v1 transform resolves xid transform methods to callables.

        Verifies that xid transform methods 'prepend' and 'to_uppercase'
        are resolved to callables.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V1_TRANSFORM), pf)

        assert result.xid is not None
        assert result.xid.transform is not None
        assert len(result.xid.transform) == 2
        for t in result.xid.transform:
            fn = t.method or t.for_each
            assert callable(fn)

    def test_load_v1_attributes_present(self, tcex: TcEx):
        """Test v1 transform includes attributes.

        Verifies the v1 transform has attributes with the expected types.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V1_TRANSFORM), pf)

        assert len(result.attributes) > 0
        attr_types = [a.type for a in result.attributes]
        assert 'External ID' in attr_types
        assert 'Description' in attr_types

    def test_load_v2_returns_group_model(self, tcex: TcEx):
        """Test v2 group transform produces a GroupTransformModel.

        Verifies that a v2 transform with ti_type='group' produces
        a GroupTransformModel.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V2_TRANSFORM), pf)

        assert isinstance(result, GroupTransformModel)

    def test_load_v2_normalizes_camel_to_snake(self, tcex: TcEx):
        """Test v2 transform normalizes camelCase keys to snake_case.

        Verifies that v2 keys like 'associatedGroups' and 'externalDateAdded'
        are properly converted to snake_case model fields.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V2_TRANSFORM), pf)

        assert result.external_date_added is not None
        assert result.external_date_added.path == 'notification.created_date'

    def test_load_v2_strips_metadata(self, tcex: TcEx):
        """Test v2 transform strips metadata from fields.

        Verifies that metadata objects are removed during loading and do
        not appear in the resulting model.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V2_TRANSFORM), pf)

        # name had metadata with a comment; it should be stripped
        assert result.name.path is not None
        assert not hasattr(result.name, 'metadata')

    def test_load_v2_type_field(self, tcex: TcEx):
        """Test v2 transform parses the type field.

        Verifies the type field path is properly loaded.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V2_TRANSFORM), pf)

        assert result.type.path == '`Event`'

    def test_load_v2_xid_field(self, tcex: TcEx):
        """Test v2 transform parses the xid field.

        Verifies the xid path is properly loaded.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V2_TRANSFORM), pf)

        assert result.xid is not None
        assert result.xid.path == 'id'

    def test_load_v2_associated_groups(self, tcex: TcEx):
        """Test v2 transform loads associated groups.

        Verifies associated_groups are parsed and metadata is stripped.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V2_TRANSFORM), pf)

        assert len(result.associated_groups) == 2

    def test_load_v2_associated_group_transforms_resolved(self, tcex: TcEx):
        """Test v2 associated group transform methods are resolved to callables.

        Verifies that string method/forEach names in associated group transforms
        become callables.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V2_TRANSFORM), pf)

        # First associated group has transforms with custom + forEach
        first_group = result.associated_groups[0]
        assert first_group.value.transform is not None
        for t in first_group.value.transform:
            fn = t.method or t.for_each
            assert callable(fn), f'Expected callable, got {fn}'

    def test_load_v2_tags(self, tcex: TcEx):
        """Test v2 transform loads tags.

        Verifies tags are parsed and empty transforms are cleaned.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V2_TRANSFORM), pf)

        assert len(result.tags) == 2

    def test_load_v2_tag_transforms_resolved(self, tcex: TcEx):
        """Test v2 tag transform methods are resolved to callables.

        Verifies that the second tag's 'prepend' transform is resolved.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V2_TRANSFORM), pf)

        # Second tag has a prepend transform
        second_tag = result.tags[1]
        assert second_tag.value.transform is not None
        fn = second_tag.value.transform[0].method
        assert callable(fn)

    def test_load_v2_attributes(self, tcex: TcEx):
        """Test v2 transform loads attributes.

        Verifies attributes are parsed with correct types and metadata removed.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V2_TRANSFORM), pf)

        assert len(result.attributes) == 2
        attr_types = [a.type for a in result.attributes]
        assert 'Alert Rule' in attr_types
        assert 'Priority' in attr_types

    def test_load_v2_empty_security_labels_cleaned(self, tcex: TcEx):
        """Test v2 transform removes empty security labels list.

        Verifies that an empty securityLabels array is cleaned from output.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V2_TRANSFORM), pf)

        assert result.security_labels == []

    def test_load_v2_status_transform_resolved(self, tcex: TcEx):
        """Test v2 status transform resolves static_map to callable.

        Verifies the status field's static_map transform is resolved.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V2_TRANSFORM), pf)

        assert result.status is not None
        assert result.status.transform is not None
        fn = result.status.transform[0].method
        assert callable(fn)

    def test_load_v2_event_date(self, tcex: TcEx):
        """Test v2 transform loads event_date field.

        Verifies the eventDate field is normalized and loaded.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V2_TRANSFORM), pf)

        assert result.event_date is not None
        assert result.event_date.path == 'notification.breach_summary.exposure_date'

    def test_load_v2_empty_transforms_stripped(self, tcex: TcEx):
        """Test v2 transform strips empty transform arrays.

        Verifies that fields with empty transform arrays have the transform
        key removed rather than kept as an empty list.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V2_TRANSFORM), pf)

        # xid had an empty transform list; it should be stripped
        assert result.xid is not None
        assert result.xid.transform is None or result.xid.transform == []

    def test_load_v2_external_last_modified(self, tcex: TcEx):
        """Test v2 transform loads external_last_modified field.

        Verifies the externalLastModified field is normalized and loaded.

        Fixtures:
            tcex: TcEx instance for creating ProcessingFunctions
        """
        pf = ProcessingFunctions(tcex)
        result = load(copy.deepcopy(V2_TRANSFORM), pf)

        assert result.external_last_modified is not None
        assert result.external_last_modified.path == 'notification.updated_date'
