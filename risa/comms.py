import socket
import json
import logging
import time

from . import config
from . import crypto


log = logging.getLogger(__name__)


def send_broadcast(msg):

    msg = dict(msg)
    if not msg.get('type'):
        raise ValueError('messages need types', msg)
    msg.setdefault('device', config.DEVICE_NAME)
    msg.setdefault('time', time.time())

    serialized = json.dumps(msg, sort_keys=True, separators=(',', ':'))
    log.debug('send_broadcast(**%s)' % serialized)

    signed = crypto.sign(serialized)
    if len(signed) > 1024:
        log.warning('message is %d bytes' % len(signed))

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(signed.encode('utf8'), ('255.255.255.255', config.BROADCAST_PORT))



def iter_broadcasts():

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', config.BROADCAST_PORT))

    while True:

        raw, addr = s.recvfrom(8192)
        try:
            serialized = crypto.verify(raw)
        except ValueError as e:
            log.warning('verify failed: %s on %r' % (e, raw))
            continue

        #log.debug('iter_broadcasts(); %s:%s -> %s' % (addr[0], addr[1], serialized))

        try:
            msg = json.loads(serialized)
        except Exception as e:
            log.warning('deserialization failed: %s on %r' % (e, serialized))

        yield msg




