import json
from rkweb.ipc import IpcUtils
from rkweb.auth import login_required
from rkweb.session import AuthSession
from inject_session import InjectSession
from rkweb.flaskutils import Blueprint, respond, abort
from google.protobuf.json_format import MessageToDict
from mm_rkproto.dki.RetrieveSlots import rkproto_dki_RetrieveSlotsResponse, rkproto_dki_RetrieveSlots
from rkproto.dki.RetrieveSlots_pb2 import RetrieveSlotsResponse, RetrieveSlots

from flask import request

blp = Blueprint("slots", "slots", url_prefix="/slots", description="Query the usb slots")


def SlotsBlueprint():
    return blp


@blp.fxroute(
    endpoint="/query",
    method="GET",
    description="Retrieve the slots",
    schema=rkproto_dki_RetrieveSlots,
    location='query',
    resp_schemas={
        200: rkproto_dki_RetrieveSlotsResponse,
    })
@login_required()
async def getQuery(args):
    auth_token = AuthSession.auth_token()
    msg = RetrieveSlots()
    session_id = args.get('session', None)
    if session_id is None:
        print('session_id is required')
        abort(400, 'session_id is required')

    msg.session = session_id
    response = await IpcUtils.send(
        port=InjectSession.port,
        msg=msg,
        resp_type=RetrieveSlotsResponse,
        auth_token=auth_token
    )

    slots = []
    for slot in response.slots:
        extra_infos = []
        for extra_info in slot.extra_info:
            extra_infos.append(extra_info)

        json_slot = {
            'id': str(slot.id),
            'cardIndex': slot.card_index,
            'slotIndex': slot.port_index,
            'type': slot.type,
            'extraInfo': extra_infos
        }

        id = json_slot['id']
        slots.append(json_slot)

    data = {
        'slots': slots,

    }
    respond(200, data)
