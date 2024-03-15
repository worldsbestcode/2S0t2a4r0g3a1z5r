from functools import wraps
from urllib.parse import urlsplit

from flask import request

from rkweb.session import AuthSession
from rkweb.config import WebConfig
from rkweb.flaskutils import unauthenticated, unauthorized, abort_bad_csrf, abort_not_logged_in
from rkweb.login import login_tls, login_bearer_token, refresh_jwt
from rkweb.security import get_client_type, ClientType

async def check_login(sess):
    # Check something is logged in
    # Try Bearer token login if not logged in
    if len(sess.perms) == 0 or len(sess.users) == 0:
        await login_bearer_token(sess)

    # Try TLS login if not logged in
    if len(sess.perms) == 0 or len(sess.users) == 0:
        if not sess.has_done_tls_auth:
            await login_tls(sess)

    if len(sess.perms) == 0 or len(sess.users) == 0:
        abort_not_logged_in()

    # Need to get a new token
    if sess.token_dirty:
        await refresh_jwt(sess)

def check_token(sess):
    # CSRF not required for this user
    if not sess.csrf_token:
        return

    # Check CSRF token
    request_token = request.headers.get('X-Fxsrf-Token')
    if not request_token or request_token != sess.csrf_token:
        abort_bad_csrf()

async def check_origin(sess):
    # Origin check not required for this user
    if not sess.check_origin:
        return

    # Check if the valid origins is able to be initialized
    valid_origins = await WebConfig.get_origins()
    if len(valid_origins) == 0:
        print("No valid origins configured.")
        return

    # Anything goes
    if '*' in valid_origins:
        return

    # Allow localhost origin when using local cardbrowser dashboard
    if request.environ['SERVER_PORT'] == '9876':
        valid_origins = set(valid_origins) # Make local copy
        valid_origins.add("https://127.0.0.1:9876")
        valid_origins.add("https://localhost:9876")

    # Check origin
    request_origin = request.headers.get('Origin')
    if request_origin in valid_origins:
        return

    # Origin is bad or missing, try referer
    def valid_referer(referer, valid_origins):
        if referer is None:
            return False

        referer_split = urlsplit(referer)
        referer_base = referer_split.scheme + "://" + referer_split.netloc
        return referer_base in valid_origins

    # Check referer
    request_referer = request.headers.get('Referer')
    if not valid_referer(request_referer, valid_origins):
        unauthenticated("Invalid Origin or Referer")

async def check_csrf_login():
    # Get login state
    sess = AuthSession.get()

    # Check login status
    await check_login(sess)

    # Check CSRF token
    check_token(sess)

    # Check origin/referer
    await check_origin(sess)

    return sess

def user_login_required():
    def wrapper(func):
        @wraps(func)
        async def check_csrf_login_wrapper(*args, **kwargs):
            await check_csrf_login()
            current_type = get_client_type()
            if not current_type in [ClientType.WebUser, ClientType.Securus]:
                unauthorized("Invalid client type.")
            # Forward to view
            return await func(*args, **kwargs)

        return check_csrf_login_wrapper
    return wrapper

def login_required(client_type=None):
    def wrapper(func):
        @wraps(func)
        async def check_csrf_login_wrapper(*args, **kwargs):
            await check_csrf_login()
            # Forward to view
            return await func(*args, **kwargs)

        return check_csrf_login_wrapper
    return wrapper

def perm_required(perm):
    def wrapper(func):
        @wraps(func)
        async def perm_check(*args, **kwargs):
            # Get login state
            sess = await check_csrf_login()
            # Check permissions
            if len(sess.perms) == 0 or len(sess.users) == 0 or not perm in sess.perms:
                unauthorized("Missing permission {}".format(perm))
            # Forward to view
            return await func(*args, **kwargs)

        return perm_check
    return wrapper

def perms_required(perms):
    def wrapper(func):
        @wraps(func)
        async def perm_check(*args, **kwargs):
            # Get login state
            sess = await check_csrf_login()
            # Check permissions
            if len(sess.perms) == 0 or len(sess.users) == 0 or not all(perm in sess.perms for perm in perms):
                unauthorized("Missing permission set ({})".format(",".join(perms)))
            # Forward to view
            return await func(*args, **kwargs)

        return perm_check
    return wrapper

def one_perm_required(perms):
    def wrapper(func):
        @wraps(func)
        async def perm_check(*args, **kwargs):
            # Get login state
            sess = await check_csrf_login()
            # Check permissions
            if len(sess.perms) == 0 or len(sess.users) == 0 or not any(perm in sess.perms for perm in perms):
                unauthorized("Missing one permission of ({})".format(",".join(perms)))
            # Forward to view
            return await func(*args, **kwargs)

        return perm_check
    return wrapper

