"""TcEx Utilities AES Operations Module"""
# standard library
from typing import Optional, Union

# third-party
import pyaes


class AesOperations:
    """TcEx Utilities AES Operations Class"""

    @staticmethod
    def decrypt_aes_cbc(
        key: bytes, ciphertext: Union[bytes, str], iv: Optional[bytes] = None
    ) -> bytes:
        """Return AES CBC decrypted string.

        Args:
            key: The encryption key.
            ciphertext: The ciphertext to decrypt.
            iv: The CBC initial vector.
        """
        iv = iv or b'\0' * 16

        # ensure key is bytes
        if isinstance(key, str):
            key = key.encode()

        # ensure iv is bytes
        if isinstance(iv, str):
            iv = iv.encode()

        aes_cbc_decrypt = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, iv=iv))
        decrypted = aes_cbc_decrypt.feed(ciphertext)
        decrypted += aes_cbc_decrypt.feed()
        return decrypted

    @staticmethod
    def encrypt_aes_cbc(
        key: bytes, plaintext: Union[bytes, str], iv: Optional[bytes] = None
    ) -> bytes:
        """Return AES CBC encrypted string.

        Args:
            key: The encryption key.
            plaintext: The text to encrypt.
            iv: The CBC initial vector.
        """
        iv = iv or b'\0' * 16

        # ensure key is bytes
        if isinstance(key, str):
            key = key.encode()

        # ensure plaintext is bytes
        if isinstance(plaintext, str):
            plaintext = plaintext.encode()

        # ensure iv is bytes
        if isinstance(iv, str):
            iv = iv.encode()

        aes_cbc_encrypt = pyaes.Encrypter(pyaes.AESModeOfOperationCBC(key, iv=iv))
        encrypted = aes_cbc_encrypt.feed(plaintext)
        encrypted += aes_cbc_encrypt.feed()
        return encrypted
