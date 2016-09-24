import socket
import json
import logging
import time

from . import config
from . import crypto


log = logging.getLogger(__name__)


def send_broadcast(**kw):

    if not kw.get('type'):
        raise ValueError('messages need types', kw)
    kw.setdefault('device', config.DEVICE_NAME)
    kw.setdefault('time', time.time())
    
    msg = json.dumps(kw, sort_keys=True, separators=(',', ':'))
    log.debug('send_broadcast(**%s)' % msg)

    signed = crypto.sign(msg)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(signed.encode('utf8'), ('255.255.255.255', config.BROADCAST_PORT))

