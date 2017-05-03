import unittest

from mathcp.math import calculate

class MathTestCase(unittest.TestCase):
    def test_integer(self):
        self.assertEqual(calculate('1'), 1)
        self.assertEqual(calculate('1 * 1'), 1)
        self.assertEqual(calculate('1 / 1'), 1)
        self.assertEqual(calculate('2 / 2'), 1)

        self.assertEqual(calculate('1 + 1'), 2)
        self.assertEqual(calculate('1 * 2'), 2)
        self.assertEqual(calculate('4 / 2'), 2)

    def test_float(self):
        self.assertAlmostEqual(calculate('2.2 + 2.2'), 4.4)
        self.assertAlmostEqual(calculate('2.2 - 2.2'), 0)
        self.assertAlmostEqual(calculate('2.2 * 2.2'), 4.84)
        self.assertAlmostEqual(calculate('2.2 / 2.2'), 1)

    def test_unary(self):
        self.assertEqual(calculate('-1'), -1)
        self.assertEqual(calculate('-2.2'), -2.2)
        self.assertEqual(calculate('2 + (-1 + 3)'), 4)


    def test_parentheses(self):
        self.assertEqual(calculate('(1)'), 1)
        self.assertEqual(calculate('(1 + 1)'), 2)

    def test_operator_precedence(self):
        self.assertEqual(calculate('2 + 2 - 2 + 2'), 4)
        self.assertEqual(calculate('2 + 2 * 2 - 2'), 4)
        self.assertEqual(calculate('2 + 2 / 2 - 2'), 1)
        self.assertEqual(calculate('2 + 2 * 2 / 2 - 2'), 2)
        self.assertAlmostEqual(calculate('1 * 2 / 3'), 0.66666666)
        self.assertAlmostEqual(calculate('1 / 2 * 3'), 1.5)

    def test_abrites_example(self):
        self.assertEqual(calculate('((1 + 3) / 3.14) * 4 - 5.1'), -0.004458598726114538)

    def test_non_string_input(self):
        self.assertEqual(calculate(1), 1)
        self.assertEqual(calculate(1.9999), 1.9999)

        with self.assertRaises(SyntaxError):
            calculate(object)

    def test_invalid_operator(self):
        cases = ['1 ^ 3', '1 ++ 3', '1 -- 3', '1 ** 3', '1 // 3', '10 + 50%', '--1']

        for case in cases:
            with self.assertRaises(SyntaxError):
                calculate(case)

    def test_invalid_operand(self):
        with self.assertRaises(SyntaxError):
            calculate('2 * pi')
