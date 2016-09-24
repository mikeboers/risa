import hmac
import hashlib
import os
import binascii

from . import config


def sign(message):
    encoded = message.encode('utf8')
    salt = binascii.hexlify(os.urandom(8))
    sig = hmac.new(config.SECRET, encoded + salt, hashlib.sha256).hexdigest()
    return '%s:%s:%s' % (message, salt.decode(), sig)


def verify(signed):
    
    try:
        encoded, salt, old_sig = signed.rsplit(':', 2)
    except ValueError:
        raise ValueError('malformed signature')

    new_sig = hmac.new(config.SECRET, encoded + salt, hashlib.sha256).hexdigest()
    if new_sig != old_sig:
        raise ValueError('invalid signature')

    return encoded.decode('utf8')

