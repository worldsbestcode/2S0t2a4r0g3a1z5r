from rkweb.auth import login_required
from rkweb.flaskutils import Blueprint, respond, abort

from rkweb.rkserver import ServerConn, ExcryptMsg
from rkweb.session import AuthSession
from rkweb.lilmodels.base import Model, field

from typing import List

import json
import base64

# Blueprint
def FidoBlueprintV1():
    blp = Blueprint(
        "FIDO 2-Factor Authentication",
        "fido",
        url_prefix="/fido",
        description="Manage FIDO U2F Tokens",
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
    class FidoToken(Model):
        issuedTime: str = field(description="Time (UTC) token was issued")
        name: str = field(description="User chose name of token")
        credentialId: str = field(description="Token chosen credential identifier")
        origin: str = field(description="HTTP origin credential is bound to")

    class FidoTokens(Model):
        tokens: List[FidoToken] = field(description="FIDO tokens associated with user.")

    @blp.fxroute(
        endpoint="/tokens/<identityUuid>",
        method="GET",
        description="Retrieve identity's FIDO tokens",
        resp_schemas={
            200: FidoTokens,
        })
    @login_required()
    async def get(identityUuid):

        jwt = AuthSession.auth_token()

        # Request all auth mechanisms
        req = ExcryptMsg("[AOFIDO;]")
        req.set_tag("OP", "list-tokens")
        req.set_tag("ID", identityUuid)
        req.set_tag("JW", jwt)
        rsp = await ServerConn().send_excrypt(req)
        check_error(rsp)

        tokens = json.loads(base64.b64decode(rsp.get_tag("TO")).decode('utf-8'))

        data = {
            'tokens': tokens,
        }

        respond(200, data)

def define_delete_token(blp):
    @blp.fxroute(
        endpoint="/tokens/<identityUuid>/<tokenName>",
        method="DELETE",
        description="Unassign an identity's FIDO token",
        )
    @login_required()
    async def remove(identityUuid, tokenName):

        jwt = AuthSession.auth_token()

        # Request all auth mechanisms
        req = ExcryptMsg("[AOFIDO;]")
        req.set_tag("OP", "remove-token")
        req.set_tag("ID", identityUuid)
        req.set_tag("NA", tokenName)
        req.set_tag("JW", jwt)
        rsp = await ServerConn().send_excrypt(req)
        check_error(rsp)

        respond(200)

def define_start_register(blp):
    class RegisterFidoChallenge(Model):
        sessionId: str = field(description="Session identifier")
        challenge: str = field(description="Base64 challenge for token")

    @blp.fxroute(
        endpoint="/register/<identityUuid>/<tokenName>",
        method="GET",
        description="Retrieve challenge for registering new FIDO token",
        resp_schemas={
            200: RegisterFidoChallenge,
        })
    @login_required()
    async def start(identityUuid, tokenName):

        jwt = AuthSession.auth_token()

        # Request all auth mechanisms
        req = ExcryptMsg("[AOFIDO;]")
        req.set_tag("OP", "get-challenge")
        req.set_tag("ID", identityUuid)
        req.set_tag("NA", tokenName)
        req.set_tag("JW", jwt)
        rsp = await ServerConn().send_excrypt(req)
        check_error(rsp)

        data = {
            'sessionId': rsp.get_tag("CH"),
            'challenge': rsp.get_tag("BO"),
        }

        respond(200, data)

def define_finish_register(blp):
    class ChallengeResponse(Model):
        sessionId: str = field(description="Session identifier for this register operation")
        response: str = field(description="Base64 encoded JSON token challenge response")

    class RegisterSuccess(Model):
        origin: str = field(description="The HTTP origin the credential is bound to")
        credentialId: str = field(description="The token chosen credential ID")

    @blp.fxroute(
        endpoint="/register/<identityUuid>",
        method="POST",
        description="Challenge response that assigns token to user",
        schema=ChallengeResponse,
        resp_schemas={
            200: RegisterSuccess,
        })
    @login_required()
    async def finish(args, identityUuid):

        jwt = AuthSession.auth_token()

        # Request all auth mechanisms
        req = ExcryptMsg("[AOFIDO;]")
        req.set_tag("OP", "challenge-response")
        req.set_tag("ID", identityUuid)
        req.set_tag("CH", args['sessionId'])
        req.set_tag("RF", args['response'])
        req.set_tag("JW", jwt)
        rsp = await ServerConn().send_excrypt(req)
        check_error(rsp)

        data = {
            'origin': rsp.get_tag('OR'),
            'credentialId': rsp.get_tag('CI'),
        }

        respond(200, data)
