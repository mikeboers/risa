from __future__ import print_function

import os
import logging
import re

log = logging.getLogger(__name__)


_bus_path = None
def get_bus_path():
    global _bus_path
    if _bus_path:
        return _bus_path

    device_dir = '/sys/bus/w1/devices'
    for name in os.listdir(device_dir):

        # So far, the themometers have all started with 28-.
        # In the future, we might need to be smarter about it...
        if not name.startswith('28-'):
            continue

        path = os.path.join(device_dir, name, 'w1_slave')
        if os.path.exists(path):
            break

        log.warning('28-* w1 device is missing w1_slave')
        continue

    else:
        # We didn't find anything!
        raise ValueError('could not find sensor')

    _bus_path = path
    return path


def get_temp():

    path = get_bus_path()
    with open(path, 'rb') as fh:
        raw = fh.read().decode('ascii')

    if 'YES' not in raw:
        raise ValueError('sensor data not "YES"', raw)

    m = re.search(r't=(-?\d+)', raw)
    if not m:
        raise ValueError('could not parse raw sensor', raw)

    return float(m.group(1)) / 1000
    



if __name__ == '__main__':

    print(get_temp())