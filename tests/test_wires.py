from . import TestCase

from risa import wires
from risa import config


class TestWires(TestCase):

    def test_asserters(self):

        wires._set_pin(config.PIN_FAN1, True)
        self.assertFan(1)
        wires._set_pin(config.PIN_FAN2, True)
        self.assertRaises(ValueError, self.assertFan, 0)
        self.assertRaises(ValueError, self.assertFan, 1)

        wires._set_pin(config.PIN_HEAT, True)
        self.assertValve('heat')
        wires._set_pin(config.PIN_COOL, True)
        self.assertRaises(ValueError, self.assertValve, 'heat')

    def test_basic_heat(self):

        for pin in config.pins():
            wires._set_pin(pin, False)

        valve, fan = wires.set('heat', 3)

        # The function.
        self.assertValve('heat')
        self.assertFan(3)

        # The API.
        self.assertEqual(valve, 'heat')
        self.assertEqual(fan, 3)

    def test_basic_cool(self):

        for pin in config.pins():
            wires._set_pin(pin, False)

        valve, fan = wires.set('cool', 2)

        # The function.
        self.assertValve('cool')
        self.assertFan(2)

        # The API.
        self.assertEqual(valve, 'cool')
        self.assertEqual(fan, 2)

    def test_basic_off(self):

        for pin in config.pins():
            wires._set_pin(pin, True)

        valve, fan = wires.set('closed', 0)

        self.assertValve('closed')
        self.assertFan(0)

        self.assertEqual(valve, 'closed')
        self.assertEqual(fan, 0)

    def test_unsafe_set(self):
        
        self.assertRaises(ValueError, wires.set, 'heat', 0)
        self.assertRaises(ValueError, wires.set, 'cool', 0)
        wires.set('closed', 0)
        wires.set('closed', 1)
        wires.set('closed', 2)
        wires.set('closed', 3)

        wires.set('heat', 0, safe=False)
        self.assertValve('heat')
        self.assertFan(0)
        self.assertFalse(self.isSafe())

    def test_safe_open(self):

        for valve in 'heat', 'cool':

            wires.set('closed', 0)
            valve, fan = wires.set(valve)

            self.assertValve(valve)
            self.assertFan(1)
            self.assertSafe() # Redundant?

            self.assertEqual(valve, valve)
            self.assertEqual(fan, 1)

    def test_safe_stop(self):

        for valve in 'heat', 'cool':

            wires.set(valve, 3)
            valve, fan = wires.set(fan=0)

            self.assertValve('closed')
            self.assertFan(0)
            self.assertSafe() # Redundant?

            self.assertEqual(valve, 'closed')
            self.assertEqual(fan, 0)
