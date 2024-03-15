from rkweb.flaskutils import Blueprint, respond
from rkweb.login import login_jwt
from rkweb.auth_models import LoginIntentResponse
from rkweb.protoflask import args_to_proto, proto_to_dict

from mm_rkproto.admin.DefaultLogin import rkproto_admin_ChangeDefaultLogin
from rkproto.admin.DefaultLogin_pb2 import ChangeDefaultLogin, ChangeDefaultLoginResponse

from adminifx import AdminIfx
from google.protobuf import json_format

import json

# Blueprint
def DefaultLoginBlueprintV1():
    blp = Blueprint("Change Default Login", "init", url_prefix="/init",
        description="Performs initial provisioning of device")
    define_change_login(blp)
    return blp

def define_change_login(blp):
    @blp.fxroute(
        endpoint="",
        method="POST",
        description="Initialize device and change default credentials",
        schema=rkproto_admin_ChangeDefaultLogin,
        resp_schemas={
            200: LoginIntentResponse,
        })
    async def change(req):
        msg = args_to_proto(req, ChangeDefaultLogin)

        # Forward to microservice
        rsp = await AdminIfx().send(msg, ChangeDefaultLoginResponse)

        # Convert to dictionary
        data = proto_to_dict(rsp)

        # Update login state
        await login_jwt({
            'authCredentials': {
                'token': data['authToken'],
            }})
