"""Test the TcEx Utils Module."""
# first-party
from tcex.utils import Utils


class TestWrapString:
    """Test the TcEx Utils Module."""

    @staticmethod
    def test_1():
        """Test long string with single separator."""
        # flake8: noqa: E501; pylint: disable=line-too-long
        s = '# vv: Build|Difference|Duplicates|Fill|Intersection|Is In|Is Subset|Is Superset|Length|Pop|Reverse|Reverse Sort|Slice|Sort|Sort Lowercase|Symmetric Difference|Unique|Union'

        correct = [
            (
                '# vv: Build|Difference|Duplicates|Fill|Intersection|Is In|Is Subset|Is '
                'Superset|Length|Pop|Reverse|'
            ),
            'Reverse Sort|Slice|Sort|Sort Lowercase|Symmetric Difference|Unique|Union',
        ]

        answer = Utils.wrap_string(s, (' ', '|'))

        assert answer == '\n'.join(correct)

    @staticmethod
    def test_unwrappable():
        """Test long string that can't be wrapped."""
        # flake8: noqa: E501; pylint: disable=line-too-long
        s = '# vv: Build|Difference|Duplicates|Fill|Intersection|Is In|Is Subset|Is Superset|Length|Pop|Reverse|Reverse Sort|Slice|Sort|Sort Lowercase|Symmetric Difference|Unique|Union'

        answer = Utils.wrap_string(s, (','))

        assert answer == s

    @staticmethod
    def test_empty_input():
        """Test empty string input."""
        assert Utils.wrap_string('') == ''

    @staticmethod
    def test_short_input():
        """Test input shorter than length."""
        assert Utils.wrap_string('foobar') == 'foobar'
