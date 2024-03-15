from rkweb.auth import login_required
from rkweb.flaskutils import Blueprint, respond
from rkweb.protoflask import proto_to_dict

from mm_rkproto.gcse.User import rkproto_gcse_User
from mm_rkproto.gcse.User import rkproto_gcse_User_ADD
from mm_rkproto.gcse.User import rkproto_gcse_User_GET
from mm_rkproto.gcse.User import rkproto_gcse_User_MODIFY
from mm_rkproto.gcse.User import rkproto_gcse_User_Stub
from mm_rkproto.gcse.LookupUser import rkproto_gcse_LookupUserResponse

from rkproto.gcse.User_pb2 import User, User_Stub
from rkproto.gcse.LookupUser_pb2 import LookupUser, LookupUserResponse

from manager import UserManager

from rkweb.lilmodels.base import Model, field
from rkweb.lilmodels.page import PagedRequestModel, PagedResponseModel
from rkweb.protoflask import serialize_filter_results, load_paging
from rkproto.mo.ObjectFilter_pb2 import ObjectFilter, FilterClause

from gcseifx import GcseIfx

from flask import request
from marshmallow import fields

import json
from google.protobuf import json_format

# Blueprint
def UsersBlueprintV1():
    blp = Blueprint("Google Users", "users", url_prefix="/users", description="Manage Google CSE Users")
    define_crud(blp)
    define_list(blp)
    define_lookup_user(blp)
    return blp

# CRUD operations
def define_crud(blp):
    from rkweb.protocrud import ProtoCrud
    ProtoCrud(
        name="CSE User",
        blp=blp,
        port=5080,
        proto_class=User,
        proto_stub_class=User_Stub,
        mmproto_get=rkproto_gcse_User_GET,
        mmproto_stub=None,
        mmproto_add=rkproto_gcse_User_ADD,
        mmproto_modify=rkproto_gcse_User_MODIFY,
        perm_category=None)

# Retrieve stubs by service
def define_list(blp):
    class UserStubsRequest(PagedRequestModel):
        service: str = field(description="The service UUID to query", required=False)

    class UserStubs(PagedResponseModel):
        results: list = field(
            description="The page of results",
            marshmallow_field=fields.List(
                fields.Nested(rkproto_gcse_User_Stub)
            )
        )

    @blp.fxroute(
        endpoint="/stubs",
        method="GET",
        description="Retrieve a page of Google CSE users by service",
        schema=UserStubsRequest,
        location='query',
        resp_schemas={
            200: UserStubs,
        })
    @login_required()
    async def getStubs(args):

        # Build filter
        obj_filter = ObjectFilter()
        obj_filter.object_type = "rkproto.gcse.User"
        obj_filter.sort_attribute = "name"
        obj_filter.stubs = True
        load_paging(args, obj_filter)

        # Filter by category
        if 'service' in args:
            uuid = args.get('service')
            clause = FilterClause()
            clause.match_type = FilterClause.MatchType.Equals
            clause.attribute = "service_uuid"
            clause.value = uuid
            obj_filter.query_params.clauses.append(clause)

        # Filter
        (pagination, objs) = await UserManager().filter(obj_filter)

        # Respond
        respond(200, serialize_filter_results(pagination, objs))

def define_lookup_user(blp):
    @blp.fxroute(
        endpoint="/lookup",
        method="GET",
        description="Lookup a CSE user by auth state",
        resp_schemas={
            200: rkproto_gcse_LookupUserResponse,
        })
    @login_required()
    async def lookupUser():
        # Forward to microservice
        msg = LookupUser()
        rsp = await GcseIfx.send(msg, LookupUserResponse)

        # Convert to dictionary
        data = proto_to_dict(rsp)
        respond(200, data)
