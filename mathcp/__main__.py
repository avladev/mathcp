import argparse
import logging

from mathcp.loop import Loop
from mathcp.math import calculate
from mathcp.parallel import Pool
from mathcp.server import Server, Client


logger = logging.getLogger(__name__)

class MathClient(Client):
    def __init__(self, client_socket, pool: Pool, **kwargs):
        super().__init__(client_socket, '\n', 'utf8')
        self.pool = pool

    def on_message(self, message):
        logger.info("Message: %s", message)

        if message == chr(0x03) or message == "exit":
            self.on_disconnect()
            return

        self.pool.add(calculate, (message,), self.on_calculation_success, self.on_calculation_error)

    def on_calculation_success(self, result):
        logger.info("Calculation success: %s", result)
        self.socket.print(str(result))

    def on_calculation_error(self, error):
        logger.info("Calculation error: %s", error)

        if isinstance(error, SyntaxError):
            self.socket.print("Error: Invalid expression!")
        else:
            self.socket.print("Error: %s" % error)

    def on_connected(self):
        super().on_connected()
        self.socket.print("=====================================")
        self.socket.print(" Welcome to math solver :D")
        self.socket.print(" Allowed operations are: +, -, *, /")
        self.socket.print("")
        self.socket.print(" Send 'exit' or Ctrl-C to quit")
        self.socket.print("=====================================")

    def on_disconnect(self):
        super().on_disconnect()
        logger.info("Connection closed")


if __name__ == "__main__":
    logging.basicConfig(
        format='[%(asctime)s] [%(levelname)s] [pid %(process)d] '
               '[%(name)s][%(funcName)s][%(lineno)d] %(message)s'
    )

    parser = argparse.ArgumentParser(description='Math TCP Server')
    parser.add_argument("host", type=str, nargs="?", help="Server ip address. Default: 0.0.0.0", default='0.0.0.0')
    parser.add_argument("port", type=int, nargs="?", help="Server port. Default: 8000", default="8000")
    parser.add_argument('-v', '--verbose', help="Verbose logger", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    pool = Pool()
    server = Server(args.host, args.port, MathClient, pool=pool)
    server.listen()

    Loop(server, pool).run()
