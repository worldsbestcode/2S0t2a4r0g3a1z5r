from rkweb.auth import perm_required
from rkweb.flaskutils import Blueprint, respond
from rkweb.protoflask import args_to_proto, proto_to_dict

from mm_rkproto.admin.RemoteDrives import rkproto_admin_RetrieveRemoteDrivesResponse

from rkproto.admin.RemoteDrives_pb2 import RetrieveRemoteDrives, RetrieveRemoteDrivesResponse

from adminifx import AdminIfx

import json
from google.protobuf import json_format

# Blueprint
def RemoteDrivesBlueprintV1():
    blp = Blueprint("Remote Drives", "remote_drives", url_prefix="/drives", description="Remote drives")
    define_retrieve(blp)
    return blp

def define_retrieve(blp):
    @blp.fxroute(
        endpoint="",
        method="GET",
        description="Retrieve available remote drives",
        resp_schemas={
            200: rkproto_admin_RetrieveRemoteDrivesResponse,
        })
    @perm_required("System:Administration")
    async def retrieveRemoteDrives():
        # Forward to microservice
        msg = RetrieveRemoteDrives()
        rsp = await AdminIfx.send(msg, RetrieveRemoteDrivesResponse)

        # Convert to dictionary
        data = proto_to_dict(rsp)
        respond(200, data)
