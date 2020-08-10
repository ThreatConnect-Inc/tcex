"""Test the TcEx Utils Module."""


# pylint: disable=no-self-use
class TestBool:
    """Test the TcEx Utils Module."""

    def test_utils_encrypt(self, tcex):
        """Test writing a temp file to disk.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        key = 'ajfmuyodhscwegea'
        plaintext = 'blah'
        encrypted_data = tcex.utils.encrypt_aes_cbc(key, plaintext)

        assert encrypted_data == b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n'

    def test_utils_encrypt_iv_string(self, tcex):
        """Test writing a temp file to disk.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        key = 'ajfmuyodhscwegea'
        plaintext = 'blah'
        encrypted_data = tcex.utils.encrypt_aes_cbc(key, plaintext, iv='\0' * 16)

        assert encrypted_data == b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n'

    def test_utils_decrypt(self, tcex):
        """Test writing a temp file to disk.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        key = 'ajfmuyodhscwegea'
        ciphertext = b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n'
        decrypted_data = tcex.utils.decrypt_aes_cbc(key, ciphertext)

        assert decrypted_data.decode() == 'blah'

    def test_utils_decrypt_iv_string(self, tcex):
        """Test writing a temp file to disk.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        key = 'ajfmuyodhscwegea'
        ciphertext = b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n'
        decrypted_data = tcex.utils.decrypt_aes_cbc(key, ciphertext, iv='\0' * 16)

        assert decrypted_data.decode() == 'blah'
