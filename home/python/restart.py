from typing import List

from rkweb.lilmodels.base import Model, field

from rkweb.auth import login_required, perm_required
from rkweb.session import AuthSession
from rkweb.flaskutils import Blueprint, abort, respond
from rkweb.rkserver import ExcryptMsg, ServerConn

# Blueprint
blp = Blueprint("restart", "restart", url_prefix="/restart", description="Restart services")
def RestartBlueprint():
    return blp

def get_service_list():
    return [
        'VRRP',
        'middleware',
        'ntp',
        'rkmicro-auth',
        'rkmicro-fsmonitor',
        'rkmicro-cuserv',
        'rkmicro-cuservobject',
        'rkmicro-pedinject',
        'rkserver',
        'web server',
    ]

# GET /
class RestartActions(Model):
    reboot: bool = field(description="Restart the hardware server")
    restart: bool = field(description="Restart the server process")
    debug: bool = field(description="Restart the server process and dump debug information")

    services: List[str] = field(description="List of services that can be restarted")

@blp.fxroute(
    endpoint="/",
    method="GET",
    description="Get information about what restart actions can be performed",
    resp_schemas={
        200: RestartActions,
    })
@login_required()
@perm_required("Device:Reboot")
async def get():

    data = {
        'reboot': True,
        'restart': True,
        'debug': True,
        'services': get_service_list(),
    }

    respond(200, data)


# POST /reboot
@blp.fxroute(
    endpoint="/reboot",
    method="POST",
    description="Restart the hardware server")
@login_required()
@perm_required("Device:Reboot")
async def reboot():

    msg = ExcryptMsg("[AOSETT;]")
    msg.set_tag("OP", "server:reboot")
    msg.set_tag("JW", AuthSession.auth_token())

    server = ServerConn()
    rsp = await server.send_excrypt(msg)
    if rsp.get_tag("AN") != "Y":
        abort(500, "Failed to reboot: " + rsp.to_error())

    respond(200)


# POST /restart
@blp.fxroute(
    endpoint="/restart",
    method="POST",
    description="Restart the server process")
@login_required()
@perm_required("Device:Reboot")
async def restart():

    msg = ExcryptMsg("[AOSETT;]")
    msg.set_tag("OP", "server:restart")
    msg.set_tag("JW", AuthSession.auth_token())

    server = ServerConn()
    rsp = await server.send_excrypt(msg)
    if rsp.get_tag("AN") != "Y":
        abort(500, "Failed to restart server: " + rsp.to_error())

    respond(200)


# POST /debug
@blp.fxroute(
    endpoint="/debug",
    method="POST",
    description="Restart the server process and save debugging information")
@login_required()
@perm_required("Device:Reboot")
async def debug():

    msg = ExcryptMsg("[AOSETT;]")
    msg.set_tag("OP", "service:restart")
    msg.set_tag("SE", "server")
    msg.set_tag("JW", AuthSession.auth_token())

    server = ServerConn()
    rsp = await server.send_excrypt(msg)
    if rsp.get_tag("AN") != "Y":
        abort(500, "Failed to debug restart server: " + rsp.to_error())

    respond(200)


# POST /service/%s
@blp.fxroute(
    endpoint="/service/<service>",
    method="POST",
    location="query",
    description="Restart a service process")
@login_required()
@perm_required("Device:Reboot")
async def service_restart(service):

    if not service in get_service_list():
        abort(400, "Invalid service")

    msg = ExcryptMsg("[AOSETT;]")
    msg.set_tag("OP", "service:restart")
    msg.set_tag("SE", service)
    msg.set_tag("JW", AuthSession.auth_token())

    server = ServerConn()
    rsp = await server.send_excrypt(msg)
    if rsp.get_tag("AN") != "Y":
        abort(500, "Failed to debug restart service: " + rsp.to_error())

    respond(200)

