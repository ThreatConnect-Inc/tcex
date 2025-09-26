"""TestPlaybookTcEntityType for TcEx App Playbook TC Entity Type Module Testing.

This module contains comprehensive test cases for the TcEx App Playbook TC Entity Type Module,
specifically testing TC entity and TC entity array variable functionality including creation,
reading, validation, deletion, and error handling across various data types and formats
for playbook variable operations involving ThreatConnect entity data structures.

Classes:
    TestPlaybookTcEntityType: Test class for TcEx App Playbook TC Entity Type Module functionality

TcEx Module Tested: app.playbook.playbook
"""


from typing import Any


import pytest


from tcex.app.playbook.playbook import Playbook  # TYPE-CHECKING
from tcex.input.field_type import KeyValue


class TestPlaybookTcEntityType:
    """TestPlaybookTcEntityType for TcEx App Playbook TC Entity Type Module Testing.

    This class provides comprehensive testing for the TcEx App Playbook TC Entity Type Module,
    covering various TC entity and TC entity array scenarios including successful operations,
    failure handling, type validation, and proper cleanup across different playbook
    variable types and data formats for ThreatConnect entity operations.
    """

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param(
                '#App:0002:te1!TCEntity',
                {'id': '001', 'value': '1.1.1.1', 'type': 'Address'},
                id='pass-tcentity-1',
            ),
            pytest.param(
                '#App:0002:te2!TCEntity',
                {'id': '002', 'value': '2.2.2.2', 'type': 'Address'},
                id='pass-tcentity-2',
            ),
            pytest.param(
                '#App:0002:te3!TCEntity',
                {'id': '003', 'value': '3.3.3.3', 'type': 'Address'},
                id='pass-tcentity-3',
            ),
            pytest.param(
                '#App:0002:te4!TCEntity',
                {'id': '004', 'value': '3.3.3.3', 'type': 'Address'},
                id='pass-tcentity-4',
            ),
        ],
    )
    def test_playbook_tc_entity_pass(
        self, variable: str, value: dict | KeyValue, playbook: Playbook
    ) -> None:
        """Test Playbook TC Entity Pass for TcEx App Playbook TC Entity Type Module.

        This test case verifies that TC entity variables can be successfully created,
        read, and deleted in the playbook system, ensuring proper TC entity data
        handling and storage operations for various entity types including Address
        entities with different IDs and values.

        Parameters:
            variable: The playbook variable name to test
            value: The TC entity data to store and retrieve

        Fixtures:
            playbook: Playbook instance for testing TC entity operations
        """
        playbook.create.tc_entity(variable, value, when_requested=False)
        result = playbook.read.tc_entity(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param(
                '#App:0002:b1!TCEntity', {'one': '1', 'two': 'two'}, id='fail-invalid-structure'
            ),
            pytest.param('#App:0002:b2!TCEntity', [], id='fail-list-type'),
            pytest.param('#App:0002:b3!TCEntity', {}, id='fail-empty-dict'),
            pytest.param('#App:0002:b4!WrongType', 'wrong type', id='fail-wrong-variable-type'),
        ],
    )
    def test_playbook_tc_entity_fail(self, variable: str, value: Any, playbook: Playbook) -> None:
        """Test Playbook TC Entity Fail for TcEx App Playbook TC Entity Type Module.

        This test case verifies that TC entity variables properly reject invalid data
        types by testing various non-entity inputs and ensuring appropriate
        RuntimeError exceptions are raised for invalid data structures including
        invalid dictionaries, lists, empty dictionaries, and wrong variable types.

        Parameters:
            variable: The playbook variable name to test
            value: The invalid data value that should cause failure

        Fixtures:
            playbook: Playbook instance for testing TC entity operations
        """
        try:
            playbook.create.tc_entity(variable, value, when_requested=False)
            pytest.fail(f'{value} is not a valid TCEntity value')
        except RuntimeError:
            assert True

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param(
                '#App:0002:tea1!TCEntityArray',
                [
                    {'id': '001', 'value': '1.1.1.1', 'type': 'Address'},
                    {'id': '011', 'value': '11.11.11.11', 'type': 'Address'},
                ],
                id='pass-tcentity-array-1',
            ),
            pytest.param(
                '#App:0002:tea2!TCEntityArray',
                [
                    {'id': '002', 'value': '2.2.2.2', 'type': 'Address'},
                    {'id': '022', 'value': '22.22.22.22', 'type': 'Address'},
                ],
                id='pass-tcentity-array-2',
            ),
            pytest.param(
                '#App:0002:tea3!TCEntityArray',
                [
                    {'id': '003', 'value': '3.3.3.3', 'type': 'Address'},
                    {'id': '033', 'value': '33.33.33.33', 'type': 'Address'},
                ],
                id='pass-tcentity-array-3',
            ),
            pytest.param(
                '#App:0002:tea4!TCEntityArray',
                [
                    {'id': '004', 'value': '4.4.4.4', 'type': 'Address'},
                    {'id': '044', 'value': '44.44.44.44', 'type': 'Address'},
                ],
                id='pass-tcentity-array-4',
            ),
        ],
    )
    def test_playbook_tc_entity_array_pass(
        self, variable: str, value: list[dict], playbook: Playbook
    ) -> None:
        """Test Playbook TC Entity Array Pass for TcEx App Playbook TC Entity Type Module.

        This test case verifies that TC entity array variables can be successfully
        created, read, and deleted in the playbook system, ensuring proper
        TC entity array data handling and storage operations for various entity
        types including Address entities with different IDs and values.

        Parameters:
            variable: The playbook variable name to test
            value: The TC entity array data to store and retrieve

        Fixtures:
            playbook: Playbook instance for testing TC entity array operations
        """
        playbook.create.tc_entity_array(variable, value, when_requested=False)  # type: ignore
        result = playbook.read.tc_entity_array(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param(
                '#App:0003:tea1!TCEntityArray',
                [
                    {'id': '001', 'value': '1.1.1.1', 'type': 'Address'},
                    {'id': '011', 'ip': '11.11.11.11', 'type': 'Address'},
                ],
                id='fail-invalid-entity-structure',
            ),
            pytest.param(
                '#App:0003:tea2!TCEntityArray', 'not a TCEntityArray', id='fail-string-type'
            ),
            pytest.param('#App:0003:tea3!WrongType', 'wrong type', id='fail-wrong-variable-type'),
        ],
    )
    def test_playbook_tc_entity_array_fail(
        self, variable: str, value: Any, playbook: Playbook
    ) -> None:
        """Test Playbook TC Entity Array Fail for TcEx App Playbook TC Entity Type Module.

        This test case verifies that TC entity array variables properly reject invalid
        data types by testing various non-entity-array inputs and ensuring
        appropriate RuntimeError exceptions are raised for invalid data structures
        including invalid entity structures, string types, and wrong variable types.

        Parameters:
            variable: The playbook variable name to test
            value: The invalid data value that should cause failure

        Fixtures:
            playbook: Playbook instance for testing TC entity array operations
        """
        with pytest.raises(RuntimeError) as ex:
            playbook.create.tc_entity_array(variable, value, when_requested=False)

        assert 'Invalid ' in str(ex.value)
