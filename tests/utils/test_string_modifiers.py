# -*- coding: utf-8 -*-
"""Test the TcEx Utils Module."""
import pytest


# pylint: disable=no-self-use
class TestStringModifiers:
    """Test the TcEx Utils Module."""

    @pytest.mark.parametrize(
        'input_,expected',
        [
            ('UpperUpper', 'upper_upper'),
            ('lowerUpper', 'lower_upper'),
            ('lowerlower', 'lowerlower'),
            ('Upper', 'upper'),
        ],
    )
    def test_utils_camel_to_snake(self, tcex, input_, expected):
        """Test **camel_to_snake** method of TcEx Utils module.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
            input_ (str): The input string to convert to snake case.
            expected (str): The expected result value.
        """
        result = tcex.utils.camel_to_snake(input_)
        assert result == expected, f'Input {input_} result of {result} != {expected}'

    @pytest.mark.parametrize(
        'input_,expected',
        [
            ('UpperUpper', 'upper upper'),
            ('lowerUpper', 'lower upper'),
            ('lowerlower', 'lowerlower'),
            ('Upper', 'upper'),
        ],
    )
    def test_utils_camel_to_space(self, tcex, input_, expected):
        """Test **camel_to_space** method of TcEx Utils module.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
            input_ (str): The input string to convert to snake case.
            expected (str): The expected result value.
        """
        result = tcex.utils.camel_to_space(input_)
        assert result == expected, f'Input {input_} result of {result} != {expected}'

    @pytest.mark.parametrize(
        'input_,expected',
        [
            ('adversary', 'adversaries'),
            ('Campaign', 'Campaigns'),
            ('Document', 'Documents'),
            ('Email', 'Emails'),
            ('Event', 'Events'),
            ('Incident', 'Incidents'),
            ('Intrusion Set', 'Intrusion Sets'),
            ('Report', 'Reports'),
            ('Signature', 'Signatures'),
            ('Task', 'Tasks'),
            ('Threat', 'Threats'),
        ],
    )
    def test_utils_inflect(self, tcex, input_, expected):
        """Test **inflect** method of TcEx Utils module.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
            input_ (str): The string to "inflect".
            expected (str): The expected results.
        """
        result = tcex.utils.inflect.plural(input_)
        assert result == expected, f'Input {input_} result of {result} != {expected}'

    @pytest.mark.parametrize(
        'input_,expected',
        [
            ('true', True),
            ('1', True),
            (1, True),
            (True, True),
            ('false', False),
            ('0', False),
            (0, False),
            (False, False),
        ],
    )
    def test_utils_to_bool(self, tcex, input_, expected):
        """Test **to_bool** method of TcEx Utils module.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
            input_ (str): The input string to convert to bool.
            expected (bool): The expected boolean value.
        """
        result = tcex.utils.to_bool(input_)
        assert result == expected, f'Input {input_} result of {result} != {expected}'

    @pytest.mark.parametrize(
        'string_length', [(0), (1), (55), (100), (1000)],
    )
    def test_utils_random_string(self, tcex, string_length):
        """Test **camel_to_snake** method of TcEx Utils module.

        Args:
            string_length (int): The length of the random string.
        """
        result = tcex.utils.random_string(string_length=string_length)
        assert (
            len(result) == string_length
        ), f'The length of the string {len(result)} != {string_length}'

    @pytest.mark.parametrize(
        'input_,expected',
        [
            ('upper_upper', 'upperUpper'),
            ('lower_upper', 'lowerUpper'),
            ('lowerlower', 'lowerlower'),
            ('upper', 'upper'),
        ],
    )
    def test_utils_snake_to_camel(self, tcex, input_, expected):
        """Test **camel_to_snake** method of TcEx Utils module.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
            input_ (str): The input string to convert to snake case.
            expected (str): The expected result value.
        """
        result = tcex.utils.snake_to_camel(input_)
        assert result == expected, f'Input {input_} result of {result} != {expected}'
