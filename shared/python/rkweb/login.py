import json
import base64
import binascii

from flask import redirect, request

from rkweb import rkserver
from rkweb.ipc import IpcUtils
from rkweb.config import WebConfig
from rkweb.session import AuthSession
from rkweb.security import is_api_user
from rkweb.flaskutils import Blueprint, abort, respond, abort_bad_csrf

from rkweb.auth_models import LoginIntent, LoginIntentResponse

def get_auth_session():
    session = AuthSession.get()

    # If they're logged in, verify CSRF
    if session.csrf_token:
        request_token = request.headers.get('X-Fxsrf-Token')
        # Mismatch = No authorization
        if not request_token or request_token != session.csrf_token:
            session.logout()
            session = AuthSession()
    return session

# Build LoginCompleteResponse
def get_login_state(session):
    rsp_data = {}
    rsp_data['users'] = session.users
    rsp_data['perms'] = session.perms
    rsp_data['authPerms'] = session.auth_perms
    rsp_data['roles'] = session.roles
    rsp_data['managedRoles'] = session.managed_roles
    rsp_data['hardened'] = session.hardened
    rsp_data['management'] = session.management
    rsp_data['userManagement'] = session.user_management
    rsp_data['fullyLoggedIn'] = session.fully_logged_in
    rsp_data['token'] = session.token
    rsp_data['tokenExpiration'] = session.token_expiration.strftime("%Y-%m-%d %H:%M:%S")
    rsp_data['hasPrincipal'] = session.has_principal
    rsp_data['remainingLogins'] = session.remaining_logins
    if session.df_state:
        rsp_data['dualFactor'] = session.df_state
    return rsp_data

def set_source(auth_data: dict):
    if request.environ['SERVER_PORT'] == '9876':
        auth_data["source"] = "CLIENT"
    elif is_api_user():
        auth_data["source"] = "REST"
    else:
        auth_data["source"] = "WEB"

# Send auth command to microservice
async def sendCommand(sess: AuthSession, auth_data: dict):
    set_source(auth_data)
    if not 'token' in auth_data and sess.get_token():
        auth_data["token"] = sess.get_token()

    # Send synchronous to auth microservice
    response_json = await IpcUtils.send_json(port=1865, data=json.dumps(auth_data))
    rsp_data = json.loads(response_json)
    if rsp_data["status"] != "success":
        abort(401, rsp_data["error"] if "error" in rsp_data else "Login failed")

    return rsp_data

# Login using microservice
async def processLogin(login_type: str, auth_data: dict):
    sess = get_auth_session()
    rsp_data = await sendCommand(sess, auth_data)

    # Save login state
    sess.login(rsp_data)

    # Build output
    msg = get_login_state(sess)

    respond(200, msg, sess.csrf_token)

# Generate nonce challenge
async def processChallenge(auth_data: dict):
    sess = get_auth_session()
    rsp_data = await sendCommand(sess, auth_data)

    # Save session ID
    sess.pki_session_id = rsp_data['sessionId']
    sess.save()

    # Build PkiChallengeResponse
    msg = {}
    msg['challenge'] = rsp_data['nonce']

    respond(200, msg, sess.csrf_token)

# Blueprint
blp = Blueprint("login", "login", url_prefix="/login", description="Authenticate to the server")
def LoginBlueprint():
    return blp

# POST /
# Login
@blp.fxroute(
    endpoint="",
    method="POST",
    schema=LoginIntent,
    resp_schemas={
        200: LoginIntentResponse,
    },
    description="Login session")
async def login(args):
    if args['authType'] == "jwt":
        await login_jwt(args)
    elif args['authType'] == "userpass":
        await login_user(args)
    elif args['authType'] == "pkiChallenge":
        await get_challenge(args)
    elif args['authType'] == "pkiSignature":
        await login_pki(args)
    elif args['authType'] == "fido":
        await login_fido(args)
    elif args['authType'] == "otp":
        await login_otp(args)
    else:
        abort(400, "Invalid authType")

