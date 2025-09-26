"""TestPlaybookStringType for TcEx App Playbook String Type Module Testing.

This module contains comprehensive test cases for the TcEx App Playbook String Type Module,
specifically testing string and string array variable functionality including creation,
reading, validation, deletion, and error handling across various data types and formats
for playbook variable operations.

Classes:
    TestPlaybookStringType: Test class for TcEx App Playbook String Type Module functionality

TcEx Module Tested: app.playbook.playbook
"""


from collections.abc import Iterable
from typing import Any


import pytest


from tcex.app.playbook.playbook import Playbook  # TYPE-CHECKING


class TestPlaybookStringType:
    """TestPlaybookStringType for TcEx App Playbook String Type Module Testing.

    This class provides comprehensive testing for the TcEx App Playbook String Type Module,
    covering various string and string array scenarios including successful operations,
    failure handling, type validation, iterable processing, and proper cleanup across
    different playbook variable types and data formats.
    """

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param('#App:0002:s1!String', 1, id='pass-string-integer'),
            pytest.param('#App:0002:s2!String', '2', id='pass-string-string'),
            pytest.param('#App:0002:s3!String', '3', id='pass-string-string-2'),
            pytest.param('#App:0002:s4!String', True, id='pass-string-boolean'),
        ],
    )
    def test_playbook_string_pass(
        self, variable: str, value: bool | int | str, playbook: Playbook
    ) -> None:
        """Test Playbook String Pass for TcEx App Playbook String Type Module.

        This test case verifies that string variables can be successfully created,
        read, and deleted in the playbook system, ensuring proper string data
        handling and storage operations for various data types including integers,
        strings, and booleans with automatic type coercion.

        Parameters:
            variable: The playbook variable name to test
            value: The data value to store and retrieve

        Fixtures:
            playbook: Playbook instance for testing string operations
        """
        playbook.create.string(variable, value, when_requested=False)
        result = playbook.read.string(variable)
        value = str(value).lower()
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param('#App:0002:s1!String', [], id='fail-string-list'),
            pytest.param('#App:0002:s2!String', {}, id='fail-string-dict'),
            pytest.param('#App:0002:s3!String', b'bytes', id='fail-string-bytes'),
            pytest.param('#App:0002:b3!WrongType', 'wrong type', id='fail-wrong-type'),
        ],
    )
    def test_playbook_string_fail(self, variable: str, value: Any, playbook: Playbook) -> None:
        """Test Playbook String Fail for TcEx App Playbook String Type Module.

        This test case verifies that string variables properly reject invalid data
        types by testing various non-string inputs and ensuring appropriate
        RuntimeError exceptions are raised for invalid data structures.

        Parameters:
            variable: The playbook variable name to test
            value: The invalid data value that should cause failure

        Fixtures:
            playbook: Playbook instance for testing string operations
        """
        try:
            playbook.create.string(variable, value, when_requested=False)
            pytest.fail(f'{value} is not a valid String value')
        except RuntimeError:
            assert True

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param('#App:0003:sa1!StringArray', ['1', '1'], id='pass-string-array-1'),
            pytest.param('#App:0003:sa2!StringArray', ['2', '2'], id='pass-string-array-2'),
            pytest.param('#App:0003:sa3!StringArray', ['3', '3'], id='pass-string-array-3'),
            pytest.param('#App:0003:sa4!StringArray', ['4', '4'], id='pass-string-array-4'),
        ],
    )
    def test_playbook_string_array_pass(
        self, variable: str, value: list[str], playbook: Playbook
    ) -> None:
        """Test Playbook String Array Pass for TcEx App Playbook String Type Module.

        This test case verifies that string array variables can be successfully
        created, read, and deleted in the playbook system, ensuring proper
        string array data handling and storage operations.

        Parameters:
            variable: The playbook variable name to test
            value: The string array data to store and retrieve

        Fixtures:
            playbook: Playbook instance for testing string array operations
        """
        playbook.create.string_array(variable, value, when_requested=False)  # type: ignore
        result = playbook.read.string_array(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    # @pytest.mark.parametrize(
    #     'variable,value',
    #     [('#App:0003:sa5!StringArray', 'foobar')],
    # )
    # def test_playbook_string_array_string(self, variable: str, value: Str, playbook: Playbook):
    #     """Test playbook variables."""
    #     with pytest.raises(RuntimeError) as ex:
    #         playbook.create.string_array(variable, value, when_requested=False)

    #     assert True

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param('#App:0003:sa1!StringArray', ['1', []], id='fail-string-array-with-list'),
            pytest.param('#App:0003:sa2!StringArray', ['2', {}], id='fail-string-array-with-dict'),
            pytest.param(
                '#App:0003:sa3!StringArray', ['3', b'bytes'], id='fail-string-array-with-bytes'
            ),
            pytest.param('#App:0003:sa5!StringArray', 'foobar', id='fail-string-array-string'),
            pytest.param('#App:0002:b3!WrongType', 'wrong type', id='fail-wrong-variable-type'),
        ],
    )
    def test_playbook_string_array_fail(
        self, variable: str, value: Any, playbook: Playbook
    ) -> None:
        """Test Playbook String Array Fail for TcEx App Playbook String Type Module.

        This test case verifies that string array variables properly reject invalid
        data types by testing various non-string-array inputs and ensuring
        appropriate RuntimeError exceptions are raised for invalid data structures.

        Parameters:
            variable: The playbook variable name to test
            value: The invalid data value that should cause failure

        Fixtures:
            playbook: Playbook instance for testing string array operations
        """
        with pytest.raises(RuntimeError) as ex:
            playbook.create.string_array(variable, value, when_requested=False)

        assert 'Invalid ' in str(ex.value)

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param('#App:0003:sa5!StringArray', ('6', '6'), id='pass-string-array-tuple'),
            pytest.param(
                '#App:0003:sa6!StringArray',
                (a for a in ['6', '6']),
                id='pass-string-array-generator'
            ),
            pytest.param(
                '#App:0003:sa6!StringArray',
                filter(lambda _: True, ['6', '6']),
                id='pass-string-array-filter'
            ),
        ],
    )
    def test_playbook_string_array_iterables(
        self, variable: str, value: Iterable, playbook: Playbook
    ) -> None:
        """Test Playbook String Array Iterables for TcEx App Playbook String Type Module.

        This test case verifies that string array variables can handle various
        iterable types including tuples, map objects, and filter objects,
        ensuring proper conversion and storage of iterable data.

        Parameters:
            variable: The playbook variable name to test
            value: The iterable data to store and retrieve

        Fixtures:
            playbook: Playbook instance for testing string array operations
        """
        playbook.create.string_array(variable, value, when_requested=False)  # type: ignore
        result = playbook.read.string_array(variable)
        assert result == ['6', '6'], f'result of ({result}) does not match ({list(value)})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    #
    # Type Specific
    #

    @pytest.mark.parametrize(
        'variable,value',
        [pytest.param('#App:0002:s1!String', None, id='pass-string-none')],
    )
    def test_playbook_string_none(
        self, variable: str, value: str | None, playbook: Playbook
    ) -> None:
        """Test Playbook String None for TcEx App Playbook String Type Module.

        This test case verifies that string variables properly handle None values
        by testing None input for both creation and reading operations,
        ensuring appropriate null handling and return values.

        Parameters:
            variable: The playbook variable name to test
            value: The None value to test for null handling

        Fixtures:
            playbook: Playbook instance for testing string operations
        """
        playbook.create.string(variable, value, when_requested=False)  # type: ignore
        playbook.read.string(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [pytest.param('#App:0003:sa1!StringArray', None, id='pass-string-array-none')],
    )
    def test_playbook_string_array_none(
        self, variable: str, value: list | None, playbook: Playbook
    ) -> None:
        """Test Playbook String Array None for TcEx App Playbook String Type Module.

        This test case verifies that string array variables properly handle None values
        by testing None input for both creation and reading operations,
        ensuring appropriate null handling and return values.

        Parameters:
            variable: The playbook variable name to test
            value: The None value to test for null handling

        Fixtures:
            playbook: Playbook instance for testing string array operations
        """
        playbook.create.string_array(variable, value, when_requested=False)  # type: ignore
        playbook.read.string_array(variable)
        assert playbook.read.variable(variable) is None

    def test_playbook_string_read_none(self, playbook: Playbook) -> None:
        """Test Playbook String Read None for TcEx App Playbook String Type Module.

        This test case verifies that string variable reading properly handles
        null inputs by testing None values for variable names, ensuring
        appropriate null handling and return values.

        Fixtures:
            playbook: Playbook instance for testing string operations
        """
        assert playbook.read.string(None) is None  # type: ignore
