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

