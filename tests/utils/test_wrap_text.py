"""Test the TcEx Utils Module."""
# first-party
from tcex.utils import Utils


class TestWrapText:
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
