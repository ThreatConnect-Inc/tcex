"""TestUtilInterface for TcEx API TC Util Interface Module Testing.

This module contains comprehensive test cases for the TcEx API TC Util Interface Module,
specifically testing utility interface functionality including variable resolution,
API integration, and proper configuration behavior across different input formats
and validation scenarios for ThreatConnect utility operations.

Classes:
    TestUtilInterface: Test class for TcEx API TC Util Interface Module functionality

TcEx Module Tested: api.tc.util
"""


import pytest


from tcex.api.tc.v3.v3 import V3
from tcex.tcex import TcEx
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestUtilInterface(TestV3):
    """TestUtilInterface for TcEx API TC Util Interface Module Testing.

    This class provides comprehensive testing for the TcEx API TC Util Interface Module,
    covering various utility interface scenarios including variable resolution,
    API integration, and proper configuration behavior for ThreatConnect
    utility operations and interface testing.
    """

    tcex: TcEx
    v3: V3
    v3_helper = V3Helper('artifact_types')

    def setup_method(self) -> None:
        """Configure setup before all tests.

        This method is called before each test method to initialize
        the TcEx instance and V3 API helper for utility interface testing.
        """
        # Setup method for initializing test environment
        self.tcex = self.v3_helper.tcex
        self.v3 = self.v3_helper.v3

    # We dont auto stage user groups or workflow templates with new instances so i cannot
    # auto test against them.
    @pytest.mark.parametrize(
        'input_value,expected_value,fail_test',
        [
            (
                [
                    '${API_USERS}',
                    '${ARTIFACT_TYPES}',
                    '${ATTRIBUTES}',
                    '${GROUP_TYPES}',
                    '${INDICATOR_TYPES}',
                    '${OWNERS}',
                    '${USER_GROUPS}',
                    '${USERS}',
                    '${WORKFLOW_TEMPLATES}',
                    'Unique input',
                ],
                [
                    '99999999999999999999',
                    'TCI',
                    '22222222222222222222',
                    'bpurdy@threatconnect.com',
                    'External ID',
                    'Address',
                    'Registry Key',
                    'IP Address',
                    'Attack Pattern',
                    'Unique input',
                ],
                False,
            ),
            (['${API_USERS}', '${OWNERS}'], ['99999999999999999999', 'TCI'], False),
            (
                ['${USERS}', '${OWNERS}'],
                ['22222222222222222222', 'bpurdy@threatconnect.com', 'TCI'],
                False,
            ),
            (['${INDICATOR_TYPES} '], ['EmailAddress', 'Host', 'Registry Key'], False),
            (
                ['${INDICATOR_TYPES} '],
                ['EmailAddress', 'Host', 'Registry Key', 'Invalid subset item'],
                True,
            ),
        ],
    )
    def test_resolve_variables(
        self, input_value: list, expected_value: list, fail_test: bool
    ) -> None:
        """Test Resolve Variables for TcEx API TC Util Interface Module.

        This test case verifies that the utility interface correctly resolves
        various variable types including API users, artifact types, attributes,
        group types, indicator types, owners, user groups, users, and workflow
        templates, ensuring proper variable substitution and validation.

        Parameters:
            input_value: The list of input variables to resolve
            expected_value: The expected resolved values for validation
            fail_test: Boolean flag indicating if this test should fail

        This test validates the variable resolution capabilities and
        API integration functionality of the utility interface.
        """
        resolved_variables = self.v3.ti.ti_utils.resolve_variables(input_value)

        if fail_test is False:
            assert set(expected_value) <= set(resolved_variables), (
                f'expected values ({expected_value}) are not subset of resolved variables '
                f'({resolved_variables})'
            )
        else:
            assert not set(expected_value) <= set(resolved_variables), (
                f'expected values ({expected_value}) should not be subset of resolved variables '
                f'({resolved_variables}) for fail test'
            )
