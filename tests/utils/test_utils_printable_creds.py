"""Test Suite"""
# third-party
import pytest

# first-party
from tcex.utils import Utils


class TestUtilsPrintableCreds:
    """Test Suite"""

    utils = Utils()

    @pytest.mark.parametrize(
        'cred,visible,mask_char,mask_char_count,expected',
        [
            ('my_secret_password', 1, '*', 4, 'm****d'),
            ('my_secret_password', 1, '!', 10, 'm!!!!!!!!!!d'),
            ('my_secret_password', 0, '*', 4, 'm****d'),
            ('my_secret_password', 2, '*', 4, 'my****rd'),
        ],
    )
    def test_utils_remove_none(
        self,
        cred: str,
        visible: int,
        mask_char: str,
        mask_char_count: int,
        expected: str,
    ):
        """Test Case"""
        printable_cred = self.utils.printable_cred(cred, visible, mask_char, mask_char_count)
        assert printable_cred == expected, f'{printable_cred} != {expected}'
