from django.test import SimpleTestCase
from . import calc


class TestCalculator(SimpleTestCase):
    def test_add_numbers(self):
        res = calc.add(4, 6)
        self.assertEquals(res, 10)

    def test_subtract(self):
        res = calc.subtract(2, 3)
        self.assertEquals(res, -1)
