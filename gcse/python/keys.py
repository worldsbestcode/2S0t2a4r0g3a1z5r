from rkweb.auth import login_required
from rkweb.flaskutils import Blueprint, respond

from mm_rkproto.gcse.Keys import rkproto_gcse_PersonalKeyInfo
from mm_rkproto.gcse.Keys import rkproto_gcse_DeletePersonalKey
from mm_rkproto.gcse.Keys import rkproto_gcse_RotatePersonalKey
from mm_rkproto.gcse.Keys import rkproto_gcse_ExtendedPersonalKeyInfo

from rkproto.gcse.Keys_pb2 import RetrievePersonalKeys, RetrievePersonalKeysResponse
from rkproto.gcse.Keys_pb2 import DeletePersonalKey, RotatePersonalKey
from rkproto.gcse.Keys_pb2 import RetrievePersonalKey, ExtendedPersonalKeyInfo

from rkweb.lilmodels.base import Model, field
from rkweb.lilmodels.page import PagedRequestModel, PagedResponseModel
from rkweb.protoflask import serialize_pagination, args_to_proto, proto_to_dict

from gcseifx import GcseIfx

from marshmallow import fields

import json
from google.protobuf import json_format

def KeysBlueprintV1():
    blp = Blueprint("Google Keys", "keys", url_prefix="/keys", description="Manage Google CSE Keys")
    define_get_keys(blp)
    define_delete_key(blp)
    define_rotate_key(blp)
    define_get_key(blp)
    return blp

def define_get_keys(blp):
    class RetrieveKeysRequest(PagedRequestModel):
        service: str = field(description="Service to query")
        email: str = field(description="User to query")

    class RetrieveKeysResponse(PagedResponseModel):
        results: list = field(
            description="The page of results",
            marshmallow_field=fields.List(
                fields.Nested(rkproto_gcse_PersonalKeyInfo)
            )
        )

    @blp.fxroute(
        endpoint="",
        method="GET",
        description="Retrieve a chunk of personal keys for a user",
        schema=RetrieveKeysRequest,
        location='query',
        resp_schemas={
            200: RetrieveKeysResponse,
        })
    @login_required()
    async def getKeys(args):

        # Input
        page = int(args.get('page', 1))
        page_size = int(args.get('pageSize', 100))

        # To protobuf
        req = RetrievePersonalKeys()
        req.service_uuid = args['service']
        req.email = args['email']
        req.chunk = page - 1 if page > 0 else page
        req.chunk_size = page_size

        # Forward to microservice
        rsp = await GcseIfx.send(req, RetrievePersonalKeysResponse)

        # From protobuf
        data = serialize_pagination(rsp.pagination)
        rsp_dict = proto_to_dict(rsp)
        data['results'] = rsp_dict['keys'] if 'keys' in rsp_dict else []

        respond(200, data)

def define_get_key(blp):
    @blp.fxroute(
        endpoint="/<uuid>",
        method="GET",
        description="Retrieve a personal key",
        resp_schemas={
            200: rkproto_gcse_ExtendedPersonalKeyInfo,
        })
    @login_required()
    async def getKey(uuid):
        # To protobuf
        msg = RetrievePersonalKey()
        msg.key_uuid = uuid

        # Forward to microservice
        rsp = await GcseIfx.send(msg, ExtendedPersonalKeyInfo)

        # Convert to dictionary
        data = proto_to_dict(rsp)
        respond(200, data)

def define_delete_key(blp):
    @blp.fxroute(
        endpoint="",
        method="DELETE",
        description="Delete a personal key",
        schema=rkproto_gcse_DeletePersonalKey,
        )
    @login_required()
    async def deleteKey(req):
        # To protobuf
        msg = args_to_proto(req, DeletePersonalKey)

        # Forward to microservice
        await GcseIfx.send(msg, None)
        respond(200)

def define_rotate_key(blp):
    @blp.fxroute(
        endpoint="",
        method="POST",
        description="Rotate a personal key group",
        schema=rkproto_gcse_RotatePersonalKey,
        )
    @login_required()
    async def rotateKey(req):
        # To protobuf
        msg = args_to_proto(req, RotatePersonalKey)

        # Forward to microservice
        await GcseIfx.send(msg, None)
        respond(200)
