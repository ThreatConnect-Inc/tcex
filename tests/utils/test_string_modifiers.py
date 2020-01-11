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
