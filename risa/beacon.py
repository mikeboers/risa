import threading
import logging

from . import comms


log = logging.getLogger(__name__)


_thread = None
_ping_extra = {}
def start(ping_extra):
    global _thread
    if not _thread:
        _thread = threading.Thread(target=_target)
        _thread.start()
    _ping_extra.update(ping_extra)
    return _thread


_handlers = {}
def handler(name):
    def _handler(func):
        _handlers[name] = func
        return func
    return _handler


@handler('ping')
def on_ping(ping):
    pong = ping.copy()
    pong['type'] = 'pong'
    ping['in_reply_to'] = ping['device']
    pong.update(_ping_extra)
    comms.send_broadcast(pong)


def _target():
    for msg in comms.iter_broadcasts():
        handler = _handlers.get(msg.get('type'))
        if not handler:
            continue
        try:
            handler(msg)
        except Exception as e:
            log.exception('error in beacon during %r' % msg)


