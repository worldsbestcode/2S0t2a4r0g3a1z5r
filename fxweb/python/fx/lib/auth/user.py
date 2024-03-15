"""
@file      user.py
@author    James Espinoza(jespinoza@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Acts as a store for all logged in user sessions
"""
import json

from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import BadSignature, BadData, SignatureExpired
from gevent.lock import BoundedSemaphore

from asynccomm import synchronized


class User(UserMixin):
    '''
    Flask Login User class. This class stores user sessions
    and ensures that the user identifier was not tampered with
    '''
    user_semaphore = BoundedSemaphore(1)
    users = {}
    load_user = None

    def __init__(self):
        self.id = None
        self.user_group_id = None
        self.context = None
        self.authenticated = False
        self.authenticated_remote_groups = set()
        self.authenticated_remote_devices = set()
        self.card_logins_in_progress = dict()
        self.download_token = None
        self.temporary_file = None
        self.pki_session_id = None

    def set_info(self, context):
        """
        Sets the encrypted token as the user id and context associated with the user
        :param context: context object associated with the user
        """
        self.id = str(context.encrypted_token)
        self.context = context

    def reset_download_token(self):
        """
        Resets the download token assigned for this user
        """
        if self.download_token:
            self.download_token = None
        
    @property
    def is_authenticated(self):
        """
        Boolean used to tell if the user group is fully authenticated
        """
        return self.authenticated

    @property
    def is_anonymous(self):
        """
        Boolean used to tell if the user is logged in as the anonymous role
        """
        return self.context and self.context.is_anonymous()

    @property
    def requires_csrf(self):
        """Checks if this class needs CSRF protection
        Browser and anonymous users require CSRF protection
        """
        return True

    @property
    def csrf_check_origin(self):
        """
        Checks if this class should require a matching origin/referer for CSRF protection
        """
        return True

    def get_card_login_in_progress(self, session_ids):
        """
        Checks to see if a card login session by this pair of IDs is in progress.
        """
        try:
            return self.card_logins_in_progress[session_ids]
        except KeyError:
            return False

    def add_card_login_in_progress(self, session_ids, user_logged_in):
        """
        Adds a new card login session to this user.
        """
        self.card_logins_in_progress[session_ids] = []
        self.card_logins_in_progress[session_ids].append(user_logged_in)

    def remove_card_login_in_progress(self, session_ids):
        """
        Removes a card login session from this user.
        """
        try:
            del self.card_logins_in_progress[session_ids]
        except KeyError:
            pass

    @property
    def is_authenticated_to_remote_device(self, id):
        """
        Checks if a user is authenticated to a particular remote device.
        """
        try:
            return id in self.authenticated_remote_devices
        except KeyError:
            return False
    
    @property
    def is_authenticated_to_remote_device_group(self, id):
        """
        Checks if a user is authenticated to a particular remote device group,
        which also means to all of its devices.
        """
        try:
            return id in self.authenticated_remote_groups
        except KeyError:
            return False

    @classmethod
    @synchronized(user_semaphore)
    def get(cls, id):
        """
        Returns the user associated with the passed in id
        :param id: ID of user
        """
        return User.users.get(id, None)

    @classmethod
    @synchronized(user_semaphore)
    def add(cls, user):
        """
        Adds the user associated with the passed in id
        :param id: ID of user
        """
        User.users.update({user.id: user})

    @classmethod
    @synchronized(user_semaphore)
    def remove(cls, id, logout_user_cb=None):
        """
        Removes the user associated with the passed in id
        :param id: ID of user
        :param logout_user_cb: Callback for the user logout event
        """
        User.users.pop(id, None)

        if logout_user_cb:
            logout_user_cb()

    def get_authed_ids_cookie(self):
        """
        Concatenates the two sets of logged in endpoints for storing in a cookie.
        """
        return json.dumps({
            'devices': list(self.authenticated_remote_devices),
            'groups': list(self.authenticated_remote_groups)
        })

    @classmethod
    def init_login(cls, login_manager, app, unauth_exception):
        """
        Inits the login manager configuration for the application
        :param login_manager: Login maanger to init
        :param app: Application object that represents this application settings
        :param unauth_exception: Exception to throw if unauthorized
        """
        login_manager.anonymous_user = AnonymousUser
        login_manager.session_protection = 'strong'

        @login_manager.unauthorized_handler
        def unauthorized():
            """
            If the current user hasn't logged in or their session timed out, redirect to login page
            """
            # DEBUG: Uncomment this to see where login failures happen
            #raise RuntimeError("Login Failure")
            raise unauth_exception

        @login_manager.user_loader
        def load_user(user_id):
            """
            Load user call back. Used to load the current user based on the session cookie if it exists
            Note: This method decrypts the identifier and ensures it's not tampered with. This is not necessarily
                  required, since Flask MACs the entire cookie, but can be used in case we ever want to use tokenized
                  authentication(JWT for example)
            :param user_id: The session cookie identifier
            :return: Returns user object if found, None if not found. None will result in an AnonymousUser object being returned
                     by Flask-Login
            """
            user = User.get(user_id)

            if user:
                serializer = user.context.serializer
                try:
                    decrypted_token = serializer.loads(user_id)

                    if user.context.token != decrypted_token:
                        user = None

                except (BadSignature, BadData, SignatureExpired):
                    # The user loader is supposed to return None on invalid and not raise an exception
                    return None

            return user

        cls.load_user = load_user


class AnonymousUser(AnonymousUserMixin, User):
    def __init__(self):
        super(AnonymousUser, self).__init__()


class ApiUser(User):
    """A class for users limited to API methods"""
    @property
    def requires_csrf(self):
        """Checks if this class needs CSRF protection
        ApiUsers are not client browsers so they don't require CSRF protection
        """
        return False


class SecurusUser(User):
    """A class for users browsing from an Excrypt Touch"""
    @property
    def csrf_check_origin(self):
        """Ignore referer or origin if user agent is the Securus client"""
        return False
