import base64
import binascii

from rkweb.lilmodels.base import Model, field

from rkweb.login import login_jwt, get_login_state
from rkweb.session import AuthSession
from rkweb.rkserver import ExcryptMsg, ServerConn
from rkweb.flaskutils import Blueprint, abort, respond, unauthorized
from rkweb.auth_models import LoginIntentResponse

# Blueprint
blp = Blueprint("changepw", "changepw", url_prefix="/changepw", description="Change password for logged in users")
def ChangePwBlueprint():
    return blp

# POST /
class ChangePassword(Model):
    username: str = field(description="The username for the identity to change the password")
    oldPassword: str = field(description="The current password for the user")
    newPassword: str = field(description="The new password for the user")

@blp.fxroute(
    endpoint="",
    method="POST",
    schema=ChangePassword,
    resp_schemas={
        200: LoginIntentResponse,
    },
    description="Change password for a logged in user")
async def post(args):

    session = AuthSession.get()

    # Only allowed to change logged in users
    username = args['username']
    user = None
    for curuser in session.users:
        if curuser['name'] == username:
            user = curuser
            break
    if not user:
        unauthorized("User {} not logged in.".format(username))

    # base64 -> hex
    old_pw = binascii.hexlify(base64.b64decode(args['oldPassword'])).decode('utf-8')
    new_pw = binascii.hexlify(base64.b64decode(args['newPassword'])).decode('utf-8')

    # Send password change request
    msg = ExcryptMsg("[AORKNP;]")
    msg.set_tag("UN", username)
    msg.set_tag("PW", old_pw)
    msg.set_tag("PX", new_pw)
    msg.set_tag("JW", session.get_token())
    rsp = await ServerConn().send_excrypt(msg)
    if rsp.get_tag("AN") != "Y":
        abort(500, "Failed to change password: {}".format(rsp.get_tag("ER")))

    # No longer expired
    session.unexpire(username)

    # If we got a new JWT, update the auth state
    if rsp.get_tag("JW"):
        # Note this will respond for us
        await login_jwt({
            'authCredentials': {
                'token': rsp.get_tag("JW"),
            },
            'refresh': True,
            'cacheBust': True,
        })
        return

    # Respond with auth state
    data = get_login_state(session)
    respond(200, data)
