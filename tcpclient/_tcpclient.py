"""TCP client.

This module contains a class implementing a TCP network client.
Rewritten to remove the expyriment dependency.

"""

import socket
import errno
from time import perf_counter


class TcpClient:
    """A class implementing a TCP network client."""

    def __init__(self, host, port, default_package_size=1024, connect=True):
        """Create a TcpClient.

        Parameters:
        -----------
        host : str
            The hostname or IPv4 address of the server to connect to.
        port : int
            The port to connect to.
        default_package_size : int, optional
            The default size of the packages to be received (default=1024).
        connect : bool, optional
            If True, connect immediately (default=True).

        """

        self._host = host
        self._port = port
        self._default_package_size = default_package_size
        self._socket = None
        self._is_connected = False
        if connect:
            self.connect()

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        if self._is_connected:
            raise AttributeError("Cannot set host if connected!")
        self._host = value

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        if self._is_connected:
            raise AttributeError("Cannot set port if connected!")
        self._port = value

    @property
    def default_package_size(self):
        return self._default_package_size

    @default_package_size.setter
    def default_package_size(self, value):
        if self._is_connected:
            raise AttributeError("Cannot set default_package_size if connected!")
        self._default_package_size = value

    @property
    def is_connected(self):
        return self._is_connected

    def connect(self):
        """Connect to the server."""

        if not self._is_connected:
            try:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.connect((self._host, self._port))
                self._is_connected = True
                self._socket.settimeout(0)
            except socket.error:
                raise RuntimeError(
                    "TCP connection to {0}:{1} failed!".format(self._host, self._port))

    def send(self, data):
        """Send data.

        Parameters:
        -----------
        data : bytes
            The data to be sent.

        """

        self._socket.sendall(data)

    def wait(self, length=None, package_size=None, duration=None,
             callback_function=None, process_control_events=True):
        """Wait for incoming data.

        Parameters
        ----------
        length : int, optional
            The length of the data to be waited for in bytes.
        package_size : int, optional
            The size of each chunk to receive.
        duration : int, optional
            The maximum time to wait in milliseconds.
        callback_function : ignored
        process_control_events : ignored

        Returns:
        --------
        data : bytes or None
        rt : int or None
            Time taken in milliseconds.

        """

        start = perf_counter()
        data = None
        rt = None

        if package_size is None:
            package_size = self._default_package_size
        if length is None:
            length = package_size
        elif length < package_size:
            package_size = length

        while True:
            try:
                if data is None:
                    data = self._socket.recv(package_size)
                while len(data) < length:
                    chunk_size = min(package_size, length - len(data))
                    data = data + self._socket.recv(chunk_size)
                    if duration and int((perf_counter() - start) * 1000) >= duration:
                        return None, None
                rt = int((perf_counter() - start) * 1000)
                break
            except socket.error as e:
                err = e.args[0]
                if err in (errno.EAGAIN, errno.EWOULDBLOCK):
                    if duration and int((perf_counter() - start) * 1000) >= duration:
                        return None, None
                else:
                    raise

        return data, rt

    def clear(self):
        """Read the socket buffer empty."""

        while True:
            try:
                if not self._socket.recv(1024):
                    break
            except:
                break

    def close(self):
        """Close the connection to the server."""

        if self._is_connected:
            self._socket.close()
            self._socket = None
            self._is_connected = False
