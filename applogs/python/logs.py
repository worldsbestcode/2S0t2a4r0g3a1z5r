from rkweb.auth import perm_required
from rkweb.flaskutils import Blueprint, respond
from rkweb.protoflask import args_to_proto, proto_to_dict

from rkproto.applogs.RetrieveLogs_pb2 import RetrieveLogs, RetrieveLogsResponse
from mm_rkproto.applogs.RetrieveLogs import rkproto_applogs_RetrieveLogs, rkproto_applogs_RetrieveLogsResponse

from applogsifx import ApplogsIfx

# Blueprint
blp = Blueprint("View Logs", "logs", url_prefix="/logs", description="View Application Logs")
def LogsBlueprint():
    return blp

@blp.fxroute(
    endpoint="",
    method="GET",
    description="Retrieve a page of logs.",
    schema=rkproto_applogs_RetrieveLogs,
    location="query",
    resp_schemas={
        200: rkproto_applogs_RetrieveLogsResponse,
    })
@perm_required("System:System Logs")
async def get(args):
    # Ask microservice
    rsp = await ApplogsIfx.send(args_to_proto(args, RetrieveLogs), RetrieveLogsResponse)

    # Respond
    respond(200, proto_to_dict(rsp))
