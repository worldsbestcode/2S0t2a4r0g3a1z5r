import json
from flask import request
from rkweb.ipc import IpcUtils
from rkweb.auth import login_required
from rkweb.session import AuthSession
from inject_session import InjectSession
from rkweb.flaskutils import Blueprint, respond, abort
from google.protobuf.json_format import MessageToDict
from rkproto.dki.StartInjection_pb2 import StartInjection, StartInjectionResponse
from mm_rkproto.dki.StartInjection import rkproto_dki_StartInjectionResponse, rkproto_dki_StartInjection
from rkproto.dki.InjectionStatus_pb2 import InjectionStatus, InjectionStatusResponse
from mm_rkproto.dki.InjectionStatus import rkproto_dki_InjectionStatusResponse, rkproto_dki_InjectionStatus
from rkproto.dki.GetSerialNumber_pb2 import GetSerialNumber, GetSerialNumberResponse
from mm_rkproto.dki.GetSerialNumber import rkproto_dki_GetSerialNumberResponse, rkproto_dki_GetSerialNumber

#TODO(DR) - if the serial communction for PED device is incorrect it will take a very long time to timeout
# Find issue and fix in different ticket. For now increase the timeout
COMMAND_TIMEOUT = 100 * 1000  #1 minute.

blp = Blueprint('injection', "injection", url_prefix='/inject')


def InjectBlueprint():
    return blp


@blp.fxroute(
    endpoint='/start',
    method="POST",
    description="Start injection",
    schema=rkproto_dki_StartInjection,
    resp_schemas={
        200: rkproto_dki_StartInjectionResponse,
    })
@login_required()
async def start(req):

    session_id = req.get('session', None)
    if session_id is None:
        abort(400, 'session is required')

    slot_id = req.get('slotId', None)
    if slot_id is None:
        abort(400, 'slot_id is required')

    service_uuid = req.get('serviceUuid', None)
    if service_uuid is None:
        abort(400, 'service_uuid is required')

    serial_number = req.get('serialNumber', None)
    serial_num_entry_cancelled = req.get('serialNumEntryCancelled', False)

    auth_token = AuthSession.auth_token()
    request = StartInjection()
    request.session = session_id
    request.slot_id = int(slot_id)
    request.serial_num_entry_cancelled = serial_num_entry_cancelled
    request.service_uuid = service_uuid
    if serial_number is not None:
        request.serial_number = serial_number

    response = await IpcUtils.send(
        port=InjectSession.port,
        msg=request,
        resp_type=StartInjectionResponse,
        auth_token=auth_token
    )

    data = {
        'session': response.session,
    }
    respond(200, data)


@blp.fxroute(
    endpoint='/status',
    method="GET",
    description="Get Injection status",
    location='query',
    schema=rkproto_dki_InjectionStatus,
    resp_schemas={
        200: rkproto_dki_InjectionStatusResponse,
    })
@login_required()
async def status(req):
    session_id = req.get('session', None)
    if session_id is None:
        abort(400, "session is required")

    slot_id = req.get('slotId', None)
    if slot_id is None:
        abort(400, "slotId is required")

    auth_token = AuthSession.auth_token()
    msg = InjectionStatus()
    msg.session = session_id
    msg.slot_id = int(slot_id)

    response = await IpcUtils.send(
        port=InjectSession.port,
        msg=msg,
        resp_type=InjectionStatusResponse,
        auth_token=auth_token)

    response_dict = MessageToDict(response)
    messages = response_dict.get('messages', [])
    log_messages = response_dict.get('logMessages', []);

    data = {
        'status': response.status,
        'messages': messages,
        'logMessages': log_messages,
    }

    respond(200, data)


@blp.fxroute(
    endpoint='/serial',
    method="POST",
    description="Get Serial Number",
    schema=rkproto_dki_GetSerialNumber,
    resp_schemas={
        200: rkproto_dki_GetSerialNumberResponse
    })
@login_required()
async def serial(req):
    session_id = req.get('session', None)
    if session_id is None:
        abort(400, "session is required")

    slot_id = req.get('slotId', None)
    if slot_id is None:
        abort(400, "slotId is required")

    service_uuid = req.get('serviceUuid', None)
    if service_uuid is None:
        abort(400, 'service_uuid is required')

    auth_token = AuthSession.auth_token()
    print(auth_token)
    msg = GetSerialNumber()
    msg.session = session_id
    msg.slot_id = int(slot_id)
    msg.service_uuid = service_uuid

    response = await IpcUtils.send(
        port=InjectSession.port,
        msg=msg,
        resp_type=GetSerialNumberResponse,
        auth_token=auth_token,
        timeout=COMMAND_TIMEOUT)

    data = {
        'serial_number': response.serial_number,
        'display_serial_prompt': response.display_serial_prompt
    }

    respond(200, data)
