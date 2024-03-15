import json
from rkweb.ipc import IpcUtils
from rkweb.auth import login_required
from rkweb.session import AuthSession
from inject_session import InjectSession
from rkweb.flaskutils import Blueprint, respond
from rkweb.protoflask import proto_to_dict, args_to_proto
from rkproto.dki.KeyExchangeHosts_pb2 import GetHostsRequest, GetHostsResponse
from mm_rkproto.dki.KeyExchangeHosts import rkproto_dki_GetHostsResponse
from rkproto.dki.KeyExchangeHosts_pb2 import HostTranslateKeysRequest, HostTranslateKeysResponse
from mm_rkproto.dki.KeyExchangeHosts import rkproto_dki_HostTranslateKeysRequest, rkproto_dki_HostTranslateKeysResponse

blp = Blueprint('hosts', "hosts", url_prefix='/hosts')


def HostsBlueprint():
    return blp


@blp.fxroute(
    endpoint='/',
    method="GET",
    description="Start injection",
    resp_schemas={
        200: rkproto_dki_GetHostsResponse,
    })
@login_required()
async def getKeyExchangeHosts():
    auth_token = AuthSession.auth_token()
    response = await IpcUtils.send(
        port=InjectSession.port,
        msg=GetHostsRequest(),
        resp_type=GetHostsResponse,
        auth_token=auth_token)
    respond(200, proto_to_dict(response))


@blp.fxroute(
    endpoint='/translate',
    method="POST",
    description="translate key under host",
    schema=rkproto_dki_HostTranslateKeysRequest,
    resp_schemas={
        200: rkproto_dki_HostTranslateKeysResponse,
    })
@login_required()
async def translateUnderHost(req):
    auth_token = AuthSession.auth_token()
    msg = args_to_proto(req, HostTranslateKeysRequest);
    response = await IpcUtils.send(
        port=InjectSession.port,
        msg=msg,
        resp_type=HostTranslateKeysResponse,
        auth_token=auth_token)
    respond(200, proto_to_dict(response))
