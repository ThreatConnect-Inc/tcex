# -*- coding: utf-8 -*-
"""Decrypt file params"""
import ctypes.util
from ctypes import (
    Structure,
    byref,
    c_char_p,
    c_int,
    c_ubyte,
    c_ulong,
    c_void_p,
    cdll,
    create_string_buffer,
)


class EVP_Context(Structure):  # pylint: disable=invalid-name,too-few-public-methods
    """Generates a EVP context object, which is the following C struct:

        struct evp_cipher_ctx_st {
            const EVP_CIPHER *cipher;
            ENGINE *engine;             /* functional reference if 'cipher' is
                                        * ENGINE-provided */
            int encrypt;                /* encrypt or decrypt */
            int buf_len;                /* number we have left */
            unsigned char oiv[EVP_MAX_IV_LENGTH]; /* original iv */
            unsigned char iv[EVP_MAX_IV_LENGTH]; /* working iv */
            unsigned char buf[EVP_MAX_BLOCK_LENGTH]; /* saved partial block */
            int num;                    /* used by cfb/ofb/ctr mode */
            void *app_data;             /* application stuff */
            int key_len;                /* May change for variable length cipher */
            unsigned long flags;        /* Various flags */
            void *cipher_data;          /* per EVP data */
            int final_used;
            int block_mask;
            unsigned char final[EVP_MAX_BLOCK_LENGTH]; /* possible final block */
        }

        None of these fields are used in this module, but declaring them
        in this manner makes sure the structure is the proper size (something
        like 184 bytes long)
    """

    _fields_ = [
        ('cipher', c_void_p),
        ('engine', c_void_p),
        ('buf_len', c_int),
        ('oiv', c_ubyte * 16),
        ('iv', c_ubyte * 16),
        ('buf', c_ubyte * 32),
        ('num', c_int),
        ('app_data', c_void_p),
        ('key_len', c_int),
        ('flags', c_ulong),
        ('cipher_data', c_void_p),
        ('final_used', c_int),
        ('block_mask', c_int),
        ('final', c_ubyte * 32),
    ]


class FileParams:  # pylint: disable=useless-object-inheritance
    """File parameter decoder"""

    def __init__(self):
        """Open up the library with ctypes"""
        self.libssl = cdll.LoadLibrary(ctypes.util.find_library('ssl'))
        self._ctx = EVP_Context()
        self.ctx = byref(self._ctx)

        # OpenSSL 1.0.x must be initialized
        if hasattr(self.libssl, 'SSL_library_init'):
            self.libssl.SSL_library_init()  # v1.0
            self.libssl.SSL_load_error_strings()
            self.libssl.OPENSSL_add_all_algorithms_noconf()

        self.libssl.EVP_aes_128_ecb.restype = c_void_p
        self.libssl.EVP_aes_128_cbc.restype = c_void_p

    def EVP_aes_128_ecb(self):  # pylint: disable=invalid-name
        """Find the AES-128-ECB cipher suite"""
        return c_void_p(self.libssl.EVP_aes_128_ecb())  # pragma: no cover

    def EVP_aes_128_cbc(self):  # pylint: disable=invalid-name
        """Find the AES-128-CBC cipher suite"""
        return c_void_p(self.libssl.EVP_aes_128_cbc())

    def EVP_DecryptInit(self, cipher_type, key, iv):  # pylint: disable=invalid-name
        """Start decrypting with a cipher, key, and initial vector"""
        assert self.libssl.EVP_DecryptInit(self.ctx, cipher_type, c_char_p(key), c_char_p(iv)) == 1

    def EVP_DecryptUpdate(self, data):  # pylint: disable=invalid-name
        """ Update the encryption in progress """
        datalen = len(data)
        inlen = c_int(datalen)
        outlen = c_int(datalen * 2)
        out = create_string_buffer(datalen * 2)
        assert (
            self.libssl.EVP_DecryptUpdate(
                self.ctx, byref(out), byref(outlen), c_char_p(data), inlen
            )
            == 1
        )

        return out.raw[: outlen.value]

    def EVP_DecryptFinal(self):  # pylint: disable=invalid-name
        """Finalize the encryption (append this to prior DecryptUpdates)"""
        out = create_string_buffer(4096)
        outlen = c_int(4096)
        assert self.libssl.EVP_DecryptFinal(self.ctx, byref(out), byref(outlen)) == 1
        return out.raw[: outlen.value]

    def EVP_EncryptInit(self, cipher_type, key, iv):  # pylint: disable=invalid-name
        """Start Encrypting with a cipher, key, and initial vector"""
        assert self.libssl.EVP_EncryptInit(self.ctx, cipher_type, c_char_p(key), c_char_p(iv)) == 1

    def EVP_EncryptUpdate(self, data):  # pylint: disable=invalid-name
        """Update the encryption in progress"""
        datalen = len(data)
        inlen = c_int(datalen)
        outlen = c_int(datalen * 2)
        out = create_string_buffer(datalen * 2)
        assert (
            self.libssl.EVP_EncryptUpdate(
                self.ctx, byref(out), byref(outlen), c_char_p(data), inlen
            )
            == 1
        )

        return out.raw[: outlen.value]

    def EVP_EncryptFinal(self):  # pylint: disable=invalid-name
        """Finalize the encryption (append this to prior EncryptUpdates)"""
        out = create_string_buffer(4096)
        outlen = c_int(4096)
        assert self.libssl.EVP_EncryptFinal(self.ctx, byref(out), byref(outlen)) == 1
        return out.raw[: outlen.value]
