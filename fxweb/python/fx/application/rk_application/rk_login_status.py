"""
@file      rk_login_status.py
@author    Aaron Perez (aperez@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2018

@section DESCRIPTION
Provide the status of the current login session and the details specific to what
type of login is being performed i.e. default, user roles, etc. for RK
"""

# Default minimum required users to login
DEFAULT_LOGIN_REQUIRED = 2


class LoginDetails:
    """
    Default login details
    """
    def __init__(self, users_total=DEFAULT_LOGIN_REQUIRED,
                 users_logged_in=0,
                 auth_token=None, **kwargs):
        self.users_total = users_total
        self.users_logged_in = users_logged_in
        self.auth_token = auth_token

    @classmethod
    def has_user_role_details(cls):
        return False

    @classmethod
    def has_pki_nonce_details(cls):
        return False


class UserRoleLoginDetails(LoginDetails):
    """
    Login details when user roles are enabled
    """
    def __init__(self, pending_groups=Ellipsis, authorized_groups=Ellipsis,
                 login_now=False, **kwargs):
        super().__init__(**kwargs)
        self.pending_groups = pending_groups if pending_groups is not Ellipsis else []
        self.authorized_groups = authorized_groups if authorized_groups is not Ellipsis else []
        self.login_now = login_now

    @classmethod
    def has_user_role_details(cls):
        return True


class PkiNonceLoginDetails(LoginDetails):
    """
    Login details when requesting a PKI nonce
    """
    def __init__(self, pki_provider, pki_challenge_nonce, pki_session_id, pki_subject, **kwargs):
        super().__init__(**kwargs)
        self.pki_provider = pki_provider
        self.pki_challenge_nonce = pki_challenge_nonce
        self.pki_session_id = pki_session_id
        self.pki_subject = pki_subject

    @classmethod
    def has_pki_nonce_details(cls):
        return True


class LoginStatus(object):
    """
    Stores the login status of the current login session
    """
    def __init__(self, success=False, fully_logged_in=False, password_change=False,
                 login_message='Invalid password.', login_info=Ellipsis,
                 login_details=None):
        self.success = success
        self.fully_logged_in = fully_logged_in
        self.password_change = password_change
        self.login_message = login_message
        self.login_info = login_info if login_info is not Ellipsis else {}
        self.login_details = login_details
