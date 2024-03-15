from rkweb.auth import perm_required
from rkweb.flaskutils import Blueprint, respond
from rkweb.protoflask import args_to_proto, proto_to_dict

from mm_rkproto.admin.GetMajorKeys import rkproto_admin_GetMajorKeysResponse
from mm_rkproto.admin.LoadMajorKey import rkproto_admin_LoadMajorKeyResponse
from mm_rkproto.admin.LoadMajorKey import rkproto_admin_LoadMajorKeyNextCard
from mm_rkproto.admin.LoadMajorKey import rkproto_admin_LoadMajorKeySmartCards
from mm_rkproto.admin.LoadMajorKey import rkproto_admin_FragmentMajorKeyNextCard
from mm_rkproto.admin.LoadMajorKey import rkproto_admin_RandomizeMajorKey
from mm_rkproto.admin.LoadMajorKeyComponents import rkproto_admin_LoadMajorKeyComponentsResponse
from mm_rkproto.admin.LoadMajorKeyComponents import rkproto_admin_LoadMajorKeyNextComponent
from mm_rkproto.admin.LoadMajorKeyComponents import rkproto_admin_LoadMajorKeyComponents

from rkproto.admin.GetMajorKeys_pb2 import GetMajorKeys, GetMajorKeysResponse
from rkproto.admin.LoadMajorKey_pb2 import RandomizeMajorKey, FragmentMajorKeyNextCard
from rkproto.admin.LoadMajorKey_pb2 import LoadMajorKeySmartCards, LoadMajorKeyNextCard
from rkproto.admin.LoadMajorKey_pb2 import LoadMajorKeyResponse
from rkproto.admin.LoadMajorKeyComponents_pb2 import LoadMajorKeyComponents, LoadMajorKeyNextComponent
from rkproto.admin.LoadMajorKeyComponents_pb2 import LoadMajorKeyComponentsResponse

from adminifx import AdminIfx

import json
from google.protobuf import json_format

# Blueprint
def MajorKeysBlueprintV1():
    blp = Blueprint("Major Keys", "majorkeys", url_prefix="/majorkeys", description="Get/Load Major Keys")
    define_get(blp)
    define_randomize(blp)
    define_get_next_fragment(blp)
    define_load_fragments(blp)
    define_load_next_card(blp)
    define_load_components(blp)
    define_load_next_component(blp)
    return blp

def define_get(blp):
    @blp.fxroute(
        endpoint="",
        method="GET",
        description="Get major key lengths and checksums",
        resp_schemas={
            200: rkproto_admin_GetMajorKeysResponse,
        })
    @perm_required("System:Administration")
    async def getMajorKeys():
        # Forward to microservice
        msg = GetMajorKeys()
        rsp = await AdminIfx.send(msg, GetMajorKeysResponse)

        # Convert to dictionary
        data = proto_to_dict(rsp)
        respond(200, data)

def define_randomize(blp):
    @blp.fxroute(
        endpoint="/random",
        method="POST",
        description="Randomize the specified major key",
        schema=rkproto_admin_RandomizeMajorKey,
        resp_schemas={
            200: rkproto_admin_LoadMajorKeyResponse,
        })
    @perm_required("System:Administration")
    async def randomizeMajorKey(req):
        # To protobuf
        msg = args_to_proto(req, RandomizeMajorKey)

        # Forward to microservice
        rsp = await AdminIfx().send(msg, LoadMajorKeyResponse)

        # Convert to dictionary
        data = proto_to_dict(rsp)
        respond(200, data)

def define_get_next_fragment(blp):
    @blp.fxroute(
        endpoint="/random/next",
        method="GET",
        description="Save the next major key fragment",
        schema=rkproto_admin_FragmentMajorKeyNextCard,
        location='query',
        resp_schemas={
            200: rkproto_admin_LoadMajorKeyResponse,
        })
    @perm_required("System:Administration")
    async def getNextFragment(req):
        # To protobuf
        msg = args_to_proto(req, FragmentMajorKeyNextCard)

        # Forward to microservice
        rsp = await AdminIfx().send(msg, LoadMajorKeyResponse)

        # Convert to dictionary
        data = proto_to_dict(rsp)
        respond(200, data)

def define_load_fragments(blp):
    @blp.fxroute(
        endpoint="/fragments",
        method="POST",
        description="Initialize major key load from fragments",
        schema=rkproto_admin_LoadMajorKeySmartCards,
        resp_schemas={
            200: rkproto_admin_LoadMajorKeyResponse,
        })
    @perm_required("System:Administration")
    async def loadFragments(req):
        # To protobuf
        msg = args_to_proto(req, LoadMajorKeySmartCards)

        # Forward to microservice
        rsp = await AdminIfx().send(msg, LoadMajorKeyResponse)

        # Convert to dictionary
        data = proto_to_dict(rsp)
        respond(200, data)

def define_load_next_card(blp):
    @blp.fxroute(
        endpoint="/fragments/next",
        method="POST",
        description="Load the next major key fragment",
        schema=rkproto_admin_LoadMajorKeyNextCard,
        resp_schemas={
            200: rkproto_admin_LoadMajorKeyResponse,
        })
    @perm_required("System:Administration")
    async def loadNextCard(req):
        # To protobuf
        msg = args_to_proto(req, LoadMajorKeyNextCard)

        # Forward to microservice
        rsp = await AdminIfx().send(msg, LoadMajorKeyResponse)

        # Convert to dictionary
        data = proto_to_dict(rsp)
        respond(200, data)

def define_load_components(blp):
    @blp.fxroute(
        endpoint="/components",
        method="POST",
        description="Initialize major key load from components",
        schema=rkproto_admin_LoadMajorKeyComponents,
        resp_schemas={
            200: rkproto_admin_LoadMajorKeyComponentsResponse,
        })
    @perm_required("System:Administration")
    async def loadComponents(req):
        # To protobuf
        msg = args_to_proto(req, LoadMajorKeyComponents)

        # Forward to microservice
        rsp = await AdminIfx().send(msg, LoadMajorKeyComponentsResponse)

        # Convert to dictionary
        data = proto_to_dict(rsp)
        respond(200, data)

def define_load_next_component(blp):
    @blp.fxroute(
        endpoint="/components/next",
        method="POST",
        description="Load the next major key component",
        schema=rkproto_admin_LoadMajorKeyNextComponent,
        resp_schemas={
            200: rkproto_admin_LoadMajorKeyComponentsResponse,
        })
    @perm_required("System:Administration")
    async def loadNextComponent(req):
        # To protobuf
        msg = args_to_proto(req, LoadMajorKeyNextComponent)

        # Forward to microservice
        rsp = await AdminIfx().send(msg, LoadMajorKeyComponentsResponse)

        # Convert to dictionary
        data = proto_to_dict(rsp)
        respond(200, data)
