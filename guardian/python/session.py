from flask import session

import datetime
import pytz

from flaskutils import abort

class UserSession():
    def __init__(self):
        self.users = []
        self.perms = []
        self.roles = []
        self.managed_roles = []
        self.token = None
        self.auth = {}
        self.provider = None
        self.token_expiration = datetime.datetime.utcnow()
        self.last_access = datetime.datetime.utcnow()
        self.hardened = False
        self.management = False
        self.user_management = False
        self.fully_logged_in = False

    @staticmethod
    def check_login() -> None:
        """
        Checks that the session is logged in to some capacity.
        If they are not logged in then an HTTP error is returned.

        Returns
            None if logged in, HTTP error otherwise
        """
        sess = UserSession.get()
        if len(sess.perms) == 0 or len(sess.users) == 0:
            abort(401, "Not logged in")

    @staticmethod
    def check_perm(perm: str):
        """
        Checks that the session has a specific permission.
        If the permission is missing than an HTTP error is returned.

        Args
            perm: Permission to check
        Returns
            None if authorized, HTTP error otherwise
        """
        sess = UserSession.get()
        if len(sess.perms) > 0 and len(sess.users) > 0 and perm in sess.perms:
            return None
        return abort(403, "Missing permission {}".format(perm))

    def get_users(self):
        return self.users

    def get_perms(self):
        return self.perms

    def get_token(self):
        return self.token

    @staticmethod
    def auth_token():
        try:
            if 'guardian' in session and 'token' in session['guardian']:
                return session['guardian']['token']
        except:
            pass
        return ""

    @staticmethod
    def logout():
        try:
            session.pop('guardian')
        except:
            pass

    def add_authenticated_identity(self, identity):
        """
        Adds an identity that is (at least partially) logged in to the session context:

        Args:
            identity: The identity information
        """
        user_info = {
            'id': identity['id'],
            #'uuid': identity.uuid,
            'name': identity['name'],
        }
        self.users.append(user_info)

    def add_authorized_role(self, role):
        """
        Adds a role's information to the current authorization context

        Args:
            role: The role to combine into the authorization context
        """
        # Don't add a role entry for the Anonymous role
        if role['id'] > 0:
            role_info = {
                'id': role['id'],
                'uuid': role['uuid'],
                'name': role['name'],
            }
            self.roles.append(role_info)
        self.hardened = role['hardened'] if role['hardened'] else self.hardened
        self.management = role['management'] if role['management'] else self.management
        # Combine perms
        for perm in role['perms']:
            if perm not in self.perms:
                self.perms.append(perm)

    def add_managed_roles(self, managed_roles):
        if 'Controllable' in managed_roles:
            for managed_role in managed_roles['Controllable']:
                id = managed_role[0]
                uuid = managed_role[1]
                found = False
                for cur_managed in self.managed_roles:
                    if cur_managed['id'] == id:
                        found = True
                        cur_managed['type'] = 'Controllable'
                        break
                if not found:
                    managed_info = {
                        'id': id,
                        'uuid': uuid,
                        'type': 'Controllable'
                    }
                    self.managed_roles.append(managed_info)

        if 'Assignable' in managed_roles:
            for managed_role in managed_roles['Assignable']:
                id = managed_role[0]
                uuid = managed_role[1]
                found = False
                for cur_managed in self.managed_roles:
                    if cur_managed['id'] == id:
                        found = True
                        if cur_managed['type'] != 'Controllable':
                            cur_managed['type'] = 'Assignable'
                        break
                if not found:
                    managed_info = {
                        'id': id,
                        'uuid': uuid,
                        'type': 'Assignable'
                    }
                    self.managed_roles.append(managed_info)

        if 'Viewable' in managed_roles:
            for managed_role in managed_roles['Viewable']:
                id = managed_role[0]
                uuid = managed_role[1]
                found = False
                for cur_managed in self.managed_roles:
                    if cur_managed['id'] == id:
                        found = True
                        break
                if not found:
                    managed_info = {
                        'id': id,
                        'uuid': uuid,
                        'type': 'Viewable'
                    }
                    self.managed_roles.append(managed_info)

    @staticmethod
    def is_valid_role(role, auth):
        # TODO: I think we should change the auth service to remove these for us
        """
        Checks if a role is valid to be authorized given the current user logins

        Args:
            role: The role to check
            auth: The authentication context
        Returns:
            True if valid, False if this role will can't be logged in
        """
        ret = True

        # All identities share role
        for user in auth['identities']:
            if role['id'] not in user['roleIds']:
                ret = False

        # Hardened
        #if role['hardened']:
        #    for user in auth['identities']:
        #        if not user['hardened']:
        #            ret = False

        return ret

    @staticmethod
    def is_authorized_role(role, auth):
        """
        Checks if a role's login requirements have been met

        Args:
            role: The role to check
            auth: The authentication context
        Returns:
            True if authorized, False if not fully logged in yet
        """
        ret = UserSession.is_valid_role(role, auth)

        # Minimum logins required
        if role['loginsRequired'] > len(auth['identities']):
            ret = False

        # Dual factor required
        if role['dualFactorRequired'] in ['Always', 'Available']:
            always = role['dualFactorRequired'] == 'Always'
            for user in auth['identities']:
                has = False
                for mech in user['mechanisms']:
                    has = mech in [
                        'TLS-2F',
                        'U2F',
                        'Signature-2F',
                        'OTP',
                        'OTP-SMS',
                        'OTP-SMTP',
                        'OTP-TOTP',
                        'JWT-2F']
                if not has and always:
                    ret = False
                elif not has and user['hasDualFactor']:
                    ret = False

        return ret

    @staticmethod
    def is_fully_logged_in(auth):
        """
        Checks if the authorization state is as logged in as possible,
        or if more authentication can be performed.

        Args:
            auth: The authentication context
        Returns:
            True if fully authorized, False if more authentication can be provided
        """
        ret = True
        for role in auth['roles']:
            if UserSession.is_valid_role(role, auth) and not UserSession.is_authorized_role(role, auth):
                ret = False
        return ret

    def login(self, auth: dict):
        self.token = auth['token']
        self.provider = auth['provider']
        self.token_expiration =  datetime.datetime.strptime(auth['tokenExpiration'], '%Y-%m-%d %H:%M:%S')
        self.hardened = False
        self.management = False
        self.user_management = False
        self.fully_logged_in = UserSession.is_fully_logged_in(auth)
        self.perms = []
        self.roles = []
        self.users = []
        self.managed_roles = []

        # Combine all of the identity information
        for identity in auth['identities']:
            self.add_authenticated_identity(identity)

        # Calculate authorization state from roles and logins
        self.add_authorized_role(auth['baseRole'])
        for role in auth['roles']:
            if UserSession.is_authorized_role(role, auth):
                self.add_authorized_role(role)

        # Create list of roles we manage
        for role in auth['roles']:
            if UserSession.is_authorized_role(role, auth):
                self.add_managed_roles(role['managedRoles'])

        self.save()

    def save(self):
        try:
            session['guardian'] = self.to_dict()
        except:
            pass

    @staticmethod
    def get():
        ret = UserSession()
        try:
            if 'guardian' in session:
                ret.from_dict(session['guardian'])
        except:
            pass
        # Update last access time
        ret.last_access = datetime.datetime.utcnow()
        return ret

    def to_dict(self):
        return {
            "users": self.users,
            "perms": self.perms,
            "roles": self.roles,
            "managed_roles": self.managed_roles,
            "token": self.token,
            "auth": self.auth,
            "provider": self.provider,
            "token_expiration": self.token_expiration,
            "hardened": self.hardened,
            "management": self.management,
            "user_management": self.user_management,
            "fully_logged_in": self.fully_logged_in,
        }

    def from_dict(self, serial: dict):
        self.users = serial['users']
        self.perms = serial['perms']
        self.roles = serial['roles']
        self.managed_roles = serial['managed_roles']
        self.token = serial['token']
        self.auth = serial['auth']
        self.provider = serial['provider']
        self.token_expiration = serial['token_expiration']
        self.hardened = serial['hardened']
        self.management = serial['management']
        self.user_management = serial['user_management']
        self.fully_logged_in = serial['fully_logged_in']

