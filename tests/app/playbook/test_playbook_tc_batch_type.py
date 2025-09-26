"""TestPlaybookTcBatchType for TcEx App Playbook TC Batch Type Module Testing.

This module contains comprehensive test cases for the TcEx App Playbook TC Batch Type Module,
specifically testing TC batch variable functionality including creation, reading, validation,
deletion, and error handling across various data types and formats for playbook variable
operations involving ThreatConnect batch data structures.

Classes:
    TestPlaybookTcBatchType: Test class for TcEx App Playbook TC Batch Type Module functionality

TcEx Module Tested: app.playbook.playbook
"""


import json
from pathlib import Path
from typing import Any


import pytest

from _pytest.fixtures import FixtureRequest


from tcex.app.playbook.playbook import Playbook


class TestPlaybookTcBatchType:
    """TestPlaybookTcBatchType for TcEx App Playbook TC Batch Type Module Testing.

    This class provides comprehensive testing for the TcEx App Playbook TC Batch Type Module,
    covering various TC batch scenarios including successful operations, failure handling,
    type validation, file-based testing, and proper cleanup across different playbook
    variable types and data formats for ThreatConnect batch operations.
    """

    @pytest.mark.parametrize(
        'variable,filename',
        [
            pytest.param('#App:0002:tb1!TCBatch', 'large_file', id='pass-large-file'),
            pytest.param('#App:0002:tb2!TCBatch', 'empty_indicators', id='pass-empty-indicators'),
            pytest.param('#App:0002:tb3!TCBatch', 'empty_groups', id='pass-empty-groups'),
            pytest.param('#App:0002:tb4!TCBatch', 'small_file', id='pass-small-file'),
        ],
    )
    def test_playbook_tc_batch_pass(
        self,
        variable: str,
        filename: str,
        playbook: Playbook,
        request: FixtureRequest,
    ) -> None:
        """Test Playbook TC Batch Pass for TcEx App Playbook TC Batch Type Module.

        This test case verifies that TC batch variables can be successfully created,
        read, and deleted in the playbook system, ensuring proper TC batch data
        handling and storage operations for various file-based test scenarios
        including large files, empty indicators, empty groups, and small files.

        Parameters:
            variable: The playbook variable name to test
            filename: The test file name to load batch data from

        Fixtures:
            playbook: Playbook instance for testing TC batch operations
            request: Pytest fixture request for accessing test file paths
        """
        abspath = Path(request.fspath.dirname) / 'batch_test_input' / f'{filename}.json'  # type: ignore

        with abspath.open() as file:
            data = json.load(file)
        playbook.create.tc_batch(variable, data, when_requested=False)
        result = playbook.read.tc_batch(variable)
        assert result == data, f'result of ({result}) does not match ({data})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param('#App:0002:b1!TCBatch', [], id='fail-empty-list'),
            pytest.param(
                '#App:0002:b2!TCBatch', {'indicator': {}, 'group': {}}, id='fail-empty-dicts'
            ),
            pytest.param(
                '#App:0002:b3!TCBatch',
                {'indicator': [], 'group': 'invalid group'},
                id='fail-invalid-group-type',
            ),
            pytest.param(
                '#App:0002:b4!TCBatch',
                {'indicator': 'invalid indicator', 'group': []},
                id='fail-invalid-indicator-type',
            ),
            pytest.param(
                '#App:0002:b5!TCBatch',
                {'indicator': None, 'group': [{'one': '1', 'two': 'two'}]},
                id='fail-null-indicator',
            ),
            pytest.param(
                '#App:0002:b6!TCBatch',
                {'indicator': [{'one': '1', 'two': 'two'}], 'group': None},
                id='fail-null-group',
            ),
            pytest.param('#App:0002:b7!WrongType', 'wrong type', id='fail-wrong-variable-type'),
        ],
    )
    def test_playbook_tc_batch_fail(self, variable: str, value: Any, playbook: Playbook) -> None:
        """Test Playbook TC Batch Fail for TcEx App Playbook TC Batch Type Module.

        This test case verifies that TC batch variables properly reject invalid data
        types by testing various non-batch inputs and ensuring appropriate
        RuntimeError exceptions are raised for invalid data structures including
        empty lists, empty dictionaries, invalid types, and null values.

        Parameters:
            variable: The playbook variable name to test
            value: The invalid data value that should cause failure

        Fixtures:
            playbook: Playbook instance for testing TC batch operations
        """
        try:
            playbook.create.tc_batch(variable, value, when_requested=False)
            pytest.fail(f'{value} is not a valid TCBatch value')
        except RuntimeError:
            assert True
