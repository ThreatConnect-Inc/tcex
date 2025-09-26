"""TestAesOperation for AES encryption/decryption operations.

Test suite for the AesOperation utility class that handles AES CBC encryption and
decryption operations.

Classes:
    TestAesOperation: Test suite for AES operations

TcEx Module Tested: tcex.util.aes_operation
"""


import pytest


from tcex.util.aes_operation import AesOperation


class TestAesOperation:
    """TestAesOperation for AES encryption/decryption operations.

    Test suite for the AesOperation utility class that handles AES CBC encryption and
    decryption operations.

    Parameters:
        aes_operations: Instance of AesOperation class for testing
    """

    aes_operations = AesOperation()

    @pytest.mark.parametrize(
        'key,ciphertext,iv,expected',
        [
            pytest.param(
                # iv of None
                'ajfmuyodhscwegea',
                b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n',
                None,
                b'blah',
                id='pass-iv-none',
            ),
            pytest.param(
                # iv of bytes
                'ajfmuyodhscwegea',
                b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n',
                b'\0' * 16,
                b'blah',
                id='pass-iv-bytes',
            ),
            pytest.param(
                # iv of string
                'ajfmuyodhscwegea',
                b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n',
                '\0' * 16,
                b'blah',
                id='pass-iv-string',
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
        """Test AES CBC decryption with various IV types.

        Test case for decrypting AES CBC encrypted data using different initialization
        vector formats. Verifies that decryption works correctly with None, bytes, and
        string IV values.

        Parameters:
            key: Encryption key for AES operation
            ciphertext: Encrypted data to decrypt
            iv: Initialization vector (None, bytes, or string)
            expected: Expected decrypted plaintext
        """
        decrypted_data = self.aes_operations.decrypt_aes_cbc(key, ciphertext, iv)
        assert decrypted_data == expected

    @pytest.mark.parametrize(
        'key,plaintext,iv,expected',
        [
            pytest.param(
                # iv of None
                'ajfmuyodhscwegea',
                'blah',
                None,
                b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n',
                id='pass-iv-none',
            ),
            pytest.param(
                # iv of bytes
                'ajfmuyodhscwegea',
                'blah',
                b'\0' * 16,
                b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n',
                id='pass-iv-bytes',
            ),
            pytest.param(
                # iv of string
                'ajfmuyodhscwegea',
                'blah',
                '\0' * 16,
                b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n',
                id='pass-iv-string',
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
        """Test AES CBC encryption with various IV types.

        Test case for encrypting plaintext data using AES CBC encryption with different
        initialization vector formats. Verifies that encryption works correctly with None,
        bytes, and string IV values.

        Parameters:
            key: Encryption key for AES operation
            plaintext: Data to encrypt
            iv: Initialization vector (None, bytes, or string)
            expected: Expected encrypted ciphertext
        """
        encrypted_data = self.aes_operations.encrypt_aes_cbc(key, plaintext, iv)
        assert encrypted_data == expected
