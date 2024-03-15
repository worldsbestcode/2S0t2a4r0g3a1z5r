import http
from rkweb.ipc import IpcUtils
from rkweb.auth import login_required
from rkweb.session import AuthSession
from inject_session import InjectSession
from rkweb.flaskutils import Blueprint, abort, respond
from google.protobuf.json_format import MessageToDict, Parse, MessageToJson
from rkproto.dki.QueryKeys_pb2 import QueryKeys, QueryKeysResponse
from rkproto.cuserv.InjectDevices_pb2 import KeyTypeInfo
from mm_rkproto.dki.QueryKeys import rkproto_dki_QueryKeysResponse, rkproto_dki_QueryKeys
from mm_rkproto.dki.DeviceKey import rkproto_dki_DeviceKey
import json

blp = Blueprint('service keys', "keys", url_prefix='/keys/')


def KeysBlueprint():
    return blp

@blp.fxroute(
    endpoint="/<uuid>",
    method="GET",
    description="Get DeviceGroup Info",
    resp_schemas={
        http.HTTPStatus.OK: rkproto_dki_DeviceKey
    })
@login_required()
async def get(uuid: str):
    msg = QueryKeys()
    msg.key_uuid = uuid

    auth_token = AuthSession.auth_token()
    response = await IpcUtils.send(
        port=InjectSession.port,
        msg=msg,
        resp_type=QueryKeysResponse,
        auth_token=auth_token
    )

    if len(response.keys) == 0:
        abort(http.HTTPStatus.BAD_REQUEST, f"Failed to query key: {uuid}.")

    else:
        key = response.keys[0]
        data = json.loads(MessageToJson(key, including_default_value_fields=True))
        respond(http.HTTPStatus.OK, data)

@blp.fxroute(
    endpoint='/query',
    method="POST",
    description="Get device group keys",
    schema=rkproto_dki_QueryKeys,
    resp_schemas={
        http.HTTPStatus.OK: rkproto_dki_QueryKeysResponse,
    })
@login_required()
async def queryKeys(req: dict):
    msg = QueryKeys()
    key_uuid = req.get('keyUuid', None)
    if key_uuid:
        msg.key_uuid = key_uuid

    restricted_keys = req.get('restrictedKeys', [])

    for restricted_key in restricted_keys:
        key_type_info = KeyTypeInfo()
        Parse(json.dumps(restricted_key), key_type_info)
        msg.restricted_keys.append(key_type_info)

    auth_token = AuthSession.auth_token()
    response = await IpcUtils.send(
        port=InjectSession.port,
        msg=msg,
        resp_type=QueryKeysResponse,
        auth_token=auth_token)

    respond(http.HTTPStatus.OK, MessageToDict(response))