async def refresh_jwt(sess):
    req_data = {
        "command": "login-token",
        "token": sess.token,
        "cacheBust": True,
        "refresh": True,
    }
    set_source(req_data)

    # Send synchronous to auth microservice
    response_json = await IpcUtils.send_json(port=1865, data=json.dumps(req_data))
    rsp_data = json.loads(response_json)
    if rsp_data["status"] != "success":
        abort(401, rsp_data["error"] if "error" in rsp_data else "Token refresh failed.")

    sess.login(rsp_data, init_csrf=False)

async def login_jwt(args):
    # Build login request
    req_data = {}
    req_data["command"] = "login-token"
    req_data["token"] = args["authCredentials"]["token"]
    if "cacheBust" in args:
        req_data["cacheBust"] = args["cacheBust"]
    if "refresh" in args:
        req_data["refresh"] = args["refresh"]

    # Process login
    await processLogin("JWT", req_data)

async def login_bearer_token(sess):
    auth_token = None
    # Try to find JWT
    for header in await WebConfig.get_jwt_headers():
        try:
            auth_header = request.headers.get(header)
            auth_token = auth_header.split(" ")[1]
            break
        except:
            pass
    # Else try to find API key
    if not auth_token:
        for header in await WebConfig.get_api_key_headers():
            auth_header = request.headers.get(header)
            if auth_header:
                auth_token = "API:" + auth_header
                break
    if auth_token:
        # Build login request
        req_data = {}
        req_data["command"] = "login-token"
        req_data["token"] = auth_token

        # Send to auth service
        rsp_data = await sendCommand(sess, req_data)

        # Save login state
        sess.login(rsp_data, stateless=True)

async def init_server_tasks(sess):
    # Send RKFL to do admin sync login tasks
    try:
        excrypt = rkserver.ExcryptMsg("[AORKFL;]")
        excrypt.set_tag("JW", sess.token)
        await rkserver.ServerConn().send_excrypt(excrypt)
    except:
        pass

async def login_user(args):
    # Get password login input
    username = args['authCredentials']['username']
    password = args['authCredentials']['password']

    # Build auth request
    req_data = {}
    req_data["command"] = "login-pw"
    req_data["user"] = username
    req_data["password"] = password

    # Send to auth service
    sess = get_auth_session()
    rsp_data = await sendCommand(sess, req_data)

    # Save login state
    sess.login(rsp_data, args['authCredentials'].get('multiLogin'))

    # Tell server it can do admin login tasks (if applicable)
    await init_server_tasks(sess)

    # Respond
    msg = get_login_state(sess)
    respond(200, msg, sess.csrf_token)

# Decode base 64 and convert to hex
def b64tohex(value):
    return binascii.hexlify(base64.b64decode(value)).decode('utf-8')

async def get_challenge(args):
    # Get cert input
    certs = args['authCredentials']['certData']
    if isinstance(certs, str):
        certs = [certs]
    certs = [b64tohex(cert) for cert in certs]
    cert = certs[0]
    cert_chain = certs[1:]

    # Build request
    req_data = {}
    req_data["command"] = "login-pki"
    req_data["cert"] = cert
    req_data["certChain"] = cert_chain

    # Get challenge
    await processChallenge(req_data)

async def login_pki(args):
    # Get session with PKI login in progress
    sess = get_auth_session()
    if not sess.pki_session_id:
        abort(400, "No nonce session in progress")

    # Get signature
    signature = args['authCredentials']['signature']
    signature = b64tohex(signature)

    # Pop PKI session ID
    session_id = sess.pki_session_id
    sess.pki_session_id = None
    sess.save()

    # Build auth request
    req_data = {}
    req_data["command"] = "challenge-response"
    req_data["sessionId"] = session_id
    req_data["answer"] = {
        "challengeResponse": signature
    }

    # Login
    await processLogin("PKI login", req_data)

# Read multiple PEM encoded certs from a file
# Return a list of hex-encoded DER certificates
def read_all_certs(cert_file):
    # Parse out the list of certificates
    certs = cert_file.split('-----BEGIN CERTIFICATE-----')[1:]

    result = []
    for cert in certs:
        # Parse PEM and encode to DER
        cert = cert.strip()
        cert = ''.join(cert.splitlines()[:-1])
        cert = b64tohex(cert)

        result.append(cert)

    return result

