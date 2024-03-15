"""
@file      regauth_login_response.py
@author    Matthew Seaworth (mseaworth@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2017

@section DESCRIPTION
Creates a response to a login request from the client
"""
from flask import redirect, url_for, make_response
from flask_login import current_user


class RALoginResponse(object):
    """Manages the response for a user login session"""
    def __init__(self):
        """Empty initializer"""

    def response(self, authenticated, download_token=None):
        """Return a result from the value of authenticated
        :return: a frontend_response corresponding to the authentication value
        """
        if download_token is None:
            download_token = current_user.download_token

        if authenticated and download_token:
            return self.download_response(download_token)
        elif authenticated:
            return self.authenticated_response()

        return self.unauthenticated_response()

    def download_response(self, download_token = None):
        """Redirect the user to the download landing
        :return: the download redirect
        """
        return redirect(self.ra_download(download_token))

    def authenticated_response(self):
        """Redirect the user to the application landing
        :return: the app landing redirect
        """
        current_user.reset_download_token()
        return redirect(self.ra_landing())

    def unauthenticated_response(self):
        """Create response for unauthenticated users
        :return: frontend_response containing the login uri
        """
        response = self.unprotected_login()
        current_user.reset_download_token()
        return response

    @staticmethod
    def ra_download(download_token = None):
        """RA download redirect"""
        if download_token is None:
            download_token = current_user.download_token
        return url_for('/regauth/download', uniqueID = download_token, _external=True, _scheme="https")

    @staticmethod
    def ra_landing():
        """RA landing redirect"""
        return "/regauth"

    @staticmethod
    def unprotected_login():
        """RA login redirect"""
        return redirect("/#?redirect=regauth")
