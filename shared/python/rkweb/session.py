import pytz
import json
import base64
import datetime
import binascii
import subprocess

from flask import session, request

from rkweb.security import new_csrf_token, should_check_origin

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

class AuthSession():
    def __init__(self):
        self.users = []
        self.unexpired = []
        self.last_user = None
        self.perms = []
        self.auth_perms = []
        self.service_perms = []
        self.roles = []
        self.max_roles = []
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
        self.csrf_token = None
        self.check_origin = True
        self.df_session_id = None
        self.df_state = None
        self.pki_session_id = None
        self.has_done_tls_auth = False
        self.has_principal = False
        self.remaining_logins = 2
        self.login_more = True
        self.default_passwords = set()
        self.token_dirty = False
        self.stateless = False

    def get_users(self):
        return self.users

    def get_perms(self):
        return self.perms

    def get_token(self):
        return self.token

    def unexpire(self, user):
        if not user in self.unexpired:
            self.unexpired.append(user)
        self.save()

    @staticmethod
    def dirty():
        state = AuthSession.get()
        state.token_dirty = True
        state.save()

    @staticmethod
    def auth_token():
        try:
            if 'auth' in session and 'token' in session['auth']:
                return session['auth']['token']
        except:
            pass
        return ""

    @staticmethod
    def logout():
        # Clear auth state
        try:
            session.pop('auth')
        except:
            pass

        # Shutdown remote desktop session
        try:
            vnc = session['desktop']
            subprocess.call(["sudo", "/usr/bin/kill-vnc", str(int(vnc['vnc_port']) + 1000)])
        except:
            pass

        try:
            session.clear()
        except:
            pass

    @staticmethod
    def clean_stateless():
        try:
            if session['auth']['stateless']:
                AuthSession.logout()
        except:
            pass

    def add_authenticated_identity(self, identity, expired):
        """
        Adds an identity that is (at least partially) logged in to the session context:

        Args:
            identity: The identity information
            expired: If the login was with an expired credential
        """
        # Server agrees we are no longer expired
        if not expired and identity['name'] in self.unexpired:
            self.unexpired.pop(self.unexpired.index(identity['name']))

        user_info = {
            'id': identity['id'],
            #'uuid': identity.uuid,
            'name': identity['name'],
            'expired': expired and identity['name'] not in self.unexpired,
            'defaultPw': identity['name'] in self.default_passwords,
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
                'principal': role['type'] == 'Principal',
            }
            if role_info['principal']:
                self.has_principal = True
            self.roles.append(role_info)
        self.hardened = role['hardened'] if role['hardened'] else self.hardened
        self.management = role['management'] if role['management'] else self.management
        # Combine perms
        for perm in role['perms']:
            if perm not in self.perms:
                self.perms.append(perm)
                if role['id'] > 0:
                    self.auth_perms.append(perm)
        for service in role['services']:
            if service not in self.service_perms:
                self.service_perms.append(service)

    def add_managed_roles(self, managed_roles):
        if 'Controllable' in managed_roles:
            for managed_role in managed_roles['Controllable']:
                id = managed_role['id']
                uuid = managed_role['uuid']
                name = managed_role['name']
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
                        'name': name,
                        'type': 'Controllable'
                    }
                    self.managed_roles.append(managed_info)

        if 'Assignable' in managed_roles:
            for managed_role in managed_roles['Assignable']:
                id = managed_role['id']
                uuid = managed_role['uuid']
                name = managed_role['name']
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
                        'name': name,
                        'type': 'Assignable'
                    }
                    self.managed_roles.append(managed_info)

        if 'Viewable' in managed_roles:
            for managed_role in managed_roles['Viewable']:
                id = managed_role['id']
                uuid = managed_role['uuid']
                name = managed_role['name']
                found = False
                for cur_managed in self.managed_roles:
                    if cur_managed['id'] == id:
                        found = True
                        break
                if not found:
                    managed_info = {
                        'id': id,
                        'uuid': uuid,
                        'name': name,
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
        ret = AuthSession.is_valid_role(role, auth)

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

    def is_fully_logged_in(self, auth):
        """
        Checks if the authorization state is as logged in as possible,
        or if more authentication can be performed.

        Args:
            auth: The authentication context
        Returns:
            True if fully authorized, False if more authentication can be provided
        """

        # No users
        if len(self.users) == 0:
            return False

        # Expired credential
        for user in self.users:
            if user['expired'] and not user['defaultPw']:
                return False

        # Some role from auth is unauthorized
        for role in self.max_roles:
            if AuthSession.is_valid_role(role, auth) and not AuthSession.is_authorized_role(role, auth):
                return False

        # Reset partial login state
        self.unexpired = []

        return True

    @staticmethod
    def get_df_state(df):
        data = {
            'required': df['required'],
            'method': "OTP" if df['active'] == "TOTP" else df['active'],
        }
        if 'nonce' in df:
            if df['active'] == 'U2F':
                data['nonce'] = binascii.unhexlify(df['nonce'].encode('utf-8')).decode('utf-8')
            else:
                data['nonce'] = df['nonce']
        if 'credential' in df:
            if df['active'] == 'U2F':
                data['credential'] = df['credential'].split(",")
            else:
                data['nonce'] = df['credential']
        if 'origin' in df:
            data['origin'] = df['origin']
        return data

    @staticmethod
    def token_has_expired(token, identity):
        try:
            token_components = token.split(".")
            while len(token_components[1]) % 4 != 0:
                token_components[1] += "="
            payload = json.loads(base64.b64decode(token_components[1]).decode('utf-8'))
            identities = payload['fxidentities'].split(",")
            factors = payload['fxmf'].split(",")
            for i in range(len(identities)):
                if identities[i] == identity and factors[i].startswith('Expired'):
                    return True
        except:
            pass
        return False

    def login(self, auth_rsp: dict, login_more: bool = None, init_csrf: bool = True, stateless: bool = False):
        # Get important parts of the auth response message
        auth = auth_rsp['auth']
        df = None
        if 'dualFactor' in auth_rsp and 'sessionId' in auth_rsp['dualFactor']:
            df = auth_rsp['dualFactor']

        self.auth = auth
        self.token = auth['token']
        self.provider = auth['provider']
        self.token_expiration =  datetime.datetime.strptime(auth['tokenExpiration'], DATETIME_FORMAT)
        self.hardened = False
        self.management = False
        self.user_management = False
        self.fully_logged_in = False
        self.perms = []
        self.auth_perms = []
        self.service_perms = []
        self.roles = []
        self.users = []
        self.managed_roles = []
        self.df_session_id = None
        self.df_state = None
        self.has_principal = False
        self.remaining_logins = 2
        self.token_dirty = False
        self.stateless = stateless
        if login_more != None:
            self.login_more = login_more

        # New for default pw logins
        expiredUser = None
        if auth_rsp.get('passwordDefault'):
            self.default_passwords.add(auth_rsp['user'])
        # Not expired then they cleared default pw
        elif 'user' in auth_rsp and auth_rsp.get('passwordExpired', False):
            expiredUser = auth_rsp['user']
            try:
                self.default_passwords.remove(expiredUser)
            except:
                pass
        if 'user' in auth_rsp:
            self.last_user = auth_rsp['user']

        # Append max roles
        for role in auth['roles']:
            has_role = False
            for saved_role in self.max_roles:
                if saved_role['id'] == role['id']:
                    has_role = True
                    break
            if not has_role:
                self.max_roles.append(role)

        # Calculate max remaining logins
        logins_max = None
        for role in auth['roles']:
            if not logins_max or role['loginsRequired'] > logins_max:
                logins_max = role['loginsRequired']

        # Dual-factor info
        if df:
            self.df_session_id = df['sessionId']
            self.df_state = AuthSession.get_df_state(df)

        # Combine all of the identity information
        for identity in auth['identities']:
            expired = AuthSession.token_has_expired(self.token, identity['name']) or identity['name'] == expiredUser
            self.add_authenticated_identity(identity, expired)

        # Calculate authorization state from roles and logins
        self.add_authorized_role(auth['baseRole'])
        for role in auth['roles']:
            if AuthSession.is_authorized_role(role, auth):
                self.add_authorized_role(role)

        # Do we want any more logins?
        if not self.login_more and self.has_principal:
            self.remaining_logins = 0
            self.fully_logged_in = True
        else:
            if logins_max:
                self.remaining_logins = logins_max - len(auth['identities'])
            self.fully_logged_in = self.is_fully_logged_in(auth)

        # Create list of roles we manage
        for role in auth['roles']:
            if AuthSession.is_authorized_role(role, auth):
                self.add_managed_roles(role['managedRoles'])

        # Setup CSRF and origin checking
        if init_csrf:
            self.init_security()

        self.save()

    def init_security(self):
        self.check_origin = should_check_origin()
        self.csrf_token = new_csrf_token()

    def save(self):
        try:
            session['auth'] = self.to_dict()
        except:
            pass

    @staticmethod
    def get():
        ret = AuthSession()
        try:
            if 'auth' in session:
                ret.from_dict(session['auth'])
                # Update last access time
                now = datetime.datetime.utcnow()
                ret.last_access = now
                session['auth']['last_access'] = now.strftime(DATETIME_FORMAT)
        except:
            pass
        return ret

    def to_dict(self):
        return {
            "users": self.users,
            "unexpired": self.unexpired,
            "last_user": self.last_user,
            "perms": self.perms,
            "auth_perms": self.auth_perms,
            "service_perms": self.service_perms,
            "roles": self.roles,
            "max_roles": self.max_roles,
            "managed_roles": self.managed_roles,
            "token": self.token,
            "auth": self.auth,
            "provider": self.provider,
            "token_expiration": self.token_expiration,
            "hardened": self.hardened,
            "management": self.management,
            "user_management": self.user_management,
            "fully_logged_in": self.fully_logged_in,
            "csrf_token": self.csrf_token,
            "check_origin": self.check_origin,
            "last_access": self.last_access.strftime(DATETIME_FORMAT),
            "df_session_id": self.df_session_id,
            "df_state": self.df_state,
            "pki_session_id": self.pki_session_id,
            "has_done_tls_auth": self.has_done_tls_auth,
            "has_principal": self.has_principal,
            "remaining_logins": self.remaining_logins,
            "login_more": self.login_more,
            "default_passwords": self.default_passwords,
            "dirty": self.token_dirty,
            "stateless": self.stateless,
        }

    def from_dict(self, serial: dict):
        self.users = serial['users']
        self.unexpired = serial['unexpired']
        self.last_user = serial['last_user']
        self.perms = serial['perms']
        self.auth_perms = serial['auth_perms']
        self.service_perms = serial['service_perms']
        self.roles = serial['roles']
        self.max_roles = serial['max_roles']
        self.managed_roles = serial['managed_roles']
        self.token = serial['token']
        self.auth = serial['auth']
        self.provider = serial['provider']
        self.token_expiration = serial['token_expiration']
        self.hardened = serial['hardened']
        self.management = serial['management']
        self.user_management = serial['user_management']
        self.fully_logged_in = serial['fully_logged_in']
        self.csrf_token = serial['csrf_token']
        self.check_origin = serial['check_origin']
        self.last_access = datetime.datetime.strptime(serial['last_access'], DATETIME_FORMAT)
        self.df_session_id = serial['df_session_id']
        self.df_state = serial['df_state']
        self.pki_session_id = serial['pki_session_id']
        self.has_done_tls_auth = serial['has_done_tls_auth']
        self.has_principal = serial['has_principal']
        self.remaining_logins = serial['remaining_logins']
        self.login_more = serial['login_more']
        self.default_passwords = serial['default_passwords']
        self.token_dirty = serial['dirty']
        self.stateless = serial['stateless']
