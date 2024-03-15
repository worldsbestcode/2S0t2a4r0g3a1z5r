from rkweb.lilmodels.base import Model, field

from rkweb.flaskutils import Blueprint, abort, respond
from rkweb.rkserver import ExcryptMsg, ServerConn

# Blueprint
blp = Blueprint("status", "status", url_prefix="/status", description="Get device status")
def StatusBlueprint():
    return blp

class StatusResponse(Model):
    version: str = field(description="Server application version")

global STATUS_version
STATUS_version = None

@blp.fxroute(
    endpoint="",
    method="GET",
    description="Get device status",
    resp_schemas={
        200: StatusResponse,
    })
async def get():

    # Initialize STATUS_version
    global STATUS_version
    if not STATUS_version:
        # Get info from server
        server = ServerConn()
        msg = ExcryptMsg("[AOECHO;]")
        rsp = await server.send_excrypt(msg)
        if not rsp.get_tag("BC"):
            abort(500, "Failed to contact status service")

        # Cache version which never changes
        STATUS_version = rsp.get_tag("BC")

    data = {
        'version': STATUS_version
    }

    # Give back to user
    respond(200, data)
