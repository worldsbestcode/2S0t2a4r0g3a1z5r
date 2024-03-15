from rkweb.auth import perm_required
from rkweb.flaskutils import Blueprint, respond
from rkweb.protoflask import args_to_proto, proto_to_dict

from mm_rkproto.admin.DateTime import rkproto_admin_GetDateTimeResponse
from mm_rkproto.admin.DateTime import rkproto_admin_SetDateTime

from rkproto.admin.DateTime_pb2 import GetDateTime, GetDateTimeResponse
from rkproto.admin.DateTime_pb2 import SetDateTime

from adminifx import AdminIfx

import json
from google.protobuf import json_format

# Blueprint
def DateTimeBlueprintV1():
    blp = Blueprint("Date/Time", "date_time", url_prefix="/time", description="Date/time and NTP")
    define_get(blp)
    define_set(blp)
    return blp

def define_get(blp):
    @blp.fxroute(
        endpoint="",
        method="GET",
        description="Get the current date, time/zone, and NTP servers",
        resp_schemas={
            200: rkproto_admin_GetDateTimeResponse,
        })
    @perm_required("System:Administration")
    async def getDateTime():
        # Forward to microservice
        msg = GetDateTime()
        rsp = await AdminIfx.send(msg, GetDateTimeResponse)

        # Convert to dictionary
        data = proto_to_dict(rsp)
        respond(200, data)

def define_set(blp):
    @blp.fxroute(
        endpoint="",
        method="POST",
        description="Set the current date, time/zone, and NTP servers",
        schema=rkproto_admin_SetDateTime)
    @perm_required("System:Administration")
    async def setDateTime(req):
        # To protobuf
        msg = args_to_proto(req, SetDateTime)

        # Forward to microservice
        await AdminIfx.send(msg, None)
        respond(200)
