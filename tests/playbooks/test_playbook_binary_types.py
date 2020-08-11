"""Test the TcEx Batch Module."""
# third-party
import pytest


# pylint: disable=no-self-use
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
    def test_playbook_binary(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        tcex.playbook.create_binary(variable, value)
        result = tcex.playbook.read_binary(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0002:b1!Binary', 'not binary 1'),
            ('#App:0002:b2!Binary', []),
            ('#App:0002:b3!Binary', {}),
            ('#App:0002:b3!WrongType', 'wrong type'),
        ],
    )
    def test_playbook_binary_fail(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        try:
            tcex.playbook.create_binary(variable, value)
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
    def test_playbook_binary_array(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        tcex.playbook.create_binary_array(variable, value)
        result = tcex.playbook.read_binary_array(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0003:ba1!BinaryArray', ['not binary 1', 'not binary 1']),
            ('#App:0002:b3!WrongType', 'wrong type'),
        ],
    )
    def test_playbook_binary_array_fail(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        try:
            tcex.playbook.create_binary_array(variable, value)
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
    def test_playbook_binary_decode(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        tcex.playbook.create_binary(variable, value)
        result = tcex.playbook.read_binary(variable, decode=True)
        assert result == value.decode('utf-8'), f'result of ({result}) does not match ({value})'

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'variable,value,expected',
        [
            ('#App:0002:b1!Binary', b'bytes 1', 'Ynl0ZXMgMQ=='),
            ('#App:0002:b2!Binary', b'bytes 2', 'Ynl0ZXMgMg=='),
            ('#App:0002:b3!Binary', b'bytes 3', 'Ynl0ZXMgMw=='),
            ('#App:0002:b4!Binary', b'bytes 4', 'Ynl0ZXMgNA=='),
        ],
    )
    def test_playbook_binary_no_b64decode(self, variable, value, expected, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        tcex.playbook.create_binary(variable, value)
        result = tcex.playbook.read_binary(variable, b64decode=False)
        assert result == expected, f'result of ({result}) for ({value}) does not match ({expected})'

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0003:ba1!BinaryArray', [b'bytes 1', b'bytes 1']),
            ('#App:0003:ba2!BinaryArray', [b'bytes 2', b'bytes 2']),
            ('#App:0003:ba3!BinaryArray', [b'bytes 3', b'bytes 3']),
            ('#App:0003:ba4!BinaryArray', [b'bytes 4', b'bytes 4']),
        ],
    )
    def test_playbook_binary_array_decode(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        tcex.playbook.create_binary_array(variable, value)
        result = tcex.playbook.read_binary_array(variable, decode=True)
        assert result == [
            v.decode('utf-8') for v in value
        ], f'result of ({result}) does not match ({value})'

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

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
    def test_playbook_binary_array_no_b64decode(self, variable, value, expected, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (list): The value to store in Key Value Store.
            expected (list): The expected output of the read command.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        tcex.playbook.create_binary_array(variable, value)
        result = tcex.playbook.read_binary_array(variable, b64decode=False)
        assert result == expected, f'result of ({result}) for ({value}) does not match ({expected})'

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None
