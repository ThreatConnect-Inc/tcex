"""TcEx Framework Module"""

# third-party
import pytest

# first-party
from tcex.api.tc.v3.v3 import V3
from tcex.tcex import TcEx
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestArtifactTypes(TestV3):
    """Test TcEx API Interface."""

    tcex: TcEx
    v3: V3
    v3_helper = V3Helper('artifact_types')

    def setup_method(self):
        """Configure setup before all tests."""
        print('')  # ensure any following print statements will be on new line
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
    def test_resolve_variables(self, input_value: list, expected_value: list, fail_test: bool):
        """Test Resolve Variables"""
        resolved_variables = self.v3.ti.ti_utils.resolve_variables(input_value)

        if fail_test is False:
            assert set(expected_value) <= set(resolved_variables)
        else:
            assert not set(expected_value) <= set(resolved_variables)
