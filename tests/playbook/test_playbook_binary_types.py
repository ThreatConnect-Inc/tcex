"""Test the TcEx Batch Module."""
# standard library
from typing import Any

# third-party
import pytest

# first-party
from tcex.playbook.playbook import Playbook


class TestUtils:
    """Test the TcEx Batch Module."""

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0002:b1!Binary', b'bytes 1'),
            ('#App:0002:b2!Binary', b'bytes 2'),
            ('#App:0002:b3!Binary', b'bytes 3'),
            ('#App:0002:b4!Binary', b'bytes 4'),
        ],
    )
    def test_playbook_binary_pass(self, variable: str, value: bytes, playbook: Playbook):
        """Test playbook variables."""
        playbook.create.binary(variable, value, when_requested=False)
        result = playbook.read.binary(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0002:b1!Binary', 'not binary 1'),
            ('#App:0002:b2!Binary', []),
            ('#App:0002:b3!Binary', {}),
            ('#App:0002:b3!WrongType', 'wrong type'),
        ],
    )
    def test_playbook_binary_fail(self, variable: str, value: Any, playbook: Playbook):
        """Test playbook variables."""
        try:
            playbook.create.binary(variable, value, when_requested=False)
            assert False, f'{value} is not a valid Binary value'
        except RuntimeError:
            assert True

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0003:ba1!BinaryArray', [b'bytes 1', b'bytes 1']),
            ('#App:0003:ba2!BinaryArray', [b'bytes 2', b'bytes 2']),
            ('#App:0003:ba3!BinaryArray', [b'bytes 3', b'bytes 3']),
            ('#App:0003:ba4!BinaryArray', [b'bytes 4', b'bytes 4']),
        ],
    )
    def test_playbook_binary_array_pass(
        self, variable: str, value: list[bytes], playbook: Playbook
    ):
        """Test playbook variables."""
        playbook.create.binary_array(variable, value, when_requested=False)
        result = playbook.read.binary_array(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0003:ba1!BinaryArray', ['not binary 1', 'not binary 1']),
            ('#App:0002:b3!WrongType', 'wrong type'),
        ],
    )
    def test_playbook_binary_array_fail(self, variable: str, value: Any, playbook: Playbook):
        """Test playbook variables."""
        try:
            playbook.create.binary_array(variable, value, when_requested=False)
            assert False, f'{value} is not a valid Binary Array value'
        except RuntimeError:
            assert True

    #
    # Type specific
    #

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0002:b1!Binary', b'bytes 1'),
            ('#App:0002:b2!Binary', b'bytes 2'),
            ('#App:0002:b3!Binary', b'bytes 3'),
            ('#App:0002:b4!Binary', b'bytes 4'),
        ],
    )
    def test_playbook_binary_decode(self, variable: str, value: bytes, playbook: Playbook):
        """Test playbook variables."""
        playbook.create.binary(variable, value, when_requested=False)
        result = playbook.read.binary(variable, decode=True)
        assert result == value.decode('utf-8'), f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value,expected',
        [
            ('#App:0002:b1!Binary', b'bytes 1', 'Ynl0ZXMgMQ=='),
            ('#App:0002:b2!Binary', b'bytes 2', 'Ynl0ZXMgMg=='),
            ('#App:0002:b3!Binary', b'bytes 3', 'Ynl0ZXMgMw=='),
            ('#App:0002:b4!Binary', b'bytes 4', 'Ynl0ZXMgNA=='),
        ],
    )
    def test_playbook_binary_no_b64decode(
        self, variable: str, value: bytes, expected: str, playbook: Playbook
    ):
        """Test playbook variables."""
        playbook.create.binary(variable, value, when_requested=False)
        result = playbook.read.binary(variable, b64decode=False)
        assert result == expected, f'result of ({result}) for ({value}) does not match ({expected})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0003:ba1!BinaryArray', [b'bytes 1', b'bytes 1']),
            ('#App:0003:ba2!BinaryArray', [b'bytes 2', b'bytes 2']),
            ('#App:0003:ba3!BinaryArray', [b'bytes 3', b'bytes 3']),
            ('#App:0003:ba4!BinaryArray', [b'bytes 4', b'bytes 4']),
        ],
    )
    def test_playbook_binary_array_decode(
        self, variable: str, value: list[bytes], playbook: Playbook
    ):
        """Test playbook variables."""
        playbook.create.binary_array(variable, value, when_requested=False)
        result = playbook.read.binary_array(variable, decode=True)
        assert result == [
            v.decode('utf-8') for v in value
        ], f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value,expected',
        [
            (
                '#App:0003:ba1!BinaryArray',
                [b'bytes 1', b'bytes 1'],
                ['Ynl0ZXMgMQ==', 'Ynl0ZXMgMQ=='],
            ),
            (
                '#App:0003:ba2!BinaryArray',
                [b'bytes 2', b'bytes 2'],
                ['Ynl0ZXMgMg==', 'Ynl0ZXMgMg=='],
            ),
            (
                '#App:0003:ba3!BinaryArray',
                [b'bytes 3', b'bytes 3'],
                ['Ynl0ZXMgMw==', 'Ynl0ZXMgMw=='],
            ),
            (
                '#App:0003:ba4!BinaryArray',
                [b'bytes 4', b'bytes 4'],
                ['Ynl0ZXMgNA==', 'Ynl0ZXMgNA=='],
            ),
        ],
    )
    def test_playbook_binary_array_no_b64decode(
        self, variable: str, value: list[bytes], expected: list[str], playbook: Playbook
    ):
        """Test playbook variables."""
        playbook.create.binary_array(variable, value, when_requested=False)
        result = playbook.read.binary_array(variable, b64decode=False)
        assert result == expected, f'result of ({result}) for ({value}) does not match ({expected})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None
