import logging
import os
import re
import ast

log = logging.getLogger(__name__)


# === DEFAULT VALUES

# For all crypto operations.
SECRET = b'monkey'
DEVICE_NAME = 'unnamed'

BROADCAST_PORT = 31415

# Sensor stuff.
SENSOR_INTERVAL = 10

LOG_LEVEL = logging.DEBUG




# Read the configfile.
path = os.environ.get('RISA_CONFIG', '/etc/risa')
if os.path.exists(path):
    local = {}
    try:
        execfile(path, globals(), local)
    except:
        log.exception('error while loading %s' % path)
    else:
        for key, value in local.iteritems():
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


if SECRET == b'monkey':
    log.warning('You should set SECRET')
if DEVICE_NAME == 'unnamed':
    log.warning('You should set DEVICE_NAME')