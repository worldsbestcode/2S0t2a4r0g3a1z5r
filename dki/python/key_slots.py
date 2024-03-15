from google.protobuf.json_format import MessageToDict, Parse
from inject_session import InjectSession
from manager import KeySlotReferenceManager, ServiceManager
from marshmallow import fields
from mm_rkproto.dki.KeySlotReference import rkproto_dki_KeySlotReference
from mm_rkproto.dki.KeySlotReference import rkproto_dki_KeySlotReference_GET
from mm_rkproto.dki.KeySlotReference import rkproto_dki_KeySlotReference_MODIFY
from mm_rkproto.dki.KeySlotReference import rkproto_dki_KeySlotReference_Stub
from rkproto.dki.KeySlotReference_pb2 import KeySlotReference, KeySlotReference_Stub
from rkproto.cuserv.CustomService_pb2 import CustomServiceObject
from rkweb.auth import login_required
from rkweb.flaskutils import Blueprint, respond, abort
from rkweb.lilmodels.base import field
from rkweb.lilmodels.page import PagedRequestModel, PagedResponseModel
from rkweb.protocrud import ProtoCrud
import http
import json

blp = Blueprint('injection keys', "key slots", url_prefix='/keyslots')


def KeySlotsBlueprint():
    return blp


ProtoCrud(
    name="key slot references",
    blp=blp,
    port=InjectSession().port,
    proto_class=KeySlotReference,
    proto_stub_class=KeySlotReference_Stub,
    mmproto_get=rkproto_dki_KeySlotReference_GET,
    mmproto_stub=rkproto_dki_KeySlotReference_Stub,
    mmproto_add=None,
    mmproto_modify=rkproto_dki_KeySlotReference_MODIFY,
    perm_category="Custom Services",
    delete=False,
    manage_perm="Manage")


class KeySlotReferencesRequest(PagedRequestModel):
    uuids: list = field(
        description="the page of result",
        required=True
    )


class KeySlotReferencesResponse(PagedResponseModel):
    results: list = field(
        description="The page of result",
        marshmallow_field=fields.List(
            fields.Nested(rkproto_dki_KeySlotReference)
        )
    )


@blp.fxroute(
    endpoint='/refs',
    method="POST",
    schema=KeySlotReferencesRequest,
    description="Get the key slot references",
    resp_schemas={
        http.HTTPStatus.OK: KeySlotReferencesResponse
    })
@login_required()
async def get_key_refs(req):
    uuids = req.get('uuids', [])

    results = []
    for uuid in uuids:
        key_slot_ref = await KeySlotReferenceManager().select(uuid)
        results.append(MessageToDict(key_slot_ref, including_default_value_fields=True))
    respond(http.HTTPStatus.OK, {'results': results})


@blp.fxroute(
    endpoint="",
    method="POST",
    schema=rkproto_dki_KeySlotReference,
    description="Create new key slot reference")
@login_required()
async def add_key_slot(req: dict):

    service_uuid = req.get('serviceUuid', None)
    if not service_uuid:
        abort(http.HTTPStatus.BAD_REQUEST, 'missing param serviceUuid')

    name = req.get('name', None)
    if not name:
        abort(http.HTTPStatus.BAD_REQUEST, 'missing param name')

    slot = req.get('slot', 0)

    key_uuid = req.get('keyUuid', None)
    if not key_uuid:
        abort(http.HTTPStatus.BAD_REQUEST, 'missing param keyUuid')

    required = req.get('required', False)

    key_slot_ref = KeySlotReference()
    key_slot_ref.required = required
    key_slot_ref.slot = int(slot)
    key_slot_ref.key_uuid = key_uuid
    key_slot_ref.service_uuid = service_uuid
    key_slot_ref.obj_info.name = name

    key_options = req.get('options', {})
    if len(key_options) > 0:
        Parse(json.dumps(key_options), key_slot_ref.options)

    key_slot_uuid = await KeySlotReferenceManager().add(key_slot_ref)

    service_manager = ServiceManager()

    service = await service_manager.select(service_uuid)
    custom_service_object = CustomServiceObject()
    custom_service_object.associated_uuid = key_slot_uuid
    custom_service_object.new_object = True
    custom_service_object.purpose = "KeySlotReference"

    service.associated_objects.append(custom_service_object)

    await service_manager.modify(service)

    respond(http.HTTPStatus.OK)


@blp.fxroute(
    endpoint="/<uuid>",
    method="DELETE",
    description="Delete key slot references")
@login_required()
async def delete(uuid: str):
    key_slot_manager = KeySlotReferenceManager()
    service_manager = ServiceManager()

    key_slot_ref = await key_slot_manager.select(uuid)
    service = await service_manager.select(key_slot_ref.service_uuid)

    for index, associated_object in enumerate(service.associated_objects):
        if associated_object.associated_uuid == uuid:
            del service.associated_objects[index]

    await service_manager.modify(service)
    await key_slot_manager.remove(uuid)

    respond(http.HTTPStatus.OK)
