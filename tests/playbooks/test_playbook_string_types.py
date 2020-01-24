# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
import pytest


# pylint: disable=no-self-use
class TestUtils:
    """Test the TcEx Batch Module."""

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0002:s1!String', 1),
            ('#App:0002:s2!String', '2'),
            ('#App:0002:s3!String', '3'),
            ('#App:0002:s4!String', True),
        ],
    )
    def test_playbook_string(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        tcex.playbook.create_string(variable, value)
        result = tcex.playbook.read_string(variable)
        value = str(value).lower()
        assert result == value, f'result of ({result}) does not match ({value})'

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0002:s1!String', []),
            ('#App:0002:s2!String', {}),
            ('#App:0002:s3!String', b'bytes'),
            ('#App:0002:b3!WrongType', 'wrong type'),
        ],
    )
    def test_playbook_string_fail(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        try:
            tcex.playbook.create_string(variable, value)
            assert False, f'{value} is not a valid String value'
        except RuntimeError:
            assert True

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0003:sa1!StringArray', ['1', '1']),
            ('#App:0003:sa2!StringArray', ['2', '2']),
            ('#App:0003:sa3!StringArray', ['3', '3']),
            ('#App:0003:sa4!StringArray', ['4', '4']),
        ],
    )
    def test_playbook_string_array(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        tcex.playbook.create_string_array(variable, value)
        result = tcex.playbook.read_string_array(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0003:sa1!StringArray', ['1', []]),
            ('#App:0003:sa2!StringArray', ['2', {}]),
            ('#App:0003:sa3!StringArray', ['3', b'bytes']),
            ('#App:0002:b3!WrongType', 'wrong type'),
        ],
    )
    def test_playbook_string_array_fail(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        try:
            tcex.playbook.create_string_array(variable, value)
            assert False, f'{value} is not a valid String Array value'
        except RuntimeError:
            assert True

    #
    # Type Specific
    #

    @pytest.mark.parametrize(
        'variable,value', [('#App:0002:s1!String', None)],
    )
    def test_playbook_string_none(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        tcex.playbook.create_string(variable, value)
        tcex.playbook.read_string(variable)
        assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'variable,value', [('#App:0003:sa1!StringArray', None)],
    )
    def test_playbook_string_array_none(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        tcex.playbook.create_string_array(variable, value)
        tcex.playbook.read_string_array(variable)
        assert tcex.playbook.read(variable) is None

    def test_playbook_string_read_none(self, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        assert tcex.playbook.read_string(None) is None
