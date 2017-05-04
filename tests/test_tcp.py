import socket
import time
from threading import Thread
from unittest import TestCase

from functools import partial

from mathcp.__main__ import run_server


def create_server() -> Thread:
    return Thread(target=run_server, args=('', 8888), daemon=True)


error_msg = 'Error: Invalid expression!'


def create_connection():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('', 8888))
    # Read the welcome message, we don't need it
    sock.recv(1024)
    return sock


def get_result(sock, message):
    sock.send(("%s\r\n" % message).encode())
    data = sock.recv(1024)
    return data.decode().strip()


class ServerTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        thread = create_server()
        thread.start()
        time.sleep(1)

    def setUp(self):
        self.connection = create_connection()
        self.calculate = partial(get_result, self.connection)

    def tearDown(self):
        self.connection.close()

    def test_integer(self):
        self.assertEqual(self.calculate('1'), '1')
        self.assertEqual(self.calculate('1 * 1'), '1')
        self.assertEqual(self.calculate('1 / 1'), '1.0')
        self.assertEqual(self.calculate('2 / 2'), '1.0')

        self.assertEqual(self.calculate('1 + 1'), '2')
        self.assertEqual(self.calculate('1 * 2'), '2')
        self.assertEqual(self.calculate('4 / 2'), '2.0')

    def test_float(self):
        self.assertAlmostEqual(float(self.calculate('2.2 + 2.2')), 4.4)
        self.assertAlmostEqual(float(self.calculate('2.2 - 2.2')), 0)
        self.assertAlmostEqual(float(self.calculate('2.2 * 2.2')), 4.84)
        self.assertAlmostEqual(float(self.calculate('2.2 / 2.2')), 1)

    def test_unary(self):
        self.assertEqual(self.calculate('-1'), '-1')
        self.assertEqual(self.calculate('-2.2'), '-2.2')
        self.assertEqual(self.calculate('2 + (-1 + 3)'), '4')

    def test_parentheses(self):
        self.assertEqual(self.calculate('(1)'), '1')
        self.assertEqual(self.calculate('(1 + 1)'), '2')

    def test_operator_precedence(self):
        self.assertEqual(self.calculate('2 + 2 - 2 + 2'), '4')
        self.assertEqual(self.calculate('2 + 2 * 2 - 2'), '4')
        self.assertEqual(self.calculate('2 + 2 / 2 - 2'), '1.0')
        self.assertEqual(self.calculate('2 + 2 * 2 / 2 - 2'), '2.0')
        self.assertAlmostEqual(float(self.calculate('1 * 2 / 3')), 0.66666666)
        self.assertAlmostEqual(float(self.calculate('1 / 2 * 3')), 1.5)

    def test_abrites_example(self):
        self.assertEqual(self.calculate('((1 + 3) / 3.14) * 4 - 5.1'), '-0.004458598726114538')

    def test_invalid_operator(self):
        cases = ['1 ^ 3', '1 ++ 3', '1 -- 3', '1 ** 3', '1 // 3', '10 + 50%', '--1']

        for case in cases:
            self.assertEqual(self.calculate(case), error_msg)

    def test_invalid_operand(self):
        self.assertEqual(self.calculate('2 * pi'), error_msg)

    def test_invalid_encoding(self):
        self.connection.send("куркума\r\n".encode('cp1251'))
        self.assertEqual(self.connection.recv(1024).decode().strip(), "Error while executing the expression!")

    def test_close_connection(self):
        # Ctrl-C
        connection = create_connection()
        connection.send(("%s\r\n" % chr(0x03)).encode())
        self.assertEqual(connection.recv(1024), b'')
        connection.close()

        # exit
        connection = create_connection()
        connection.send("exit\r\n".encode())
        self.assertEqual(connection.recv(1024), b'')
        connection.close()

    def test_two_connections(self):
        connection1 = create_connection()
        connection2 = create_connection()

        self.assertEqual(get_result(connection1, '1'), '1')
        self.assertEqual(get_result(connection2, '2'), '2')

        connection1.close()
        connection2.close()
