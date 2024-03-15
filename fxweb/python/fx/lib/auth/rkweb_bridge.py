from functools import wraps

from flask_login import current_user
from flask_login import login_required as flask_login_check

from user import User
from application_log import ApplicationLogger

from rkweb.session import AuthSession

class RkWebBridge(object):

    login_cb = None
    logout_cb = None

    @classmethod
    def set_login(cls, login):
        """
        Sets the callbacks that can be called from this module
        to login the fxweb session.
        :param login: Login callback that accepts JWT as only parameter
        """
        cls.login_cb = login

    @classmethod
    def set_logout(cls, logout):
        """
        Sets the callbacks that can be called from this module
        to logout the fxweb session.
        :param logout: Logout callback that accepts no parameters
        """
        cls.logout_cb = logout

    @classmethod
    def login(cls, token):
        try:
            cls.login_cb(token)
        except Exception as e:
            ApplicationLogger.error("Error syncing login state: " + str(e))
            pass

    @classmethod
    def logout(cls):
        try:
            cls.logout_cb()
        except Exception as e:
            # Not logged in
            if str(e) == "Attempted to access unknown connection.":
                pass
            ApplicationLogger.error("Error syncing logout state: " + str(e))
            pass

def rkweb_auth_needs_sync(rkweb_auth):
    fxweb_auth = current_user

    rkweb_is_auth = rkweb_auth and rkweb_auth.token != None and rkweb_auth.token != ""
    fxweb_is_auth = current_user != None and current_user.context != None and current_user.context.user_group_id != None

    # Nobody is logged in
    if not rkweb_is_auth and not fxweb_is_auth:
        return False

    # fxweb is anonymous and rkweb is not authed - let it be
    if not rkweb_is_auth and fxweb_auth.is_anonymous:
        return False

    # Mismatch authorization state needs sync
    if rkweb_is_auth != fxweb_is_auth:
        return True

    # Does the fxweb group match the rkweb group?
    match_groupid = False
    fxweb_groupid = fxweb_auth.context.user_group_id
    for role in rkweb_auth.roles:
        if str(role['id']) == str(fxweb_groupid):
            match_groupid = True
            break

    # BYOK need to check against group names
    if not match_groupid and isinstance(fxweb_groupid, list):
        match_groupid = True
        for role in rkweb_auth.roles:
            match_role = False
            for fxrole in fxweb_groupid:
                if role['name'] == fxrole:
                    match_role = True
                    break
            if not match_role:
                match_groupid = False
                break;

    # Need sync if they don't agree on usergroupid
    return not match_groupid

def rkweb_auth_can_sync(rkweb_auth):
    return rkweb_auth and rkweb_auth.has_principal

def rkweb_sync(rkweb_auth):
    try:
        # If the login states don't agree
        if rkweb_auth_needs_sync(rkweb_auth):
            # Make fxweb match rkweb
            if rkweb_auth_can_sync(rkweb_auth):
                RkWebBridge.login(rkweb_auth.token)
                fxweb_auth = User.get(current_user.get_id())
                if fxweb_auth:
                    fxweb_auth.context.csrf_token = rkweb_auth.csrf_token
            # Reset fxweb
            else:
                RkWebBridge.logout()
    except Exception as e:
        ApplicationLogger.error("Error syncing auth state: " + str(e))
        pass

    return None

def login_required(func):
    """
    Wrapper for the flask login manger login_required decorator.
    Before a login check occurs, we will grab the rkweb login
    session and make sure it agrees with the fxweb login session.
    If it does not, we will login the client port connection
    with the JWT from the rkweb session to update the fxweb session.
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        # Sync fxweb and rkweb login states
        rkweb_auth = AuthSession.get()
        rkweb_sync(rkweb_auth)

        # Forward to flask login manager check
        return flask_login_check(func)(*args, **kwargs)
    return decorated_view

def rkweb_session():
    return AuthSession.get()

