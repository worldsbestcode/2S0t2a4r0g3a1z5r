from rkweb.auth import login_required
from rkweb.flaskutils import Blueprint, respond
from rkweb.protoflask import proto_to_dict

from mm_rkproto.gekms.Key import rkproto_gekms_Key
from mm_rkproto.gekms.Key import rkproto_gekms_Key_ADD
from mm_rkproto.gekms.Key import rkproto_gekms_Key_GET
from mm_rkproto.gekms.Key import rkproto_gekms_Key_MODIFY
from mm_rkproto.gekms.Key import rkproto_gekms_Key_Stub

from mm_rkproto.gekms.CreateKey import rkproto_gekms_CreateKey
from mm_rkproto.gekms.CreateKey import rkproto_gekms_CreateKeyResponse

from rkproto.gekms.CreateKey_pb2 import CreateKey as fxCreateKey
from rkproto.gekms.CreateKey_pb2 import CreateKeyResponse as fxCreateKeyResponse

from rkproto.gekms.Key_pb2 import Key, Key_Stub

from manager import KeyManager
from gekmsifx import GekmsIfx

from typing import List
from rkweb.lilmodels.base import Model, field
from rkweb.lilmodels.page import PagedRequestModel, PagedResponseModel
from rkweb.protoflask import serialize_filter_results, load_paging, proto_to_dict
from rkproto.mo.ObjectFilter_pb2 import ObjectFilter, FilterClause

from flask import request
from marshmallow import fields

import json
from google.protobuf import json_format

# Blueprint
def KeysBlueprintV1():
    blp = Blueprint("Google Keys", "keys", url_prefix="/keys", description="Manage Google EKMS Keys")
    define_list(blp)
    define_get(blp)
    define_add(blp)
    define_patch(blp)
    define_justifications(blp)
    return blp

# Retrieve stubs by cryptospace
def define_list(blp):
    class KeyStubsRequest(PagedRequestModel):
        cryptoSpace: str = field(description="The CryptoSpace UUID to query", required=False)

    class KeyStubs(PagedResponseModel):
        results: list = field(
            description="The page of results",
            marshmallow_field=fields.List(
                fields.Nested(rkproto_gekms_Key_Stub)
            )
        )

    @blp.fxroute(
        endpoint="/stubs",
        method="GET",
        description="Retrieve a page of Google EKM keys by service",
        schema=KeyStubsRequest,
        location='query',
        resp_schemas={
            200: KeyStubs,
        })
    @login_required()
    async def getStubs(args):

        # Build filter
        obj_filter = ObjectFilter()
        obj_filter.object_type = "rkproto.gekms.Key"
        obj_filter.sort_attribute = "name"
        obj_filter.stubs = True
        load_paging(args, obj_filter)

        # Filter by category
        if 'cryptoSpace' in args:
            uuid = args.get('cryptoSpace')
            clause = FilterClause()
            clause.match_type = FilterClause.MatchType.Equals
            clause.attribute = "crypto_space_uuid"
            clause.value = uuid
            obj_filter.query_params.clauses.append(clause)

        # Filter
        (pagination, objs) = await KeyManager().filter(obj_filter)

        # Respond
        respond(200, serialize_filter_results(pagination, objs))

# Convert KAJ_UNAVAILABLE to front-end friendly string
def import_KAJ_UNAVAILABLE(data):
    print(data)
    jus = 'defaultJustifications' if 'defaultJustifications' in data else 'justifications'
    if jus in data:
        reasons = []
        for reason in data[jus]:
            if reason == 'No justification field is present':
                reasons.append('KAJ_UNAVAILABLE')
            elif reason == 'Unknown justification':
                reasons.append('KAJ_UNKNOWN')
            else:
                reasons.append(reason)
        data[jus] = reasons

def export_KAJ_UNAVAILABLE(data):
    jus = 'defaultJustifications' if 'defaultJustifications' in data else 'justifications'
    if jus in data:
        reasons = []
        for reason in data[jus]:
            if reason == 'KAJ_UNAVAILABLE':
                reasons.append('No justification field is present')
            elif reason == 'KAJ_UNKNOWN':
                reasons.append('Unknown justification')
            else:
                reasons.append(reason)
        data[jus] = reasons

