"""Test the TcEx Utils Module."""
# first-party
from tcex.utils import Utils


class TestWrapString:
    """Test the TcEx Utils Module."""

    @staticmethod
    def test_happy_path():
        """Test long string with single separator."""
        s = (
            '# vv: Build|Difference|Duplicates|Fill|Intersection|Is In|Is Subset|Is Superset'
            '|Length|Pop|Reverse|Reverse Sort|Slice|Sort|Sort Lowercase|Symmetric Difference'
            '|Unique|Union'
        )

        correct = [
            (
                '# vv: Build|Difference|Duplicates|Fill|Intersection|Is In|Is Subset|Is Superset'
                '|Length|Pop|Reverse|'
            ),
            'Reverse Sort|Slice|Sort|Sort Lowercase|Symmetric Difference|Unique|Union',
        ]

        answer = Utils.wrap_string(s, [' ', '|'])

        assert answer == '\n'.join(correct)

    @staticmethod
    def test_wrapping():
        """Test long string that can't be wrapped."""
        # flake8: noqa: E501; pylint: disable=line-too-long

        s = (
            '# vv: Build|Difference|Duplicates|Fill|Intersection|Is In|Is Subset|Is Superset|'
            'Length|Pop|Reverse|Reverse Sort|Slice|Sort|Sort Lowercase|Symmetric Difference|Unique'
            '|Union'
        )

        answer = Utils.wrap_string(s, [','], force_wrap=False)
        assert answer == s

        answer = Utils.wrap_string(s, [','], force_wrap=True)
        expected = [str(s[:100]), str(s[100:])]
        assert answer == '\n'.join(expected)

    @staticmethod
    def test_empty_input():
        """Test empty string input."""
        assert Utils.wrap_string('') == ''

    @staticmethod
    def test_short_input():
        """Test input shorter than length."""
        assert Utils.wrap_string('foobar') == 'foobar'
