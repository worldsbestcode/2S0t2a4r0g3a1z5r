#from flask.views import MethodView
from flaskutils import Blueprint, abort, respond

from marshmallow import Schema, fields, validate

import json
import base64

from ipc import IpcUtils
from session import UserSession

# Blueprint
blp = Blueprint("login", "login", url_prefix="/login", description="Authenticate to the server")
def LoginBlueprint():
    return blp

# Login schema
class UserPassCredentials(Schema):
    username = fields.String(
        required=True,
        description="Username",
    )

    password = fields.String(
        required=True,
        description="Base64 password",
    )

class LoginIntent(Schema):
    authType = fields.String(
        required=True,
        description="Login credential type",
        validate=validate.OneOf(["userpass", "pkiChallenge", "pkiSignature", "jwt"]),
    )

    authCredentials = fields.Nested(
        UserPassCredentials,
        required=True,
        description="Login credentials")

    examples = {
        "Password login": {
            "authType": "userpass",
            "authCredentials": {
                "username": "Admin1",
                "password": "c2FmZXN0",
            },
        },
    }

# Login using microservice
async def processLogin(login_type: str, auth_data: dict):
    sess = UserSession.get()
    #req_data["port"] = "Web" # TODO: Enable web login connection type for UserGroups
    if sess.get_token():
        auth_data["token"] = sess.get_token()

    # Send synchronous to auth microservice
    response_json = await IpcUtils.send_json(port=1865, data=json.dumps(auth_data))
    rsp_data = json.loads(response_json)
    if rsp_data["status"] != "success":
        abort(401, rsp_data["error"] if "error" in rsp_data else "Login failed")

    # Save login state
    UserSession.get().login(rsp_data['auth'])

    # Success
    abort(200, "Logged in {}".format(login_type))

# Login
@blp.fxroute(endpoint="", method="POST", schema=LoginIntent, description="Login session")
async def login(args):
    # Only user/pass right now
    if args['authType'] in ["pkiChallenge", "pkiSignature"]:
        abort(405, "PKI authentication not supported")
    elif args['authType'] in ["jwt"]:
        abort(405, "JWT authentication not supported on this API. Use /login/jwt")

    # Get password login input
    username = args['authCredentials']['username']
    password = args['authCredentials']['password']

    # Build auth request
    req_data = {}
    req_data["command"] = "login-pw"
    req_data["user"] = username
    req_data["password"] = password

    # Login
    await processLogin("user {}".format(username), req_data)


# XXX: Deprecate when you get union working
class JwtCredentials(Schema):
    token = fields.String(
        required=True,
        description="JSON web token",
    )

class LoginIntentJwt(Schema):
    authType = fields.String(
        required=True,
        description="Login credential type",
        validate=validate.OneOf(["jwt"]),
    )

    authCredentials = fields.Nested(
        JwtCredentials,
        required=True,
        description="Login credentials")

    examples = {
        "JWT login": {
            "authType": "jwt",
            "authCredentials": {
                "token": "eyJhbGciOiJIUzI1...",
            },
        },
    }

# Login JWT (Deprecated)
@blp.fxroute(endpoint="/jwt", method="POST", schema=LoginIntentJwt, description="Login session with JWT")
async def loginJwt(args):
    # Only JWT login on this endpoint
    if len(args["authCredentials"]["token"]) <= 0:
        abort(405, "JSON web token required.")

    # Build login request
    req_data = {}
    req_data["command"] = "login-token"
    req_data["token"] = args["authCredentials"]["token"]

    # Process login
    await processLogin("JWT", req_data)

# Login JWT (Deprecated)
@blp.fxroute(endpoint="", method="GET", schema=None, description="Get login status")
async def loginStatus():

    session = UserSession.get()

    # Check current token is still valid
    if session.get_token():
        auth_data = {}
        auth_data["command"] = "login-token"
        auth_data["token"] = session.get_token()

        try:
            response_json = await IpcUtils.send_json(port=1865, data=json.dumps(auth_data))
            rsp_data = json.loads(response_json)
            if rsp_data["status"] != "success":
                UserSession.logout()
                session = UserSession()
        except RuntimeError as e:
            UserSession.logout()
            session = UserSession()

    rsp_data = {}
    rsp_data['users'] = session.users
    rsp_data['perms'] = session.perms
    rsp_data['roles'] = session.roles
    rsp_data['managed_roles'] = session.managed_roles
    rsp_data['hardened'] = session.hardened
    rsp_data['management'] = session.management
    rsp_data['user_management'] = session.user_management
    rsp_data['fully_logged_in'] = session.fully_logged_in
    rsp_data['token'] = session.token
    rsp_data['token_expiration'] = session.token_expiration.strftime("%Y-%m-%d %H:%M:%S")
    # TODO: Make schema
    respond(200, rsp_data)

