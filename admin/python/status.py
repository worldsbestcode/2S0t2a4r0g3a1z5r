from rkweb.flaskutils import Blueprint, respond
from rkweb.protoflask import proto_to_dict
from rkweb.lilmodels.base import Model, field
from rkweb.rkserver import ExcryptMsg, ServerConn
from rkweb.ipc import IpcUtils

from rkproto.admin.ApplianceMode_pb2 import GetApplianceMode, GetApplianceModeResponse

from adminifx import AdminIfx

import json
from google.protobuf import json_format

# Blueprint
def StatusBlueprintV1():
    blp = Blueprint("Status", "status", url_prefix="/", description="Administration statuses")
    define_isup(blp)
    define_mode(blp)
    return blp

def define_isup(blp):
    class IsUpResponse(Model):
        isup: bool = field(description="If the services are ready")

    @blp.fxroute(
        endpoint="/isup",
        method="GET",
        description="Check if the services are ready",
        resp_schemas={
            200: IsUpResponse,
        })
    async def isup():
        serverIsUp = False
        try:
            # Ping rkserver
            server = ServerConn()
            msg = ExcryptMsg("[AOECHO;]")
            rsp = await server.send_excrypt(msg)

            # Check auth microservice status
            response_json = await IpcUtils.send_json(port=1865, data=json.dumps({'command': 'ping'}))
            rsp_data = json.loads(response_json)
            serverIsUp = rsp_data["enabled"]
        except:
            pass
        respond(200, {'isup': serverIsUp})

def define_mode(blp):
    class ModeResponse(Model):
        hardware: bool = field(description="Hardware appliance or virtual container")
        release: bool = field(description="Server was built in release mode or development mode")
        cloud: bool = field(description="VirtuCrypt cloud server")

    @blp.fxroute(
        endpoint="/appliance-mode",
        method="GET",
        description="Get the appliance mode",
        resp_schemas={
            200: ModeResponse,
        })
    async def mode():
        # Forward to microservice
        rsp = await AdminIfx().send(GetApplianceMode(), GetApplianceModeResponse)

        # Convert to dictionary
        data = proto_to_dict(rsp)

        respond(200, data)
