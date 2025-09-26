"""TestPlaybookBinaryType for TcEx App Playbook Binary Type Module Testing.

This module contains comprehensive test cases for the TcEx App Playbook Binary Type Module,
specifically testing binary and binary array variable functionality including creation,
reading, validation, decoding, base64 handling, and error scenarios across various
data types and playbook variable operations.

Classes:
    TestPlaybookBinaryType: Test class for TcEx App Playbook Binary Type Module functionality

TcEx Module Tested: app.playbook.playbook
"""


from typing import Any


import pytest


from tcex.app.playbook.playbook import Playbook


class TestPlaybookBinaryType:
    """TestPlaybookBinaryType for TcEx App Playbook Binary Type Module Testing.

    This class provides comprehensive testing for the TcEx App Playbook Binary Type Module,
    covering various binary and binary array scenarios including successful operations,
    failure handling, type validation, decoding functionality, and base64 encoding
    across different playbook variable types and data formats.
    """

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param('#App:0002:b1!Binary', b'bytes 1', id='pass-binary-1'),
            pytest.param('#App:0002:b2!Binary', b'bytes 2', id='pass-binary-2'),
            pytest.param('#App:0002:b3!Binary', b'bytes 3', id='pass-binary-3'),
            pytest.param('#App:0002:b4!Binary', b'bytes 4', id='pass-binary-4'),
        ],
    )
    def test_playbook_binary_pass(self, variable: str, value: bytes, playbook: Playbook) -> None:
        """Test Playbook Binary Pass for TcEx App Playbook Binary Type Module.

        This test case verifies that binary variables can be successfully created,
        read, and deleted in the playbook system, ensuring proper binary data
        handling and storage operations.

        Parameters:
            variable: The playbook variable name to test
            value: The binary data value to store and retrieve

        Fixtures:
            playbook: Playbook instance for testing binary operations
        """
        playbook.create.binary(variable, value, when_requested=False)
        result = playbook.read.binary(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param('#App:0002:b1!Binary', 'not binary 1', id='fail-binary-string'),
            pytest.param('#App:0002:b2!Binary', [], id='fail-binary-list'),
            pytest.param('#App:0002:b3!Binary', {}, id='fail-binary-dict'),
            pytest.param('#App:0002:b3!WrongType', 'wrong type', id='fail-wrong-type'),
        ],
    )
    def test_playbook_binary_fail(self, variable: str, value: Any, playbook: Playbook) -> None:
        """Test Playbook Binary Fail for TcEx App Playbook Binary Type Module.

        This test case verifies that binary variables properly reject invalid data
        types by testing various non-binary inputs and ensuring appropriate
        RuntimeError exceptions are raised.

        Parameters:
            variable: The playbook variable name to test
            value: The invalid data value that should cause failure

        Fixtures:
            playbook: Playbook instance for testing binary operations
        """
        try:
            playbook.create.binary(variable, value, when_requested=False)
            pytest.fail(f'{value} is not a valid Binary value')
        except RuntimeError:
            assert True

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param(
                '#App:0003:ba1!BinaryArray', [b'bytes 1', b'bytes 1'], id='pass-binary-array-1'
            ),
            pytest.param(
                '#App:0003:ba2!BinaryArray', [b'bytes 2', b'bytes 2'], id='pass-binary-array-2'
            ),
            pytest.param(
                '#App:0003:ba3!BinaryArray', [b'bytes 3', b'bytes 3'], id='pass-binary-array-3'
            ),
            pytest.param(
                '#App:0003:ba4!BinaryArray', [b'bytes 4', b'bytes 4'], id='pass-binary-array-4'
            ),
        ],
    )
    def test_playbook_binary_array_pass(
        self, variable: str, value: list[bytes], playbook: Playbook
    ) -> None:
        """Test Playbook Binary Array Pass for TcEx App Playbook Binary Type Module.

        This test case verifies that binary array variables can be successfully
        created, read, and deleted in the playbook system, ensuring proper
        binary array data handling and storage operations.

        Parameters:
            variable: The playbook variable name to test
            value: The binary array data value to store and retrieve

        Fixtures:
            playbook: Playbook instance for testing binary array operations
        """
        playbook.create.binary_array(variable, value, when_requested=False)
        result = playbook.read.binary_array(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param(
                '#App:0003:ba1!BinaryArray',
                ['not binary 1', 'not binary 1'],
                id='fail-binary-array-string',
            ),
            pytest.param('#App:0002:b3!WrongType', 'wrong type', id='fail-binary-array-wrong-type'),
        ],
    )
    def test_playbook_binary_array_fail(
        self, variable: str, value: Any, playbook: Playbook
    ) -> None:
        """Test Playbook Binary Array Fail for TcEx App Playbook Binary Type Module.

        This test case verifies that binary array variables properly reject invalid
        data types by testing various non-binary array inputs and ensuring
        appropriate RuntimeError exceptions are raised.

        Parameters:
            variable: The playbook variable name to test
            value: The binary array data value to store and retrieve

        Fixtures:
            playbook: Playbook instance for testing binary array operations
        """
        try:
            playbook.create.binary_array(variable, value, when_requested=False)
            pytest.fail(f'{value} is not a valid Binary Array value')
        except RuntimeError:
            assert True

    #
    # Type specific
    #

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param('#App:0002:b1!Binary', b'bytes 1', id='decode-binary-1'),
            pytest.param('#App:0002:b2!Binary', b'bytes 2', id='decode-binary-2'),
            pytest.param('#App:0002:b3!Binary', b'bytes 3', id='decode-binary-3'),
            pytest.param('#App:0002:b4!Binary', b'bytes 4', id='decode-binary-4'),
        ],
    )
    def test_playbook_binary_decode(self, variable: str, value: bytes, playbook: Playbook) -> None:
        """Test Playbook Binary Decode for TcEx App Playbook Binary Type Module.

        This test case verifies that binary variables can be successfully decoded
        to strings when the decode parameter is set to True, ensuring proper
        UTF-8 decoding functionality for binary data.

        Parameters:
            variable: The playbook variable name to test
            value: The binary data value to store and retrieve

        Fixtures:
            playbook: Playbook instance for testing binary decode operations
        """
        playbook.create.binary(variable, value, when_requested=False)
        result = playbook.read.binary(variable, decode=True)
        assert result == value.decode('utf-8'), f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value,expected',
        [
            pytest.param(
                '#App:0002:b1!Binary', b'bytes 1', 'Ynl0ZXMgMQ==', id='no-b64decode-binary-1'
            ),
            pytest.param(
                '#App:0002:b2!Binary', b'bytes 2', 'Ynl0ZXMgMg==', id='no-b64decode-binary-2'
            ),
            pytest.param(
                '#App:0002:b3!Binary', b'bytes 3', 'Ynl0ZXMgMw==', id='no-b64decode-binary-3'
            ),
            pytest.param(
                '#App:0002:b4!Binary', b'bytes 4', 'Ynl0ZXMgNA==', id='no-b64decode-binary-4'
            ),
        ],
    )
    def test_playbook_binary_no_b64decode(
        self, variable: str, value: bytes, expected: str, playbook: Playbook
    ) -> None:
        """Test Playbook Binary No Base64 Decode for TcEx App Playbook Binary Type Module.

        This test case verifies that binary variables return base64 encoded strings
        when the b64decode parameter is set to False, ensuring proper base64
        encoding preservation for binary data.

        Parameters:
            variable: The playbook variable name to test
            value: The binary array data value to store, retrieve, and decode
            expected: The expected base64 encoded string result

        Fixtures:
            playbook: Playbook instance for testing binary base64 operations
        """
        playbook.create.binary(variable, value, when_requested=False)
        result = playbook.read.binary(variable, b64decode=False)
        assert result == expected, f'result of ({result}) for ({value}) does not match ({expected})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param(
                '#App:0003:ba1!BinaryArray', [b'bytes 1', b'bytes 1'], id='decode-binary-array-1'
            ),
            pytest.param(
                '#App:0003:ba2!BinaryArray', [b'bytes 2', b'bytes 2'], id='decode-binary-array-2'
            ),
            pytest.param(
                '#App:0003:ba3!BinaryArray', [b'bytes 3', b'bytes 3'], id='decode-binary-array-3'
            ),
            pytest.param(
                '#App:0003:ba4!BinaryArray', [b'bytes 4', b'bytes 4'], id='decode-binary-array-4'
            ),
        ],
    )
    def test_playbook_binary_array_decode(
        self, variable: str, value: list[bytes], playbook: Playbook
    ) -> None:
        """Test Playbook Binary Array Decode for TcEx App Playbook Binary Type Module.

        This test case verifies that binary array variables can be successfully
        decoded to string arrays when the decode parameter is set to True,
        ensuring proper UTF-8 decoding functionality for binary array data.

        Parameters:
            variable: The playbook variable name to test
            value: The binary array data value to store, retrieve, and decode

        Fixtures:
            playbook: Playbook instance for testing binary array decode operations
        """
        playbook.create.binary_array(variable, value, when_requested=False)
        result = playbook.read.binary_array(variable, decode=True)
        assert result == [v.decode('utf-8') for v in value], (
            f'result of ({result}) does not match ({value})'
        )

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value,expected',
        [
            pytest.param(
                '#App:0003:ba1!BinaryArray',
                [b'bytes 1', b'bytes 1'],
                ['Ynl0ZXMgMQ==', 'Ynl0ZXMgMQ=='],
                id='no-b64decode-binary-array-1',
            ),
            pytest.param(
                '#App:0003:ba2!BinaryArray',
                [b'bytes 2', b'bytes 2'],
                ['Ynl0ZXMgMg==', 'Ynl0ZXMgMg=='],
                id='no-b64decode-binary-array-2',
            ),
            pytest.param(
                '#App:0003:ba3!BinaryArray',
                [b'bytes 3', b'bytes 3'],
                ['Ynl0ZXMgMw==', 'Ynl0ZXMgMw=='],
                id='no-b64decode-binary-array-3',
            ),
            pytest.param(
                '#App:0003:ba4!BinaryArray',
                [b'bytes 4', b'bytes 4'],
                ['Ynl0ZXMgNA==', 'Ynl0ZXMgNA=='],
                id='no-b64decode-binary-array-4',
            ),
        ],
    )
    def test_playbook_binary_array_no_b64decode(
        self, variable: str, value: list[bytes], expected: list[str], playbook: Playbook
    ) -> None:
        """Test Playbook Binary Array No Base64 Decode for TcEx App Playbook Binary Type Module.

        This test case verifies that binary array variables return base64 encoded
        string arrays when the b64decode parameter is set to False, ensuring
        proper base64 encoding preservation for binary array data.

        Parameters:
            variable: The playbook variable name to test
            value: The binary array data value to store, retrieve, and decode
            expected: The expected base64 encoded string array result

        Fixtures:
            playbook: Playbook instance for testing binary array base64 operations
        """
        playbook.create.binary_array(variable, value, when_requested=False)
        result = playbook.read.binary_array(variable, b64decode=False)
        assert result == expected, f'result of ({result}) for ({value}) does not match ({expected})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None
