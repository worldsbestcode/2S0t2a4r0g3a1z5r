from rkweb.auth import login_required
from rkweb.flaskutils import Blueprint, respond

from mm_rkproto.gekms.CryptoSpace import rkproto_gekms_CryptoSpace
from mm_rkproto.gekms.CryptoSpace import rkproto_gekms_CryptoSpace_ADD
from mm_rkproto.gekms.CryptoSpace import rkproto_gekms_CryptoSpace_GET
from mm_rkproto.gekms.CryptoSpace import rkproto_gekms_CryptoSpace_MODIFY
from mm_rkproto.gekms.CryptoSpace import rkproto_gekms_CryptoSpace_Stub

from rkproto.gekms.CryptoSpace_pb2 import CryptoSpace, CryptoSpace_Stub

from manager import CryptoSpaceManager
from keys import import_KAJ_UNAVAILABLE, export_KAJ_UNAVAILABLE

from rkweb.lilmodels.base import Model, field
from rkweb.lilmodels.page import PagedRequestModel, PagedResponseModel
from rkweb.protoflask import serialize_filter_results, load_paging
from rkproto.mo.ObjectFilter_pb2 import ObjectFilter, FilterClause

from flask import request
from marshmallow import fields

# Blueprint
def CryptoSpacesBlueprintV1():
    blp = Blueprint("Google CryptoSpaces", "cryptospaces", url_prefix="/cryptospaces", description="Manage Google EKMS CryptoSpaces")
    define_crud(blp)
    define_list(blp)
    return blp

# CRUD operations
def define_crud(blp):
    from rkweb.protocrud import ProtoCrud
    ProtoCrud(
        name="Google cryptospace",
        blp=blp,
        port=5070,
        proto_class=CryptoSpace,
        proto_stub_class=CryptoSpace_Stub,
        mmproto_get=rkproto_gekms_CryptoSpace_GET,
        mmproto_stub=None,
        mmproto_add=rkproto_gekms_CryptoSpace_ADD,
        mmproto_modify=rkproto_gekms_CryptoSpace_MODIFY,
        perm_category=None,
        proto_preparse=import_KAJ_UNAVAILABLE,
        proto_postserialize=export_KAJ_UNAVAILABLE,
    )

# Retrieve stubs by service
def define_list(blp):
    class CryptoSpaceStubsRequest(PagedRequestModel):
        service: str = field(description="The service UUID to query", required=False)

    class CryptoSpaceStubs(PagedResponseModel):
        results: list = field(
            description="The page of results",
            marshmallow_field=fields.List(
                fields.Nested(rkproto_gekms_CryptoSpace_Stub)
            )
        )

    @blp.fxroute(
        endpoint="/stubs",
        method="GET",
        description="Retrieve a page of Google EKMS CryptoSpaces by service",
        schema=CryptoSpaceStubsRequest,
        location='query',
        resp_schemas={
            200: CryptoSpaceStubs,
        })
    @login_required()
    async def getStubs(args):

        # Build filter
        obj_filter = ObjectFilter()
        obj_filter.object_type = "rkproto.gekms.CryptoSpace"
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
        (pagination, objs) = await CryptoSpaceManager().filter(obj_filter)

        # Respond
        respond(200, serialize_filter_results(pagination, objs))
