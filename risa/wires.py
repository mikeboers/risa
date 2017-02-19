import logging

from . import config


log = logging.getLogger(__name__)


_mock_pins = {}

def _get(pin):
    
    if config.MOCK_PINS:
        return bool(_mock_pins.get(pin))

    path = '/sys/class/gpio/gpio%d/value' % pin
    return open(path).read().strip() != '0'

def _set(pin, value):

    if config.MOCK_PINS:
        _mock_pins[pin] = bool(value)
        return

    path = '/sys/class/gpio/gpio%d/value' % pin
    with open(path, 'w') as fh:
        fh.write('1' if value else '0')


HOT = 'hot'
COLD = 'cold'
CLOSED = 'closed'


def _assert_sane_valve(valve):
    if valve not in (HOT, COLD, CLOSED):
        raise ValueError('Invalid valve: %s.' % valve)

def _assert_sane_fan(speed):
    if not isinstance(speed, int):
        raise TypeError('Fan speed must be int.')
    if speed < 0 or speed > 3:
        raise ValueError('Fan speed %d out of range (0-3).' % speed)

def _assert_safety(valve, fan):
    if valve != CLOSED and not fan:
        raise ValueError('Cannot have valve open without fan.')


def get_valve():
    # We assume the valve pins are sane.
    if _get(config.PIN_HOT):
        return HOT
    elif _get(config.PIN_COLD):
        return COLD
    else:
        return CLOSED


def set_valve(valve, fan=None, _safe=True, _fix_unsafe=True):

    _assert_sane_valve(valve)

    if _safe and fan is None:
        fan = get_fan()

    # Should check this even if not going for safety.
    if fan is not None:
        _assert_sane_fan(fan)

    if _safe:
        if _fix_unsafe and valve != CLOSED and not fan:
            fan = 1
        _assert_safety(valve, fan)

    if valve == CLOSED:
        _set(config.PIN_HOT, False)
        _set(config.PIN_COLD, False)

    # This is awkwardly placed so that the fans
    # are set after closing the valve, and before
    # opening it.
    if fan is not None:
        set_fan(fan, _safe=False)

    if valve == HOT:
        # Always turn off before on!
        _set(config.PIN_COLD, False)
        _set(config.PIN_HOT, True)

    elif valve == COLD:
        _set(config.PIN_HOT, False)
        _set(config.PIN_COLD, True)


def get_fan():
    # We assume the fan pins are sane.
    pins = (None, config.PIN_FAN1, config.PIN_FAN2, config.PIN_FAN3)
    for i, pin in enumerate(pins):
        if pin and _get(pin):
            return i
    return 0


def set_fan(fan, _safe=True, _fix_unsafe=True):

    _assert_sane_fan(fan)
    pins = (None, config.PIN_FAN1, config.PIN_FAN2, config.PIN_FAN3)

    if _safe:
        valve = get_valve()
        if _fix_unsafe and valve != CLOSED and not fan:
            valve = CLOSED
            set_valve(valve, _safe=False)
        _assert_safety(valve, fan)

    # Turn off the other fan pins first.
    for i, pin in enumerate(pins):
        if pin and fan != i:
            _set(pin, False)

    if fan:
        _set(pins[fan], True)


def set(valve=None, fan=None, _safe=True):
    if valve is None and fan is None:
        raise ValueError('Please specify valve or fan.')
    if valve is not None:
        set_valve(valve, fan, _safe=_safe)
    else:
        set_fan(fan, _safe=_safe)


if __name__ == '__main__':

    import time

    for pin in config.pins():
        print(pin, _get(pin))
        _set(pin, True)
        print(pin, _get(pin))
        time.sleep(0.2)
        _set(pin, False)
        print(pin, _get(pin))
        time.sleep(0.2)
        print()
