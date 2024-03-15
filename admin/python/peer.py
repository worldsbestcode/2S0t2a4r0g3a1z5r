from rkweb.auth import perm_required
from rkweb.session import AuthSession
from rkweb.flaskutils import Blueprint, abort, respond
from rkweb.rkserver import ExcryptMsg, ServerConn

from mm_rkproto.admin.PeerCluster import rkproto_admin_PeersList

import json

# Blueprint
def PeerBlueprintV1():
    blp = Blueprint("Peers", "peers", url_prefix="/peers", description="Peer clusters")
    define_get(blp)
    define_put(blp)
    return blp

def define_get(blp):
    @blp.fxroute(
        endpoint="",
        method="GET",
        description="Get all peer IPs",
        resp_schemas={
            200: rkproto_admin_PeersList,
        })
    @perm_required("System:Administration")
    async def getPeers():
        msg = ExcryptMsg("[AOGDPE;OPlist;]")
        msg.set_tag("JW", AuthSession.auth_token())
        rsp = await ServerConn().send_excrypt(msg)

        peers = []
        if rsp.get_tag("IP"):
            ips = rsp.get_tag("IP").split(',')
            ports = rsp.get_tag("PO").split(',')
            peers = [{'ip': ip, 'port': int(port)} for ip, port in zip(ips, ports)]

        respond(200, {'peers': peers})

def define_put(blp):
    @blp.fxroute(
        endpoint="",
        method="PUT",
        description="Set peers list",
        schema=rkproto_admin_PeersList)
    @perm_required("System:Administration")
    async def setPeers(req):
        msg = ExcryptMsg("[AOGDPE;OPlist;]")
        msg.set_tag("JW", AuthSession.auth_token())
        rsp = await ServerConn().send_excrypt(msg)

        # Get current peers
        peers = set()
        if rsp.get_tag("IP"):
            peers.update(rsp.get_tag("IP").split(','))

        # Remove peers
        for ip in peers.difference(peer['ip'] for peer in req['peers']):
            msg = ExcryptMsg("[AOGDPE;OPdelete;]")
            msg.set_tag("IP", ip)

            msg.set_tag("JW", AuthSession.auth_token())
            rsp = await ServerConn().send_excrypt(msg)
            if rsp.get_tag("AN") != "Y":
                abort(500, "Failed to remove peer '{}': {}".format(ip, rsp.to_error()))

        # Set new peers
        for peer in req['peers']:
            # Prune empty entries
            if len(peer['ip']) == 0:
                continue

            msg = ExcryptMsg("[AOGDPE;OPadd;FE1;]")
            msg.set_tag("IP", peer['ip'])
            msg.set_tag("PO", peer['port'])

            msg.set_tag("JW", AuthSession.auth_token())
            rsp = await ServerConn().send_excrypt(msg)
            if rsp.get_tag("AN") != "Y":
                abort(500, "Failed to add peer '{}': {}".format(ip, rsp.to_error()))

        respond(200)
