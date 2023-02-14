"""Test the TcEx Utils Module."""
# third-party
import pytest

# first-party
from tcex.utils import Utils


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
    def test_utils_camel_to_snake(self, input_, expected):
        """Test **camel_to_snake** method of TcEx Utils module."""
        result = Utils().camel_to_snake(input_)
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
    def test_utils_camel_to_space(self, input_, expected):
        """Test **camel_to_space** method of TcEx Utils module."""
        result = Utils().camel_to_space(input_)
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
    def test_utils_inflect(self, input_, expected):
        """Test **inflect** method of TcEx Utils module."""
        result = Utils().inflect.plural(input_)
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
    def test_utils_to_bool(self, input_, expected):
        """Test **to_bool** method of TcEx Utils module."""
        result = Utils().to_bool(input_)
        assert result == expected, f'Input {input_} result of {result} != {expected}'

    @pytest.mark.parametrize(
        'string_length',
        [(0), (1), (55), (100), (1000)],
    )
    def test_utils_random_string(self, string_length):
        """Test **camel_to_snake** method of TcEx Utils module."""
        result = Utils().random_string(string_length=string_length)
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
    def test_utils_snake_to_camel(self, input_, expected):
        """Test **camel_to_snake** method of TcEx Utils module."""
        result = Utils().snake_to_camel(input_)
        assert result == expected, f'Input {input_} result of {result} != {expected}'

    @pytest.mark.parametrize(
        'input_,length,append_chars,spaces,expected',
        [
            # no truncate, no append, no spaces
            ('short_no_truncate', 20, '', False, 'short_no_truncate'),
            # no truncate, append, no spaces
            ('short_no_truncate', 20, ' ...', False, 'short_no_truncate'),
            # no truncate, append, spaces
            ('short_no_truncate', 20, '', True, 'short_no_truncate'),
            # truncate, no append, no spaces
            ('truncate_string', 5, '', False, 'trunc'),
            # truncate, append, no spaces
            ('truncate_append', 5, ' .', False, 'tru .'),
            # truncate, append, spaces
            ('truncate append spaces', 20, ' .', True, 'truncate append .'),
            # truncate, append, spaces
            ('truncate  double spaces', 20, ' .', True, 'truncate  double .'),
            # return input
            (None, 20, None, False, ''),
            # return input
            ('', 20, None, False, ''),
            # return input
            ('input', None, None, False, 'input'),
            # return input
            ('input', 100, None, False, 'input'),
            # return empty string
            ('input', 0, None, False, ''),
            # return empty string, spaces
            ('input', 2, None, True, ''),
        ],
    )
    def test_utils_truncate_string(self, input_, length, append_chars, spaces, expected):
        """Test **truncate_string** method of TcEx Utils module.

        Args:
            input_ (str): The input string to convert to snake case.
            length (int): The length of the truncated string.
            append_chars (str): Any character that should be appended to the
                string. Typically used for ellipsis (e.g. ...).
            spaces (bool): If True truncation will be done at the
                nearest space before the truncation length to avoid chopping words.
            expected (str): The expected result value.
        """
        result = Utils().truncate_string(input_, length, append_chars, spaces)
        assert result == expected, f'Input {input_} result of {result} != {expected}'
