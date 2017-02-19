import logging

from . import config


log = logging.getLogger(__name__)


_mock_pins = {}

def _get_pin(pin):
    
    if config.MOCK_PINS:
        return bool(_mock_pins.get(pin))

    path = '/sys/class/gpio/gpio%d/value' % pin
    return open(path).read().strip() != '0'

def _set_pin(pin, value):

    if config.MOCK_PINS:
        _mock_pins[pin] = bool(value)
        return

    path = '/sys/class/gpio/gpio%d/value' % pin
    with open(path, 'w') as fh:
        fh.write('1' if value else '0')


HEAT = 'heat'
COOL = 'cool'
CLOSED = 'closed'


def _assert_sane_valve(valve):
    if valve not in (HEAT, COOL, CLOSED):
        raise ValueError('Invalid valve: %s.' % valve)

def _assert_sane_fan(speed):
    if not isinstance(speed, int):
        raise TypeError('Fan speed must be int.')
    if speed < 0 or speed > 3:
        raise ValueError('Fan speed %d out of range (0-3).' % speed)

def _fix_unsafe_valve(valve, fan):
    # Disable the valve of the fan is off.
    if valve != CLOSED and not fan:
        return CLOSED, 0
    else:
        return valve, fan

def _fix_unsafe_fan(valve, fan):
    # Turn on the fan if we are opening the valve.
    if valve != CLOSED and not fan:
        return valve, 1
    else:
        return valve, fan

def _assert_safety(valve, fan):
    if valve != CLOSED and not fan:
        raise ValueError('Cannot have valve open without fan.')


def get_valve():
    # We assume the valve pins are sane.
    if _get_pin(config.PIN_HEAT):
        return HEAT
    elif _get_pin(config.PIN_COOL):
        return COOL
    else:
        return CLOSED

def get_fan():
    # We assume the fan pins are sane.
    pins = (None, config.PIN_FAN1, config.PIN_FAN2, config.PIN_FAN3)
    for i, pin in enumerate(pins):
        if pin and _get_pin(pin):
            return i
    return 0

def get():
    return get_valve(), get_fan()


def set(valve=None, fan=None, safe=True, fix_unsafe=True):

    given_valve = valve is not None
    given_fan = fan is not None

    if not given_valve and not given_fan:
        raise TypeError('Provide valve or fan.')

    if given_valve:
        _assert_sane_valve(valve)
    if given_fan:
        _assert_sane_fan(fan)

    if not given_valve:
        valve = get_valve()
        if fix_unsafe:
            valve, fan = _fix_unsafe_valve(valve, fan)
    elif not given_fan:
        fan = get_fan()
        if fix_unsafe:
            valve, fan = _fix_unsafe_fan(valve, fan)

    _assert_sane_valve(valve)
    _assert_sane_fan(fan)
    if safe:
        _assert_safety(valve, fan)

    if valve == CLOSED:
        _set_pin(config.PIN_HEAT, False)
        _set_pin(config.PIN_COOL, False)

    # This is awkwardly placed so that the fans
    # are set after closing the valve, and before
    # opening it.
    fan_pins = (None, config.PIN_FAN1, config.PIN_FAN2, config.PIN_FAN3)
    for i, pin in enumerate(fan_pins):
        if pin and fan != i:
            _set_pin(pin, False)
    if fan:
        _set_pin(fan_pins[fan], True)

    if valve == HEAT:
        # Always turn off before on!
        _set_pin(config.PIN_COOL, False)
        _set_pin(config.PIN_HEAT, True)

    elif valve == COOL:
        _set_pin(config.PIN_HEAT, False)
        _set_pin(config.PIN_COOL, True)

    return valve, fan


