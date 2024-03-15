# @file      device.py
# @author    Dante Ruiz (druiz@futurex.com)
#
# @section LICENSE
#
# This program is the property of Futurex, LP.
#
# No disclosure, reproduction, or use of any part thereof may be made without
# express written permission of Futurex, LP.
#
# Copyright by:  Futurex, LP. 2023
from rkweb.ipc import IpcUtils
from rkweb.auth import login_required
from rkweb.session import AuthSession
from rkweb.flaskutils import Blueprint, abort, respond
from rkweb.protoflask import args_to_proto, proto_to_dict

from rkproto.dki.DeviceGroup_pb2 import UpdateDeviceGroup, DeviceGroupInfo, DeviceGroupInfoResponse
from rkproto.dki.KeySlotReference_pb2 import KeySlotReference
from mm_rkproto.dki.DeviceGroup import rkproto_dki_UpdateDeviceGroup, rkproto_dki_DeviceGroupInfoResponse
from google.protobuf.json_format import Parse, MessageToDict, MessageToJson
from inject_session import InjectSession
from google.protobuf import json_format
import http
import json

blp = Blueprint("device", "device", url_prefix="/device",
                description="Manager device group")


def DeviceBlueprint():
    return blp


@blp.fxroute(
    endpoint="/<uuid>",
    method="PATCH",
    description="Update Device Group.",
    schema=rkproto_dki_UpdateDeviceGroup)
@login_required()
async def update(data: dict, uuid: str):

    data['deviceGroupUuid'] = uuid
    update_device_group = args_to_proto(data, UpdateDeviceGroup)

    await IpcUtils.send(
        port=InjectSession.port,
        msg=update_device_group,
        auth_token=AuthSession.auth_token()
    )
    respond(200)

@blp.fxroute(
    endpoint="/<uuid>",
    method="GET",
    description="Get DeviceGroup Info",
    resp_schemas={
        http.HTTPStatus.OK: rkproto_dki_DeviceGroupInfoResponse
    })
@login_required()
async def get(uuid: str):
    msg = DeviceGroupInfo()
    msg.device_group_uuid = uuid

    auth_token = AuthSession.auth_token()
    response = await IpcUtils.send(
        port=InjectSession.port,
        msg=msg,
        resp_type=DeviceGroupInfoResponse,
        auth_token=auth_token
    )

    data = proto_to_dict(response)
    respond(http.HTTPStatus.OK, data)
