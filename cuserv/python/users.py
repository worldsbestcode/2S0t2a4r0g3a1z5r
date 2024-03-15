from rkweb.lilmodels.base import Model, List, field
from rkweb.lilmodels.page import PagedRequestModel, PagedResponseModel

from rkweb.auth import perm_required
from rkweb.flaskutils import Blueprint, respond
from rkweb.protoflask import serialize_pagination, proto_to_dict

from flask import request
from marshmallow import fields

from cuservifx import CuservIfx

from rkproto.cuserv.RetrieveIdentities_pb2 import RetrieveIdentities, RetrieveIdentitiesResponse as pbRIR

from mm_rkproto.cuserv.RetrieveAuthMechanisms import rkproto_cuserv_AuthMechInfo
from rkproto.cuserv.RetrieveAuthMechanisms_pb2 import RetrieveAuthMechs, RetrieveAuthMechsResponse as pbRAM

# Blueprint
def UsersBlueprintV1():
    blp = Blueprint("User information", "users", url_prefix="/users", description="Retrieve information about identities and roles")
    define_retrieve_identities(blp)
    define_retrieve_authmechs(blp)
    return blp


# Retrieve identities
def define_retrieve_identities(blp):
    class RetrieveIdentitiesRequest(PagedRequestModel):
        ...

    class Identity(Model):
        name: str = field(description="Identity name")
        uuid: str = field(description="UUID for identity")

    class RetrieveIdentitiesResponse(PagedResponseModel):
        identities: list = field(
            description="The page of results",
            marshmallow_field=fields.List(
                fields.Nested(Identity.schema)
            )
        )

    @blp.fxroute(
        endpoint="/identities",
        method="GET",
        description="Retrieve the assignable identities",
        schema=RetrieveIdentitiesRequest,
        location='query',
        resp_schemas={
            200: RetrieveIdentitiesResponse,
        })
    @perm_required("Custom Services:Deploy")
    async def getUsers(args):

        # Input
        page = int(args.get('page', 1))
        page_size = int(args.get('pageSize', 100))

        # Send protobuf
        msg = RetrieveIdentities()
        msg.chunk = page - 1 if page > 0 else page
        msg.chunk_size = page_size
        rsp = await CuservIfx.send(msg, pbRIR)

        # Output
        data = serialize_pagination(rsp.pagination)
        rsp_dict = proto_to_dict(rsp)
        data['identities'] = rsp_dict['identities']

        respond(200, data)


# Retrieve auth mechanisms
def define_retrieve_authmechs(blp):
    class RetrieveAuthMechsRequest(PagedRequestModel):
        ...

    class RetrieveAuthMechsResponse(PagedResponseModel):
        results: list = field(
            description="The page of results",
            marshmallow_field=fields.List(
                fields.Nested(rkproto_cuserv_AuthMechInfo)
            )
        )

    @blp.fxroute(
        endpoint="/authmechs",
        method="GET",
        description="Retrieve the assignable auth mechanisms",
        schema=RetrieveAuthMechsRequest,
        location='query',
        resp_schemas={
            200: RetrieveAuthMechsResponse,
        })
    @perm_required("Custom Services:Deploy")
    async def getAuthMechs(args):

        # Input
        page = int(args.get('page', 1))
        page_size = int(args.get('page_size', 100))

        # Send protobuf
        msg = RetrieveAuthMechs()
        msg.chunk = page - 1 if page > 0 else page
        msg.chunk_size = page_size
        rsp = await CuservIfx.send(msg, pbRAM)

        # Output
        data = serialize_pagination(rsp.pagination)
        rsp_dict = proto_to_dict(rsp)
        for entry in rsp_dict['authMechs']:
            if not 'authType' in entry:
                entry['authType'] = 'None'
        data['results'] = rsp_dict['authMechs']

        respond(200, data)
