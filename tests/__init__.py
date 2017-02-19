from unittest import TestCase as BaseTestCase

from risa import config
from risa import wires


config.MOCK_PINS = True


class TestCase(BaseTestCase):

    def __init__(self, *args):
        super(TestCase, self).__init__(*args)
        self._config_bak = {}

    def tearDown(self):
        super(TestCase, self).tearDown()
        for k, v in self._config_bak.iteritems():
            setattr(config, k, v)
        self._config_bak.clear()

    def setConfig(self, **kwargs):
        for k, v in kwargs.iteritems():
            self._config_bak[k] = getattr(config, k)
            setattr(config, k, v)

    def getValve(self):
        heat = wires._get_pin(config.PIN_HEAT)
        cool = wires._get_pin(config.PIN_COOL)
        if heat and cool:
            raise ValueError('PIN_HEAT and PIN_COOL set')
        if heat:
            return 'heat'
        elif cool:
            return 'cool'
        else:
            return 'closed'

    def assertValve(self, valve):
        self.assertEqual(self.getValve(), valve)

    def getFan(self):

        pins = [None, config.PIN_FAN1, config.PIN_FAN2, config.PIN_FAN3]

        num = 0
        fan = 0
        for i, pin in enumerate(pins):
            if pin:
                is_set = wires._get_pin(pin)
                num += int(is_set)
                if is_set:
                    fan = i
        if num > 1:
            raise ValueError('Too many fan pins set.')

        return fan

    def assertFan(self, fan):
        if not isinstance(fan, int) or not (0 <= fan <= 3):
            raise ValueError('Bad fan: %r' % fan)
        self.assertEqual(self.getFan(), fan)

    def isSafe(self):
        valve = self.getValve()
        fan = self.getFan()
        return valve == 'closed' or fan

    def assertSafe(self):
        valve = self.getValve()
        fan = self.getFan()
        if valve != 'closed' and not fan:
            self.fail('Valve is %r with no fan.' % valve)




