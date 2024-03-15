from rkweb.auth import login_required
from rkweb.flaskutils import Blueprint, respond, abort

from rkweb.rkserver import ServerConn, ExcryptMsg
from rkweb.session import AuthSession
from rkweb.lilmodels.base import Model, field

# Blueprint
def OtpBlueprintV1():
    blp = Blueprint(
        "One Time Passwords",
        "otp",
        url_prefix="/otp",
        description="Manage One Time Passwords",
    )
    define_get_token(blp)
    define_delete_token(blp)
    define_start_register(blp)
    define_finish_register(blp)
    return blp

def check_error(rsp: ExcryptMsg) -> None:
    if rsp.get_tag("AN") != "Y":
        msg = rsp.to_error()
        if rsp.get_tag("AN") == "P":
            abort(401, msg)
        else:
            abort(400, msg)

def define_get_token(blp):
    class UserToken(Model):
        token: str = field(description="Identifier of identity's OTP token")

    @blp.fxroute(
        endpoint="/tokens/<identityUuid>",
        method="GET",
        description="Retrieve identity's OTP tokens",
        resp_schemas={
            200: UserToken,
        })
    @login_required()
    async def get(identityUuid):

        jwt = AuthSession.auth_token()

        # Request all auth mechanisms
        req = ExcryptMsg("[AOTOTP;]")
        req.set_tag("OP", "list-tokens")
        req.set_tag("ID", identityUuid)
        req.set_tag("JW", jwt)
        rsp = await ServerConn().send_excrypt(req)
        check_error(rsp)

        data = {
            'token': None if len(rsp.get_tag("TO")) == 0 else rsp.get_tag("TO"),
        }

        respond(200, data)

def define_delete_token(blp):
    @blp.fxroute(
        endpoint="/tokens/<identityUuid>",
        method="DELETE",
        description="Unassign an identity's OTP token",
        )
    @login_required()
    async def remove(identityUuid):

        jwt = AuthSession.auth_token()

        # Request all auth mechanisms
        req = ExcryptMsg("[AOTOTP;]")
        req.set_tag("OP", "remove-token")
        req.set_tag("ID", identityUuid)
        req.set_tag("JW", jwt)
        rsp = await ServerConn().send_excrypt(req)
        check_error(rsp)

        respond(200)

def define_start_register(blp):
    class RegisterOtpChallenge(Model):
        sessionId: str = field(description="Session identifier for this register operation")
        secret: str = field(description="Base32 encoded secret")
        uri: str = field(description="URI formatted secret")

    @blp.fxroute(
        endpoint="/register/<identityUuid>",
        method="GET",
        description="Retrieve secret for new OTP token registration",
        resp_schemas={
            200: RegisterOtpChallenge,
        })
    @login_required()
    async def start(identityUuid):

        jwt = AuthSession.auth_token()

        # Request all auth mechanisms
        req = ExcryptMsg("[AOTOTP;]")
        req.set_tag("OP", "get-seed")
        req.set_tag("ID", identityUuid)
        req.set_tag("JW", jwt)
        rsp = await ServerConn().send_excrypt(req)
        check_error(rsp)

        data = {
            'sessionId': rsp.get_tag("RF"),
            'secret': rsp.get_tag("BO"),
            'uri': rsp.get_tag("UI"),
        }

        respond(200, data)

def define_finish_register(blp):
    class RegisterResponse(Model):
        sessionId: str = field(description="Session identifier for this register operation")
        verify: str = field(description="OTP value to verify against")

    @blp.fxroute(
        endpoint="/register/<identityUuid>",
        method="POST",
        description="Challenge response that assigns token to user",
        schema=RegisterResponse,
        )
    @login_required()
    async def finish(args, identityUuid):

        jwt = AuthSession.auth_token()

        # Request all auth mechanisms
        req = ExcryptMsg("[AOTOTP;]")
        req.set_tag("OP", "verify-seed")
        req.set_tag("ID", identityUuid)
        req.set_tag("RF", args['sessionId'])
        req.set_tag("CH", args['verify'])
        req.set_tag("JW", jwt)
        rsp = await ServerConn().send_excrypt(req)
        check_error(rsp)

        respond(200)
