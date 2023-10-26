"""
OTP generation code to protect from unwanted parties sending emails out.

References:
https://github.com/tadeck/onetimepass (MIT)
https://stackoverflow.com/a/8549884/703462
"""

from hmac import new as hmac_new
from base64 import b32decode, b32encode
from struct import pack, unpack
from hashlib import sha1
from time import time
from random import randint

def get_hotp_token(secret, intervals_no):
    """
    HMAC-based One-Time Password generator, which is changed with each call,
    in compliance to RFC4226.
    """
    key = b32decode(secret, True)
    # Decoding our key
    msg = pack(">Q", intervals_no)
    # Conversions between Python values and C structs representation
    h = hmac_new(key, msg, sha1).digest()
    o = o = h[19] & 15
    # Generate a hash using both of these. Hashing algorithm is HMAC
    h = (unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
    # Unpacking
    return h

def get_totp_token(secret: str):
    """
    Example:

        # Base 32 encoded key
        secret = 'MNUGC2DBGBZQ===='
        print(get_totp_token(secret))
    """
    # Ensuring to give the same otp for 30 seconds
    x = str(get_hotp_token(secret, intervals_no=int(time())//30))
    # Adding 0 in the beginning until OTP has 6 digits
    while len(x) != 6:
        x += '0'
    return x

def secret_generator():
    """
    Base32 secret generator for get_totp_token.
    Used to generate the secret, shared by client and server.
    """
    return b32encode(''.join(chr(randint(0, 127)) for _ in range(9)).encode('ascii'))

def gen_otp_from_secret_file(secret_path: str):
    """
    Generates the OTP given a secret file path.
    """
    secret = None
    with open(secret_path, 'r', encoding='ascii') as secret_file:
        secret = secret_file.read()
    return get_totp_token(secret)
