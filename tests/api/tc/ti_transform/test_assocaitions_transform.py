"""TestAssociationTransform for TcEx API TC TI Transform Module Testing.

This module contains comprehensive test cases for the TcEx API TC TI Transform Module,
specifically testing association transform functionality including regression testing,
file occurrence transforms, attribute transforms, and proper configuration behavior
across different data formats and validation scenarios for ThreatConnect association
transformation and processing.

Classes:
    TestAssociationTransform: Test class for TcEx API TC TI Transform Module functionality

TcEx Module Tested: api.tc.ti_transform
"""

import deepdiff
from tcex import TcEx


class TestAssociationTransform:
    """TestAssociationTransform for TcEx API TC TI Transform Module Testing.

    This class provides comprehensive testing for the TcEx API TC TI Transform Module,
    covering various association transform scenarios including regression testing,
    file occurrence transforms, attribute transforms, and proper configuration
    behavior for ThreatConnect association transformation and processing.
    """

    def test_association_types(self, tcex: TcEx) -> None:
        """Test Association Types for TcEx API TC TI Transform Module.

        This test case verifies that the association type transform functionality
        works correctly by testing type and value transformations,
        ensuring proper handling of association type data in indicator transforms.

        Parameters:
            tcex: The TcEx instance for API access

        This test validates the association type transform capabilities
        and data processing for associationn transformation.
        """
        data = [{'xid2': 'group-2', 'indicator1': '1.2.3.4'}]

        transform = tcex.api.tc.association_transform(
            {
                'associations': [
                    {
                        'xid_1': {'default': 'group-1'},
                        'xid_2': {'path': 'xid2'},
                    },
                    {
                        'xid': {'path': 'xid2'},
                        'indicator_value': {'path': 'indicator1'},
                        'indicator_type': {'default': 'Address'},
                    },
                    {
                        'indicator_value_1': {'path': 'indicator1'},
                        'indicator_type_1': {'default': 'Address'},
                        'indicator_value_2': {'default': '1.2.3.4'},
                        'indicator_type_2': {'default': 'Address'},
                        'custom_association_type': {'default': 'related-to'},
                    },
                ],
            }
        )

        transforms = tcex.api.tc.ti_transforms(data, [transform])

        tcex.log.warning(transforms.batch)

        expected_result = {
            'group': [],
            'indicator': [],
            'association': [
                {'ref_1': 'group-1', 'ref_2': 'group-2'},
                {'ref_1': 'group-2', 'ref_2': '1.2.3.4', 'type_2': 'Address'},
                {
                    'ref_1': '1.2.3.4',
                    'type_1': 'Address',
                    'ref_2': '1.2.3.4',
                    'type_2': 'Address',
                    'association_type': 'related-to',
                },
            ],
        }

        assert not deepdiff.DeepDiff(transforms.batch, expected_result), (
            f'transform results ({transforms.batch}) do not match expected ({expected_result})'
        )
