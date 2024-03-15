from rkweb.auth import perm_required
from rkweb.session import AuthSession
from rkweb.flaskutils import Blueprint, respond
from rkweb.protoflask import args_to_proto, proto_to_dict
from rkweb.lilmodels.base import Model, List, field

from mm_rkproto.cuserv.CustomService import rkproto_cuserv_CustomService
from mm_rkproto.cuserv.CustomService import rkproto_cuserv_CustomService_ADD
from mm_rkproto.cuserv.CustomService import rkproto_cuserv_CustomService_GET
from mm_rkproto.cuserv.CustomService import rkproto_cuserv_CustomService_MODIFY
from mm_rkproto.cuserv.CustomService import rkproto_cuserv_CustomService_Stub

from mm_rkproto.cuserv.DeployService import rkproto_cuserv_DeployService
from mm_rkproto.cuserv.DeployService import rkproto_cuserv_DeployServiceResponse

from mm_rkproto.cuserv.DestroyService import rkproto_cuserv_DestroyService
from mm_rkproto.cuserv.DestroyService import rkproto_cuserv_DestroyServiceResponse

from rkproto.mo.ObjectFilter_pb2 import ObjectFilter, FilterClause
from rkproto.cuserv.CustomService_pb2 import CustomService, CustomService_Stub
from rkproto.cuserv.DeployService_pb2 import DeployService, DeployServiceResponse
from rkproto.cuserv.DestroyService_pb2 import DestroyService, DestroyServiceResponse

# Deploy Parameters
from rkproto.cuserv.DeployClientAppParams_pb2 import *
from rkproto.cuserv.DeployGoogleEkmsParams_pb2 import *
from rkproto.cuserv.DeployGoogleCseParams_pb2 import *
from rkproto.cuserv.DeployPedInjectParams_pb2 import *

from rkproto.cuserv.RetrieveServiceCategories_pb2 import RetrieveServiceCategories, RetrieveServiceCategoriesResponse

from google.protobuf import json_format

from cuservifx import CuservIfx

import json

# Blueprint
blp = Blueprint("Deployed Services", "services", url_prefix="/services", description="Manage deployed services")
def DeployedServicesBlueprint():
    return blp

# CRUD operations
from rkweb.protocrud import ProtoCrud
ProtoCrud(
    name="deployed service",
    blp=blp,
    port=5055,
    proto_class=CustomService,
    proto_stub_class=CustomService_Stub,
    mmproto_get=rkproto_cuserv_CustomService_GET,
    mmproto_stub=rkproto_cuserv_CustomService_Stub,
    mmproto_add=None,
    mmproto_modify=rkproto_cuserv_CustomService_MODIFY,
    delete=False,
    perm_category="Custom Services",
    manage_perm="Manage")


# Deploy a service template
@blp.fxroute(
    endpoint="/deploy",
    method="POST",
    description="Deploy a service template",
    schema=rkproto_cuserv_DeployService,
    resp_schemas={
        200: rkproto_cuserv_DeployServiceResponse,
    })
@perm_required("Custom Services:Deploy")
async def deploy(req):
    # To protobuf
    msg = args_to_proto(req, DeployService)
    # Forward to microservice
    rsp = await CuservIfx.send(msg, DeployServiceResponse)
    # From protobuf
    data = proto_to_dict(rsp)
    # Will need to refresh token to get new service list
    AuthSession.dirty()
    # Respond
    respond(200, data)


# Destroy a service template
@blp.fxroute(
    endpoint="/<uuid>",
    method="DELETE",
    description="Tear down a service that was previously deployed",
    schema=rkproto_cuserv_DestroyService,
    resp_schemas={
        200: rkproto_cuserv_DestroyServiceResponse,
    })
@perm_required("Custom Services:Deploy")
async def deploy(req: dict, uuid: str):
    req['service_uuid'] = uuid
    # To protobuf
    msg = args_to_proto(req, DestroyService)
    # Forward to microservice
    rsp = await CuservIfx.send(msg, DestroyServiceResponse)
    # From protobuf
    data = proto_to_dict(rsp)
    # Respond
    respond(200, data)


# Retrieve categories
def define_get_categories(blp):
    class ServiceServiceCategories(Model):
        categories: List[str] = field(description="The categories")

    @blp.fxroute(
        endpoint="/categories",
        method="GET",
        description="Retrieve the list of all deployed categories",
        resp_schemas={
            200: ServiceServiceCategories,
        })
    @perm_required("Custom Services")
    async def getCategories():

        msg = RetrieveServiceCategories()
        rsp = await CuservIfx.send(msg, RetrieveServiceCategoriesResponse)

        data = {
            'categories': list(rsp.categories)
        }

        respond(200, data)
define_get_categories(blp)
