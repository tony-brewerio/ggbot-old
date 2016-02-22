from __future__ import absolute_import, division, print_function, unicode_literals

import ctypes
import ctypes.util
import functools

from Crypto.Cipher import AES
from django.conf import settings

RSA_PKCS1_PADDING = 1


def rsa_encrypt(ssl, rsa_key, rsa_size, message):
    encrypted = ctypes.create_string_buffer(rsa_size)
    encrypted_bytes = ssl.RSA_private_encrypt(len(message), message, encrypted, rsa_key, RSA_PKCS1_PADDING)
    if encrypted_bytes != rsa_size:
        raise Exception(u"failed to encrypt the message")
    return encrypted.raw


def rsa_create_encrypter(gkey):
    """
    Creates function that will encrypt messages with private key.
    Uses ctypes, since  pycrypto/pyrsa deliberately won't let me encrypt with private key.
    M2Crypto has this function, but it looks like its a dead project.
    So in the end, I decided to directly call opennsl library functions with ctypes.
    """
    ssl = ctypes.CDLL(
        ctypes.util.find_library('libeay32') or ctypes.util.find_library('ssl'),
        use_errno=True, use_last_error=True
    )
    libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True, use_last_error=True)
    libc.fopen.restype = ctypes.c_void_p
    ssl.PEM_read_RSAPrivateKey.restype = ctypes.c_void_p
    file_pointer = libc.fopen(gkey, 'rb')
    if file_pointer is None:
        raise Exception('could not open file containing garena rsa key')
    try:
        rsa_key = ssl.PEM_read_RSAPrivateKey(file_pointer, None, None, None)
        if rsa_key is None:
            raise Exception('could not load garena rsa key')
        return functools.partial(rsa_encrypt, ssl, rsa_key, ssl.RSA_size(rsa_key))
    finally:
        libc.fclose(file_pointer)


def split_by(seq, length):
    return [seq[i:i + length] for i in xrange(0, len(seq), length)]


def django_encrypt(plaintext, iv):
    plaintext = plaintext.ljust(len(plaintext) + 16 - len(plaintext) % 16, b'\0')
    return AES.new(settings.SECRET_KEY[:32], mode=AES.MODE_CBC, IV=iv).encrypt(plaintext)


def django_decrypt(ciphertext, iv):
    return AES.new(settings.SECRET_KEY[:32], mode=AES.MODE_CBC, IV=iv).decrypt(ciphertext).rstrip(b'\0')
