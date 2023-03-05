"""Test Suite"""
# third-party
import pytest

# first-party
from tcex.utils.aes_operations import AesOperations


class TestAesOperations:
    """Test Suite"""

    aes_operations = AesOperations()

    @pytest.mark.parametrize(
        'key,ciphertext,iv,expected',
        [
            (
                # iv of None
                'ajfmuyodhscwegea',
                b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n',
                None,
                b'blah',
            ),
            (
                # iv of bytes
                'ajfmuyodhscwegea',
                b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n',
                b'\0' * 16,
                b'blah',
            ),
            (
                # iv of string
                'ajfmuyodhscwegea',
                b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n',
                '\0' * 16,
                b'blah',
            ),
        ],
    )
    def test_decrypt_aes_cbc(
        self,
        key: bytes | str,
        ciphertext: bytes | str,
        iv: bytes | str | None,
        expected: bytes,
    ):
        """Test Case"""
        decrypted_data = self.aes_operations.decrypt_aes_cbc(key, ciphertext, iv)
        assert decrypted_data == expected

    @pytest.mark.parametrize(
        'key,plaintext,iv,expected',
        [
            (
                # iv of None
                'ajfmuyodhscwegea',
                'blah',
                None,
                b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n',
            ),
            (
                # iv of bytes
                'ajfmuyodhscwegea',
                'blah',
                b'\0' * 16,
                b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n',
            ),
            (
                # iv of string
                'ajfmuyodhscwegea',
                'blah',
                '\0' * 16,
                b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n',
            ),
        ],
    )
    def test_encrypt_aes_cbc(
        self,
        key: bytes | str,
        plaintext: bytes | str,
        iv: bytes | str | None,
        expected: bytes,
    ):
        """Test Case"""
        encrypted_data = self.aes_operations.encrypt_aes_cbc(key, plaintext, iv)
        assert encrypted_data == expected
