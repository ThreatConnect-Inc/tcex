"""TestPlaybookRaw for TcEx App Playbook Raw Module Testing.

This module contains comprehensive test cases for the TcEx App Playbook Raw Module,
specifically testing raw variable functionality including creation, reading, deletion,
and null handling for various data types including bytes, strings, and integers
across different playbook variable operations.

Classes:
    TestPlaybookRaw: Test class for TcEx App Playbook Raw Module functionality

TcEx Module Tested: app.playbook.playbook
"""


import pytest


from tcex.app.playbook.playbook import Playbook


class TestPlaybookRaw:
    """TestPlaybookRaw for TcEx App Playbook Raw Module Testing.

    This class provides comprehensive testing for the TcEx App Playbook Raw Module,
    covering various raw variable scenarios including successful operations,
    null handling, and proper cleanup across different data types and formats.
    """

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param('#App:0002:r1!Raw', b'bytes 1', id='pass-raw-bytes-1'),
            pytest.param('#App:0002:r2!Raw', b'string', id='pass-raw-string'),
            pytest.param('#App:0002:r3!Raw', b'1', id='pass-raw-integer'),
        ],
    )
    def test_playbook_raw(self, variable: str, value: bytes, playbook: Playbook) -> None:
        """Test Playbook Raw for TcEx App Playbook Raw Module.

        This test case verifies that raw variables can be successfully created,
        read, and deleted in the playbook system, ensuring proper raw data
        handling and storage operations for various data types including bytes,
        strings, and integers.

        Parameters:
            variable: The playbook variable name to test
            value: The raw data value to store and retrieve

        Fixtures:
            playbook: Playbook instance for testing raw operations
        """
        playbook.create.raw(variable, value)
        result = playbook.read.raw(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    def test_playbook_create_raw_none(self, playbook: Playbook) -> None:
        """Test Playbook Create Raw None for TcEx App Playbook Raw Module.

        This test case verifies that raw variable creation properly handles
        null inputs by testing None values for both variable name and data,
        ensuring appropriate null handling and return values.

        Fixtures:
            playbook: Playbook instance for testing raw operations
        """
        result = playbook.create.raw(None, None)  # type: ignore
        assert result is None, f'result of ({result}) is not None'

    def test_playbook_read_raw_none(self, playbook: Playbook) -> None:
        """Test Playbook Read Raw None for TcEx App Playbook Raw Module.

        This test case verifies that raw variable reading properly handles
        null inputs by testing None values for variable names, ensuring
        appropriate null handling and return values.

        Fixtures:
            playbook: Playbook instance for testing raw operations
        """
        result = playbook.read.raw(None)  # type: ignore
        assert result is None, f'result of ({result}) is not None'
