from rkweb.auth import perm_required
from rkweb.flaskutils import Blueprint, respond
from rkweb.protoflask import proto_to_dict

from rkproto.applogs.RetrieveFiles_pb2 import RetrieveFiles, RetrieveFilesResponse
from mm_rkproto.applogs.RetrieveFiles import rkproto_applogs_RetrieveFilesResponse

from applogsifx import ApplogsIfx

# Blueprint
blp = Blueprint("Log Files", "files", url_prefix="/files", description="Application Log Files")
def FilesBlueprint():
    return blp

@blp.fxroute(
    endpoint="",
    method="GET",
    description="Retrieve information about available log files.",
    resp_schemas={
        200: rkproto_applogs_RetrieveFilesResponse,
    })
@perm_required("System:System Logs")
async def get():
    rsp = await ApplogsIfx.send(RetrieveFiles(), RetrieveFilesResponse)
    respond(200, proto_to_dict(rsp))
