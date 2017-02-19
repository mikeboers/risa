import ast
import logging
import os
import re

log = logging.getLogger(__name__)


# === DEFAULT VALUES

# For all crypto operations.
SECRET = b'monkey'
DEVICE_NAME = 'unnamed'

BROADCAST_PORT = 31415

# Sensor stuff.
SENSOR_INTERVAL = 10

LOG_LEVEL = logging.INFO

PIN_HEAT  = 19 # "W"
PIN_COOL = 16 # "Y"
PIN_FAN1 = 26 # "G"
PIN_FAN2 = 20 # "G2"
PIN_FAN3 = 21 # "G3"

GPIO_GROUP = 'gpio'

# For testing.
MOCK_PINS = False


# Read the configfile.
path = os.environ.get('RISA_CONFIG', '/etc/risa')
if os.path.exists(path):
    local = {}
    try:
        exec(open(path).read(), globals(), local)
    except:
        log.exception('error while loading %s' % path)
    else:
        for key, value in local.items():
            if re.match(r'^[A-Z][A-Z_]*$', key):
                globals()[key] = value


# Pull in envvars.
for key, value in os.environ.items():
    m = re.match(r'^RISA_([A-Z][A-Z_]*)$', key)
    if m:
        try:
            value = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            pass
        globals()[m.group(1)] = value


# Summarize some stuff.
def pins():
    return (PIN_HEAT, PIN_COOL, PIN_FAN1, PIN_FAN2, PIN_FAN3)


if SECRET == b'monkey':
    log.warning('You should set SECRET')
if isinstance(SECRET, str):
    SECRET = SECRET.encode('ascii')

if DEVICE_NAME == 'unnamed':
    log.warning('You should set DEVICE_NAME')
