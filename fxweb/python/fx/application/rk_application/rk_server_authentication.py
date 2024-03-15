"""
@file      rk_server_authentication.py
@author    Aaron Perez (aperez@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2018

@section DESCRIPTION
Handles server authentication for RK applications
"""

import typing
if typing.TYPE_CHECKING:
    from lib.auth.user import User
    from rk_application.rk_login_status import LoginStatus


class RKAuthStatus(object):
    """
    Implements the various ways of updating the auth status
    (default, user roles, etc.)
    """
    def update_auth_status(self, user, login_status, update_cb=None):
        """
        Updates the user authentication status and updates session and login status parameters
        Arguments:
            user: Current user to update information on
            login_status: Metadata about login status
        Returns: An updated login_status
        """
        # Login status should contain details about a login response
        if login_status.login_details is not None:
            # User role login
            if login_status.login_details.has_user_role_details():
                login_status = self._update_user_role_auth_status(user, login_status, update_cb)
            # Request for PKI nonce challenge login
            elif login_status.login_details.has_pki_nonce_details():
                login_status = self._update_nonce_auth_status(user, login_status, update_cb)
            # Default login
            else:
                login_status = self._update_default_auth_status(user, login_status, update_cb)

        return login_status

    def _update_default_auth_status(self, user, login_status, update_cb):
        """
        Handles login statuses with the default details
        Arguments:
            user: Current user to update information on
            login_status: Metadata about login status
        Returns: An updated login_status
        """
        logged_in = login_status.login_details.users_logged_in
        total = login_status.login_details.users_total

        if logged_in < total:
            name = login_status.login_info['name']
            message = "{} out of {} users have logged in for '{}' group."
            login_status.login_message = message.format(logged_in, total, name)
        elif logged_in >= total:
            if update_cb is not None:
                update_cb(user, login_status)
            else:
                self._update(user, login_status)

        return login_status

    def _update_user_role_auth_status(self, user, login_status, update_cb):
        """
        Handles login statuses with the default details
        Arguments:
            user: Current user to update information on
            login_status: Metadata about login status
        Returns: An updated login_status
        """
        pending_groups = login_status.login_details.pending_groups
        has_pending = len(pending_groups) > 0

        authorized_groups = login_status.login_details.authorized_groups
        has_authorized = len(authorized_groups) > 0

        # Always login now, fxweb is no longer responsible for deciding 'login now' logic
        login_now = has_authorized

        if has_pending or has_authorized:
            message = "Pending Groups: {}; Authorized Groups: {}"
            login_status.login_message = message.format(
                ','.join(pending_groups),
                ','.join(authorized_groups)
            )
            # Automatically login now if there are no other options
            if not has_pending and has_authorized:
                login_now = True

        # Check if user wants to login now
        if has_authorized and login_now:
            if update_cb is not None:
                update_cb(user, login_status)
            else:
                self._update(user, login_status)

        return login_status

    def _update_nonce_auth_status(self, user: 'User', login_status: 'LoginStatus', update_cb):
        """
        Handles login statuses with a PKI nonce challenge
        Arguments:
            user: Current user to update information on
            login_status: Metadata about login status
        Returns: An updated login_status
        """

        user.pki_session_id = login_status.login_details.pki_session_id

        if update_cb is not None:
            update_cb(user, login_status)

        return login_status

    def _update(self, user, login_status):
        """
        Handle the actual updating of the login status and user upon success
        """
        login_status.login_message = "All users have logged in, please wait..."
        # Returns to the client that the user is fully logged in
        login_status.fully_logged_in = True
        # Authenticate the user once all required users are logged in.
        # Note: This controls the login_required decorator
        user.authenticated = True
        user.user_group_id = login_status.login_info['id']
