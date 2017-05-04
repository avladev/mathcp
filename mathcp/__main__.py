import argparse
import logging

from mathcp.loop import Loop
from mathcp.math import calculate
from mathcp.parallel import Pool
from mathcp.server import Server, Connection

logger = logging.getLogger(__name__)


class MathSolver(Connection):
    """
    This is a Connection implementation which separates socket data by '\n'
    and executes each message in a pool of processes to obtain the result of
    the math operations.
    """

    def __init__(self, raw_socket, pool: Pool, **kwargs):
        super().__init__(raw_socket, '\n', 'utf8')
        self._pool = pool

    def on_message(self, message):
        logger.info("Message: %s", message)

        if message == "":
            self.send("Please enter an expression!")
            return

        if message == chr(0x03) or message == "exit":
            # Disconnect when "exit" or Ctrl-C is received
            self.on_disconnect()
            return

        self._pool.add(calculate, (message,), self.on_calculation_success, self.on_calculation_error)

    def on_message_error(self, error: Exception) -> None:
        logger.info("Error: %s", error)
        self.send("Error while executing the expression!")

    def on_calculation_success(self, result):
        logger.info("Calculation success: %s", result)
        self.send(str(result))

    def on_calculation_error(self, error):
        logger.info("Calculation error: %s", error)

        if isinstance(error, SyntaxError):
            self.send("Error: Invalid expression!")
        else:
            self.send("Error: %s" % error)

    def on_connected(self):
        super().on_connected()
        self.send("=====================================")
        self.send(" Welcome to math solver")
        self.send(" Allowed operations are: +, -, *, /")
        self.send("")
        self.send(" Send 'exit' or Ctrl-C to quit")
        self.send("=====================================")

    def on_disconnect(self):
        super().on_disconnect()
        logger.info("Connection closed")


def run_server(host: str, port: int):
    pool = Pool()
    server = Server(host, port, MathSolver, pool=pool)
    server.listen()

    Loop(server, pool).run()


def main():
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

    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
