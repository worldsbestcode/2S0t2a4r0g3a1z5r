"""
@file      credentials.py
@author    James Espinoza(jespinoza@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Stores a set of credentials
"""
from binascii import hexlify

class Credentials(object):
    """
    Base class for credential set. This class abstracts authentication
    data for different types of authentication
    """
    Default   = 0
    UserPass  = 1
    Anonymous = 2
    PkiReq    = 3
    PkiSig    = 4
    Jwt       = 5

    def __init__(self, cred_type = Default):
        self._cred_type = cred_type

    @property
    def cred_type(self):
        """
        Returns the credential type
        """
        return self._cred_type
    
    @cred_type.setter
    def cred_type(self, value):
        """
        Sets the credential type
        """
        self._cred_type = value

class UserPassCredentials(Credentials):
    """
    Credential set that stores user name and password credentials
    """
    def __init__(self, username, password, old_password=None):
        super(UserPassCredentials, self).__init__(Credentials.UserPass)
        self.username = username
        self.password = password
        self.old_password = old_password

    @property
    def username(self):
        """
        Return user name
        """
        return self._username

    @username.setter
    def username(self, value):
        """
        Sets user name
        """
        self._username = value

    @property
    def password(self) -> str:
        """
        Return password
        """
        return self._password

    @property
    def hex_password(self) -> str:
        """
        Return password
        """
        return hexlify(self._password.encode()).decode()

    @password.setter
    def password(self, value: str):
        """
        Set password
        """
        if isinstance(value, bytes):
            value = value.decode()

        self._password = value

    @property
    def old_password(self):
        """
        Return old password
        """
        return self._old_password

    @old_password.setter
    def old_password(self, value):
        """
        Set old password
        """
        self._old_password = value

class AnonymousCredentials(Credentials):
    """
    Credential that represents an anonymous user
    """
    def __init__(self):
        super(AnonymousCredentials, self).__init__(Credentials.Anonymous)


class PkiNonceCredentials(Credentials):
    """
    Credential set for PKI nonce authentication (request a challenge nonce)
    """
    def __init__(self, cert=None, cert_chain=None):
        self.cert = cert
        self.cert_chain = cert_chain
        super().__init__(Credentials.PkiReq)


class PkiSignatureCredentials(Credentials):
    """
    Credential set for PKI nonce authentication (submit a signed nonce)
    """
    def __init__(self, session_id=None, signature=None):
        self.session_id = session_id
        self.signature = signature
        super().__init__(Credentials.PkiSig)


class JwtCredentials(Credentials):
    """
    Credential set for JWT authentication
    """
    def __init__(self, token=None):
        self.token = token
        super().__init__(cred_type=Credentials.Jwt)
