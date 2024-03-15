"""
@author    Matthew Seaworth <mseaworth@futurex.com>
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex, L.P.

Copyright by:  Futurex, L.P. 2021

@section DESCRIPTION
Holds connection information for a socket
"""
import socket
from abc import ABC, abstractmethod


class SocketAddress(ABC):
    """Container class for socket address info"""

    @abstractmethod
    def __repr__(self):
        """String representation of the target address"""

    @abstractmethod
    def new_socket(self):
        """Create a new socket for the given address"""

    @abstractmethod
    def connect_socket(self, sock):
        """Connect to a given socket"""

    @staticmethod
    def unix(address: str = None):
        """Create a unix socket info
        Args:
            address:  The location of the unix socket
        Return: A unix socket info
        """
        return UnixAddress(address)

    @staticmethod
    def inet(ipaddress: str = None, port: str = None):
        """Create an inet socket info
        Args:
            ipaddress:  The IPv4 address target
            port:  The target port
        Return: An inet socket info
        """
        return InetAddress(ipaddress, int(port))


class UnixAddress(SocketAddress):
    """A unix socket address"""
    def __init__(self, address: str):
        self.address = address

    def __repr__(self):
        return self.address

    def new_socket(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        return sock

    def connect_socket(self, sock):
        return sock.connect(self.address)


class InetAddress(SocketAddress):
    """An ip address/hostname and a port"""
    def __init__(self, address: str, port: int):
        self.address = address
        self.port = port

    def __repr__(self):
        return f'{self.address}:{self.port}'

    def new_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return sock

    def connect_socket(self, sock):
        return sock.connect((self.address, self.port))
