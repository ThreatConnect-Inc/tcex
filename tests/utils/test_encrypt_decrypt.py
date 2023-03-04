"""Test the TcEx Utils Module."""
# first-party
from tcex.utils import Utils


class TestBool:
    """Test the TcEx Utils Module."""

    @staticmethod
    def test_utils_encrypt():
        """Test Case"""
        key = 'ajfmuyodhscwegea'
        plaintext = 'blah'
        encrypted_data = Utils().encrypt_aes_cbc(key, plaintext)

        assert encrypted_data == b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n'

    @staticmethod
    def test_utils_encrypt_iv_string():
        """Test Case"""
        key = 'ajfmuyodhscwegea'
        plaintext = 'blah'
        encrypted_data = Utils().encrypt_aes_cbc(key, plaintext, iv='\0' * 16)  # type: ignore

        assert encrypted_data == b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n'

    @staticmethod
    def test_utils_decrypt():
        """Test Case"""
        key = 'ajfmuyodhscwegea'
        ciphertext = b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n'
        decrypted_data = Utils().decrypt_aes_cbc(key, ciphertext)

        assert decrypted_data.decode() == 'blah'

    @staticmethod
    def test_utils_decrypt_iv_string():
        """Test Case"""
        key = 'ajfmuyodhscwegea'
        ciphertext = b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n'
        decrypted_data = Utils().decrypt_aes_cbc(key, ciphertext, iv='\0' * 16)  # type: ignore

        assert decrypted_data.decode() == 'blah'
