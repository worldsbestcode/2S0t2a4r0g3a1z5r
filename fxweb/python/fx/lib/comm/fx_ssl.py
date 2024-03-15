""" SSL.py
SSL and socket connection functions
"""
import ssl
from socket_address import SocketAddress


class SSLInfo:
    """Container for TLS connection parameters"""
    def __init__(self):
        self.use_ssl = False
        self.private_key_file = None
        self.certificate_file = None
        self.ssl_version = None
        self.cipher = None

    @property
    def real_ssl(self) -> bool:
        return all((
            self.private_key_file is not None,
            self.certificate_file is not None,
            self.cipher is not None,
        ))

    def wrap_socket(self, sock):
        """Wrap a socket object for ssl use"""
        if not self.use_ssl:
            return sock

        return ssl.wrap_socket(sock,
                ssl_version=self.ssl_version,
                certfile=self.certificate_file,
                keyfile=self.private_key_file,
                ciphers=self.cipher)

    def __repr__(self):
        """Human readable representation of the SSLInfo"""
        real = self.real_ssl
        parts = (
            'SSL' if real else 'Anonymous SSL',
            self.ssl_version.name if self.ssl_version else None,
            f'cert={self.certificate_file}' if real else None,
            f'key={self.private_key_file}' if real else None,
            f'with cipher {self.cipher}' if real else None,
        )

        return ' '.join(part for part in parts if part)


class SSLWrappedAddress(SocketAddress):
    """Wrapper for addresses using SSL connections"""
    def __init__(self, wrapped_address, ssl_info):
        self.wrapped = wrapped_address
        self.info = ssl_info

    def __repr__(self):
        if self.info.use_ssl:
            return f'{self.wrapped} over {self.info}'

        return f'{self.wrapped} in the clear'

    def new_socket(self):
        return self.info.wrap_socket(self.wrapped.new_socket())

    def connect_socket(self, sock):
        return self.wrapped.connect_socket(sock)
