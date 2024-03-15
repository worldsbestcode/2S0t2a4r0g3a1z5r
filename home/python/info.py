import socket
import time

from typing import Dict

from rkweb.lilmodels.base import Model, field

from rkweb.auth import login_required
from rkweb.session import AuthSession
from rkweb.flaskutils import Blueprint, abort, respond
from rkweb.rkserver import ExcryptMsg, ServerConn

from dashboard import has_config_perm, get_features

# Blueprint
blp = Blueprint("info", "info", url_prefix="/dashboard/info", description="Get device information")
def InfoBlueprint():
    return blp

# GET /info
class DeviceInfo(Model):
    hostname: str = field(description="Hostname of the device")
    licenses: Dict[str, str] = field(description="Server licenses")

    version: str = field(description="Expanded application version")
    systemHash: str = field(description="System database hash")
    serial: str = field(description="Application server serial")
    product: str = field(description="Application product name")

    hsmVersion: str = field(description="HSM version")
    hsmHash: str = field(description="HSM state hash")
    hsmModel: str = field(description="HSM model")
    hsmSerial: str = field(description="HSM serial")

global data
data = None

global cache_time
cache_time = None

@blp.fxroute(
    endpoint="",
    method="GET",
    description="Get information about the device",
    resp_schemas={
        200: DeviceInfo,
    })
@login_required()
async def get():
    global data
    global cache_time
    # Cache results for 20 seconds
    if cache_time and cache_time < time.time() - 20:
        data = None

    if not data:
        data = {}
        data['hostname'] = socket.gethostname()
        data['licenses'] = await get_features()

        # Get info from server
        server = ServerConn()
        msg = ExcryptMsg("[AOECHO;]")
        msg.set_tag("EX", "1")
        msg.set_tag("JW", AuthSession.auth_token())
        rsp = await server.send_excrypt(msg)

        data['version'] = rsp.get_tag("EX")
        data['systemHash'] = rsp.get_tag("OI")
        data['serial'] = rsp.get_tag("SN")
        data['product'] = rsp.get_tag("PN")
        data['hsmVersion'] = rsp.get_tag("FW")
        data['hsmHash'] = rsp.get_tag("FH")
        data['hsmModel'] = rsp.get_tag("FM")
        data['hsmSerial'] = rsp.get_tag("FS")

        cache_time = time.time()

    # Give back to user
    respond(200, data)
