"""
@file      server_authentication.py
@author    Matthew Seaworth (mseaworth@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2017

@section DESCRIPTION
Performs functions needed to login to the remotekey server
"""
import fx
from application_log import ApplicationLogger
from lib.auth.credentials import (AnonymousCredentials, JwtCredentials,
                                  PkiNonceCredentials, PkiSignatureCredentials,
                                  UserPassCredentials)
from lib.utils.container_filters import coalesce_dict


class ServerLoginCredentials(object):
    """Handles credential parsing"""
    @staticmethod
    def parse(login_data):
        """Gets current credential object associated with login_data
        Arguments:
            login_data: The login information to turn into a credential
        Returns: Credential set
        """
        credential = {
            'pkiChallenge': ServerLoginCredentials.nonce_challenge,
            'pkiSignature': ServerLoginCredentials.nonce_signature,
            'userpass': ServerLoginCredentials.password,
            'anonymous': ServerLoginCredentials.anonymous,
            'jwt': ServerLoginCredentials.jwt,
        }

        auth_type = credential.get(coalesce_dict(login_data, ['auth_type', 'authType'], ''))
        auth_data = coalesce_dict(login_data, ['auth_credentials', 'authCredentials'], {})

        if auth_type is not None:
            return auth_type(auth_data)
        else:
            ApplicationLogger.debug('Error parsing login credentials.')

        return None

    @staticmethod
    def jwt(auth_data: dict):
        token = auth_data.get('token')
        return JwtCredentials(
            token=token,
        )

    @staticmethod
    def nonce_challenge(auth_data):
        certs = auth_data.get('certData', [])
        if isinstance(certs, (bytes, str)):
            certs = [certs]
        certs = [cert.hex() if isinstance(cert, bytes) else cert for cert in certs]
        cert = certs[0]
        cert_chain = certs[1:]
        return PkiNonceCredentials(
            cert=cert,
            cert_chain=cert_chain,
        )

    @staticmethod
    def nonce_signature(auth_data):
        signature = auth_data.get('signature')
        try:
            signature = signature.hex()
        except AttributeError:
            pass
        return PkiSignatureCredentials(
            signature=signature,
            session_id=auth_data.get('sessionId'),
        )

    @staticmethod
    def anonymous(_):
        """Create anonymous credentials
        Arguments:
            _: Unused
        Returns: A new anonymous credential
        """
        return AnonymousCredentials()

    @staticmethod
    def password(auth_data):
        """Get credentials for a user
        Arguments:
            login_data: The username and password from the request
        Returns: UserPassCredentials from login_data or None on error
        """
        try:
            user_name = auth_data['username']
            password = auth_data['password']
            old_password = auth_data['oldPassword'] if 'oldPassword' in auth_data else None
        except (KeyError, TypeError) as password_error:
            ApplicationLogger.debug(password_error)
            return None

        return UserPassCredentials(user_name, password, old_password=old_password)
