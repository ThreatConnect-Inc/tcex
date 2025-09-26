"""TestUtilPrintableCred for testing credential masking utility functions.

This module contains comprehensive test cases for the Util.printable_cred method,
which handles masking of sensitive credential strings with configurable visible characters
and mask patterns for secure display purposes.

Classes:
    TestUtilPrintableCred: Test suite for credential masking functionality

TcEx Module Tested: tcex.util
"""


import pytest


from tcex.util import Util


class TestUtilPrintableCred:
    """TestUtilPrintableCred for testing credential masking utility functions.

    This test class provides comprehensive test coverage for the Util.printable_cred method,
    which masks sensitive credential strings while preserving specified visible characters
    at the beginning and end, using configurable mask characters and counts.
    """

    @pytest.mark.parametrize(
        'cred,visible,mask_char,mask_char_count,expected',
        [
            pytest.param(
                'my_secret_password', 1, '*', 4, 'm****d', id='pass-single-visible-asterisk-mask'
            ),
            pytest.param(
                'my_secret_password',
                1,
                '!',
                10,
                'm!!!!!!!!!!d',
                id='pass-single-visible-exclamation-mask',
            ),
            pytest.param(
                'my_secret_password', 0, '*', 4, 'm****d', id='pass-zero-visible-asterisk-mask'
            ),  # Note: appears to show 1 char anyway
            pytest.param(
                'my_secret_password', 2, '*', 4, 'my****rd', id='pass-double-visible-asterisk-mask'
            ),
        ],
    )
    def test_printable_cred(
        self,
        cred: str,
        visible: int,
        mask_char: str,
        mask_char_count: int,
        expected: str,
    ) -> None:
        """Test the printable_cred method with various credential masking configurations.

        This test validates the masking of credential strings with different configurations
        for visible character count, mask characters, and mask character counts to ensure
        proper credential obfuscation while maintaining readability.
        """
        printable_cred = Util.printable_cred(cred, visible, mask_char, mask_char_count)
        assert printable_cred == expected, f'{printable_cred} != {expected}'
