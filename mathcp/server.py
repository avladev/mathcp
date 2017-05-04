import logging
import socket

from mathcp.loop import Tickable

logger = logging.getLogger(__name__)


class SocketCallback(object):
    """
    This is a helper class which holds Connections callbacks which
    have to be called when event in socket occurs.
    """

    def __init__(self, on_message: callable, on_error: callable, on_disconnect: callable):
        self._on_message = on_message
        self._on_error = on_error
        self._on_disconnect = on_disconnect

    def on_message(self, message: str) -> None:
        self._on_message(message)

    def on_error(self, error: Exception) -> None:
        self._on_error(error)

    def on_disconnect(self) -> None:
        self._on_disconnect()

    def __del__(self):
        logger.debug("Destruct %s", type(self))


class Socket(Tickable):
    """
    Socket is a wrapper to the raw socket, and handles reads, writes, decoding of messages.
    """

    def __init__(self, raw_socket, callback: SocketCallback, separator='\r\n', encoding='utf8'):
        super().__init__()
        self._socket = raw_socket
        self._callback = callback
        self._separator = separator.encode(encoding)
        self._encoding = encoding

        self._read_buffer = bytearray()
        self._write_buffer = bytes()

    def print(self, message: str, end="\r\n") -> None:
        """
        Writes a string to the socket
        """
        try:
            self._write_buffer += ("%s%s" % (message, end)).encode(self._encoding)
        except Exception as e:
            self._callback.on_error(e)

    def tick(self) -> None:
        if self._write_buffer:
            try:
                bytes_send = self._socket.send(self._write_buffer)
                self._write_buffer = self._write_buffer[bytes_send:]
            except BlockingIOError:
                # Cannot write at the moment
                pass

        try:
            data = self._socket.recv(1024)

            if data == b'':
                self._callback.on_disconnect()
                return

            self._read_buffer.extend(data)
        except BlockingIOError:
            # Cannot read at the moment
            pass

        *messages, self._read_buffer = self._read_buffer.split(self._separator)

        for message in messages:
            try:
                self._callback.on_message(message.decode(self._encoding).strip())
            except Exception as e:
                self._callback.on_error(e)

    def destroy(self) -> None:
        super().destroy()
        self._socket.close()
        del self._socket
        del self._callback

    def __del__(self) -> None:
        logger.debug("Destruct %s", type(self))


class Connection(Tickable):
    """
    Connection class is instantiated on every new connection to the server.
    You main goal is to subclass this class to be able to implement
    your app logic in on_message method for example.

    You should provide separator and encoding to be able to decode and split messages
    received on the socket.
    """

    def __init__(self, raw_socket, separator: str, encoding: str, **kwargs):
        super().__init__()

        self._socket = Socket(
            raw_socket,
            SocketCallback(self.on_message, self.on_message_error, self.on_disconnect),
            separator,
            encoding
        )

    def send(self, message:str, end="\r\n") -> None:
        """
        Send message to the client
        """
        return self._socket.print(message, end=end)

    def on_connected(self) -> None:
        """
        Called when connection object is ready to receive data from the socket
        """
        self.loop.add(self._socket)

    def on_message(self, message: str) -> None:
        """
        Called when new message is received on the socket
        """
        raise NotImplemented("Implement this method in your class")

    def on_message_error(self, error: Exception) -> None:
        """
        Called when an error occurs while reading, writing messages to the socket
        """
        pass

    def on_disconnect(self) -> None:
        """
        Called when connection to the user is lost.

        You can call this method from your child implementation when you
        want to close the connection
        :return:
        """
        self.destroy()

    def destroy(self) -> None:
        super().destroy()
        self._socket.destroy()
        del self._socket

    def __del__(self) -> None:
        logger.debug("Destruct %s", type(self))


class Server(Tickable):
    """
    This is a a socket server it's main goal is to accept new connections
    on the given host:port and create new instances of supplied connection_class.

    Kwargs are used as dependency injection to the connection class for example:

    Server('', 8000, Connection, service1=Service1())

    can be accessed in connection __init__ method

    def __init__(self, socket, ..., service1, **kwargs):
        service1.call()
    """

    def __init__(self, host: str, port: int, connection_class: Connection, **kwargs):
        super().__init__()
        self._host = host
        self._port = port

        if not issubclass(connection_class, Connection):
            raise TypeError("Your class should subclass Connection class")

        self._connection_class = connection_class
        self._socket = None
        self._dependencies = kwargs

    def listen(self) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.setblocking(0)
        self._socket.bind((self._host, self._port))
        self._socket.listen()
        logger.info("Listening on %s:%s", self._host, self._port)

    def tick(self) -> None:
        try:
            raw_socket, _ = self._socket.accept()
            raw_socket.setblocking(0)
            logger.info("New connection from %s:%s", _[0], _[1])

            if callable(self._connection_class):
                connection = self._connection_class(raw_socket, **self._dependencies)
                self.loop.add(connection)
                connection.on_connected()

        except BlockingIOError:
            # No new connections
            pass