# Retrieve key
def define_get(blp):
    @blp.fxroute(
        endpoint="/<uuid>",
        method="GET",
        description="Retrieve a Google EKM key",
        resp_schemas={
            200: rkproto_gekms_Key,
        })
    @login_required()
    async def getKey(uuid):

        # Filter
        obj = await KeyManager().select(uuid)

        # Convert to dictionary
        data = proto_to_dict(obj)
        export_KAJ_UNAVAILABLE(data)
        respond(200, data)

from mm_proto.access_reason import *
from mm_proto.resources import *
def define_add(blp):
    class CreateKeyRequest(Model):
        name: str = field(
            description="A convenient name for the key",
            required=False,
        )
        cryptoSpace: str = field(
            description="The CryptoSpace UUID",
        )
        algorithm: str = field(
            description="The algorithm for the key",
            marshmallow_field=google_cloud_ekms_v0_ExternalKeyAlgorithm(),
        )
        rotationPeriod: str = field(
            description="How often the key automatically rotates (Symmetric only)",
            required=False,
        )
        justifications: List[str] = field(
            description="The access justifications allowed for using the key (Symmetrc only)",
            marshmallow_field=fields.List(google_cloud_ekms_v0_AccessReasonContext_Reason()),
            required=False,
        )

    @blp.fxroute(
        endpoint="",
        method="POST",
        description="Add a new key to a Google EKM service",
        schema=CreateKeyRequest,
        resp_schemas={
            200: rkproto_gekms_CreateKeyResponse,
        })
    @login_required()
    async def createKey(req):
        # To protobuf
        wrapper = fxCreateKey()
        wrapper.name = req['name']
        wrapper.request_uri =  request.base_url
        wrapper.crypto_space = req['cryptoSpace']
        wrapper.gapi.algorithm = req['algorithm']
        if 'rotationPeriod' in req:
            wrapper.rotation_period = req['rotationPeriod']
        import_KAJ_UNAVAILABLE(req)
        if 'justifications' in req:
            for reason in req['justifications']:
                wrapper.justifications.append(reason)
        # Forward to microservice
        rspWrapper = await GekmsIfx.send(wrapper, fxCreateKeyResponse)
        # From protobuf
        data = proto_to_dict(rspWrapper)
        respond(200, data)

# Modify key
def define_patch(blp):
    class ModifyKeyRequest(Model):
        name: str = field(
            description="A convenient name for the key",
            required=False,
        )
        rotationPeriod: str = field(
            description="How often the key automatically rotates (Symmetric only)",
            required=False,
        )
        justifications: List[str] = field(
            description="The access justifications allowed for using the key (Symmetrc only)",
            marshmallow_field=fields.List(google_cloud_ekms_v0_AccessReasonContext_Reason()),
            required=False,
        )

    @blp.fxroute(
        endpoint="/<uuid>",
        method="PATCH",
        description="Modify a key in a Google EKM service",
        schema=ModifyKeyRequest,
        )
    @login_required()
    async def modifyKey(req, uuid):
        key = Key()
        key.obj_info.uuid = uuid
        field_mask = []
        if 'name' in req:
            key.obj_info.name= req['name']
            key.field_mask.paths.append('name')
            key.field_mask.paths.append('obj_info.name')
        if 'rotationPeriod' in req:
            key.rotation_period = req['rotationPeriod']
            key.field_mask.paths.append('rotation_period')
        import_KAJ_UNAVAILABLE(req)
        if 'justifications' in req:
            for reason in req['justifications']:
                key.justifications.append(reason)
            key.field_mask.paths.append('justifications')

        # Save
        await KeyManager().modify(key)

        # Respond
        respond(200)

# Initialize/cache a list of all possible justifications
from proto.access_reason_pb2 import *
justifications=[]
i = 0
while True:
    try:
        value = AccessReasonContext.Reason.Name(i)
        justifications.append(value)
    except:
        break
    i += 1

# Endpoint for front-end to dynamically retrieve justifications list
def define_justifications(blp):
    class JustificationsInfo(Model):
        justifications: List[str] = field(
            description="The access justifications allowed for using the key (Symmetrc only)",
            marshmallow_field=fields.List(google_cloud_ekms_v0_AccessReasonContext_Reason()),
            required=False,
        )

    @blp.fxroute(
        endpoint="/justifications",
        method="GET",
        description="Retrieve the list of possible justifications",
        resp_schemas={
            200: JustificationsInfo,
        })
    @login_required()
    async def serveJustice():
        data = {"justifications": justifications}
        respond(200, data)
