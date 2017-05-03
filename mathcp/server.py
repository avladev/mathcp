import logging
import socket

from mathcp.loop import Tickable

logger = logging.getLogger(__name__)


class SocketCallback(object):
    def __init__(self, on_message: callable, on_disconnect: callable):
        self._on_message = on_message
        self._on_disconnect = on_disconnect

    def on_message(self, message: str):
        self._on_message(message)

    def on_disconnect(self):
        self._on_disconnect()

    def __del__(self):
        logger.debug("Destruct %s", type(self))


class Socket(Tickable):
    def __init__(self, raw_socket, callback: SocketCallback, separator='\r\n', encoding='utf8'):
        super().__init__()
        self.socket = raw_socket
        self.callback = callback
        self.separator = separator.encode(encoding)
        self.encoding = encoding

        self.read_buffer = bytearray()
        self.write_buffer = bytes()

    def print(self, message: str, end='\r\n'):
        self.write_buffer += ("%s%s" % (message, end)).encode(self.encoding)

    def tick(self):
        if self.write_buffer:
            try:
                bytes_send = self.socket.send(self.write_buffer)
                self.write_buffer = self.write_buffer[bytes_send:]
            except BlockingIOError:
                # Cannot write at the moment
                pass

        try:
            data = self.socket.recv(1024)

            if data == b'':
                self.callback.on_disconnect()
                return

            self.read_buffer.extend(data)
        except BlockingIOError:
            # Cannot read at the moment
            pass

        *messages, self.read_buffer = self.read_buffer.split(self.separator)

        for message in messages:
            self.callback.on_message(message.decode(self.encoding).strip())

    def destroy(self):
        super().destroy()
        self.socket.close()
        del self.socket
        del self.callback

    def __del__(self):
        logger.debug("Destruct %s", type(self))


class Client(Tickable):
    def __init__(self, client_socket, separator: str, encoding: str):
        super().__init__()

        self.socket = Socket(
            client_socket,
            SocketCallback(self.on_message, self.on_disconnect),
            separator,
            encoding
        )

    def on_connected(self):
        self.loop.add(self.socket)

    def on_message(self, message):
        raise NotImplemented("Implement this in your client implementation")

    def on_disconnect(self):
        self.destroy()

    def destroy(self):
        super().destroy()
        self.socket.destroy()
        del self.socket

    def __del__(self):
        logger.debug("Destruct %s", type(self))


class Server(Tickable):
    def __init__(self, host: str, port: int, client_class: Client, **kwargs):
        super().__init__()
        self.host = host
        self.port = port

        if not issubclass(client_class, Client):
            raise TypeError("Your client class should subclass Client class")

        self.client_class = client_class
        self.socket = None
        self.dependencies = kwargs

    def listen(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setblocking(0)
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        logger.info("Listening on %s:%s", self.host, self.port)

    def tick(self):
        try:
            client_socket, _ = self.socket.accept()
            client_socket.setblocking(0)
            logger.info("New connection from %s:%s", _[0], _[1])

            if callable(self.client_class):
                client = self.client_class(client_socket, **self.dependencies)
                self.loop.add(client)
                client.on_connected()

        except BlockingIOError:
            # No new connections
            pass