async def login_tls(sess):
    # Mark the session as having tried TLS auth
    sess.has_done_tls_auth = True
    sess.save()

    # Get client cert from environment variables
    cert = request.environ['SSL_CLIENT_CERT']

    if cert:
        # Strip PEM headers and convert to DER
        cert = ''.join(cert.splitlines()[1:-1])
        cert = b64tohex(cert)

        cert_chain = []
        # Read verification certs from filesystem
        with open('/var/run/fx/nginx/certificates/dashboard_verification.pem', 'r') as f:
            cert_chain = read_all_certs(f.read())

        # Build request
        req_data = {}
        req_data["command"] = "login-tls"
        req_data["peer"] = cert
        req_data["certChain"] = cert_chain

        # Send to auth service
        rsp_data = await sendCommand(sess, req_data)

        # Save login state
        sess.login(rsp_data)

async def login_fido(args):
    # Get session with DF login in progress
    sess = get_auth_session()
    if not sess.df_session_id:
        abort(400, "No dual-factor session in progress")

    # Get password login input
    response = args['authCredentials']['response']
    response = b64tohex(response)

    # Pop DF session ID
    session_id = sess.df_session_id
    sess.df_session_id = None
    sess.save()

    # Build auth request
    req_data = {}
    req_data["command"] = "challenge-response"
    req_data["sessionId"] = session_id
    req_data["answer"] = {
        "challengeResponse": response
    }

    # Login
    await processLogin("FIDO login", req_data)

async def login_otp(args):
    # Get session with DF login in progress
    sess = get_auth_session()
    if not sess.df_session_id:
        abort(400, "No dual-factor session in progress")

    # Get password login input
    otp = args['authCredentials']['password']

    # Pop DF session ID
    session_id = sess.df_session_id
    sess.df_session_id = None
    sess.save()

    # Build auth request
    req_data = {}
    req_data["command"] = "challenge-response"
    req_data["sessionId"] = session_id
    req_data["answer"] = {
        "challengeResponse": binascii.hexlify(otp.encode('utf-8')).decode('utf-8'),
    }

    # Login
    await processLogin("OTP login", req_data)

async def start_df(sess):
    # Already started
    if sess.df_session_id:
        return
    # Not in DF state
    if not sess.df_state:
        return

    req_data = {}
    req_data["command"] = "df-start"
    req_data["identity"] = sess.last_user
    req_data["method"] = sess.df_state['method']
    req_data["token"] = sess.token

    # Send synchronous to auth microservice
    try:
        response_json = await IpcUtils.send_json(port=1865, data=json.dumps(req_data))
        rsp_data = json.loads(response_json)
        if rsp_data["status"] == "success":
            # Save df state
            sess.df_session_id = rsp_data['sessionId']
            sess.df_state = AuthSession.get_df_state(rsp_data)
            sess.save()
    except Exception as e:
        pass

# GET /
# Get login status
@blp.fxroute(
    endpoint="",
    method="GET",
    schema=None,
    resp_schemas={
        200: LoginIntentResponse,
    },
    description="Get login status"
)
async def loginStatus():

    session = get_auth_session()

    # Check current token is still valid
    if session.get_token():
        auth_data = {}
        auth_data["command"] = "login-token"
        auth_data["token"] = session.get_token()
        auth_data["refresh"] = True
        set_source(auth_data)

        try:
            response_json = await IpcUtils.send_json(port=1865, data=json.dumps(auth_data))
            rsp_data = json.loads(response_json)
            if rsp_data["status"] != "success":
                AuthSession.logout()
                session = AuthSession()
            else:
                await start_df(session)
        except RuntimeError as e:
            AuthSession.logout()
            session = AuthSession()

    respond(200, get_login_state(session))


# Logout
blpLogout = Blueprint("logout", "logout", url_prefix="/logout", description="Terminate authentication session")
def LogoutBlueprint():
    return blpLogout

# POST /
@blpLogout.fxroute(endpoint="", method="POST", description="Logout session")
async def logout():
    AuthSession.logout()
    respond(200)

# GET /
@blpLogout.fxroute(endpoint="", method="GET", description="Logout session and redirect")
async def getLogout():
    AuthSession.logout()
    return redirect("/", code=200)
