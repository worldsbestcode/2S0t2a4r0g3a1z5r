from urllib.parse import urlsplit
from rkweb.config import WebConfig
from rkweb.lilmodels.base import Model, List, field
from rkweb.lilmodels.page import PagedRequestModel, PagedResponseModel

from rkweb.auth import perm_required
from rkweb.flaskutils import Blueprint, respond, abort
from rkweb.protoflask import serialize_filter_results, load_paging, args_to_proto, proto_to_dict, serialize_pagination

from flask import request
from marshmallow import fields

from rkproto.mo.ObjectFilter_pb2 import ObjectFilter, FilterClause

# Marshmallow
from mm_rkproto.cuserv.ClientAppCrud import rkproto_cuserv_NewClientAppEndpoint
from mm_rkproto.cuserv.ClientAppCrud import rkproto_cuserv_NewClientAppEndpointResponse
from mm_rkproto.cuserv.ClientAppCrud import rkproto_cuserv_RenewClientAppEndpointResponse
from mm_rkproto.cuserv.ClientAppEndpoint import rkproto_cuserv_ClientAppEndpoint_GET
from mm_rkproto.cuserv.ClientAppEndpoint import rkproto_cuserv_ClientAppEndpoint_Stub
from mm_rkproto.cuserv.ClientAppEndpoint import rkproto_cuserv_GetClientAppPlatforms
from mm_rkproto.cuserv.ClientAppEndpoint import rkproto_cuserv_GetClientAppPlatformsResponse
from mm_rkproto.cuserv.ClientAppKeys import rkproto_cuserv_ClientAppKey

# Protobufs
from rkproto.cuserv.ClientAppEndpoint_pb2 import ClientAppEndpoint
from rkproto.cuserv.ClientAppEndpoint_pb2 import ClientAppEndpoint_Stub
from rkproto.cuserv.ClientAppEndpoint_pb2 import GetClientAppPlatforms
from rkproto.cuserv.ClientAppEndpoint_pb2 import GetClientAppPlatformsResponse
from rkproto.cuserv.ClientAppCrud_pb2 import NewClientAppEndpoint
from rkproto.cuserv.ClientAppCrud_pb2 import NewClientAppEndpointResponse
from rkproto.cuserv.ClientAppCrud_pb2 import RenewClientAppEndpoint
from rkproto.cuserv.ClientAppCrud_pb2 import RenewClientAppEndpointResponse
from rkproto.cuserv.ClientAppCrud_pb2 import ExpireClientAppCredential
from rkproto.cuserv.ClientAppCrud_pb2 import RemoveClientAppEndpoint
from rkproto.cuserv.ClientAppKeys_pb2 import RetrieveClientAppKeys
from rkproto.cuserv.ClientAppKeys_pb2 import RetrieveClientAppKeysResponse

from manager import ClientAppEndpointManager
from cuservifx import CuservIfx

# Blueprint
def ClientAppBlueprintV1():
    blp = Blueprint(
        "Client Application Deployments",
        "clientapp",
        url_prefix="/clientapp",
        description="Manage client application deployments",
    )
    define_endpoint_crud(blp)
    define_get_endpoints(blp)
    define_get_addresses(blp)
    define_new_endpoint(blp)
    define_renew_endpoint(blp)
    define_expire_endpoint_credential(blp)
    define_remove_endpoint(blp)
    define_get_keys(blp)
    define_get_platforms(blp)
    return blp

# CRUD operations
def define_endpoint_crud(blp):
    from rkweb.protocrud import ProtoCrud
    ProtoCrud(
        prefix="/endpoint",
        name="client application endpoint",
        blp=blp,
        port=5055,
        proto_class=ClientAppEndpoint,
        proto_stub_class=ClientAppEndpoint_Stub,
        mmproto_get=rkproto_cuserv_ClientAppEndpoint_GET,
        mmproto_stub=None,
        mmproto_add=None,
        mmproto_modify=None,
        perm_category=None,
        manage_perm=None,
        delete=False)

def define_get_endpoints(blp):
    class EndpointStubsRequest(PagedRequestModel):
        service: str = field(description="The service", required=False)

    class EndpointStubs(PagedResponseModel):
        results: list = field(
            description="The page of results",
            marshmallow_field=fields.List(
                fields.Nested(rkproto_cuserv_ClientAppEndpoint_Stub)
            )
        )
    @blp.fxroute(
        endpoint="/endpoint/stubs",
        method="GET",
        description="Retrieve endpoint stubs for a service",
        schema=EndpointStubsRequest,
        location='query',
        resp_schemas={
            200: EndpointStubs,
        })
    async def getStubs(args):
        # Build filter
        obj_filter = ObjectFilter()
        obj_filter.object_type = "rkproto.cuserv.ClientAppEndpoint"
        obj_filter.sort_attribute = "name"
        obj_filter.stubs = True
        load_paging(args, obj_filter)

        # Filter by category
        if 'service' in args:
            svc = args.get('service')
            clause = FilterClause()
            clause.match_type = FilterClause.MatchType.Equals
            clause.attribute = "service_uuid"
            clause.value = svc
            obj_filter.query_params.clauses.append(clause)

        # Filter
        (pagination, objs) = await ClientAppEndpointManager().filter(obj_filter)

        # Respond
        respond(200, serialize_filter_results(pagination, objs))

def define_new_endpoint(blp):
    @blp.fxroute(
        endpoint="/endpoint",
        method="POST",
        description="Create a new endpoint",
        schema=rkproto_cuserv_NewClientAppEndpoint,
        resp_schemas={
            200: rkproto_cuserv_NewClientAppEndpointResponse,
        })
    async def newEndpoint(args):
        req = args_to_proto(args, NewClientAppEndpoint)
        rsp = await CuservIfx.send(req, NewClientAppEndpointResponse)
        data = proto_to_dict(rsp)
        respond(200, data)

def define_renew_endpoint(blp):
    class RenewEndpoint(Model):
        expireExisting: bool = field(description="If the previous credential should be expired")

    @blp.fxroute(
        endpoint="/endpoint/renew/<uuid>",
        method="POST",
        description="Renew credentials for an endpoint",
        schema=RenewEndpoint,
        resp_schemas={
            200: rkproto_cuserv_RenewClientAppEndpointResponse,
        })
    async def renewEndpoint(args, uuid):
        req = RenewClientAppEndpoint()
        req.endpoint_uuid = uuid
        req.expire_existing = args['expireExisting']
        rsp = await CuservIfx.send(req, RenewClientAppEndpointResponse)
        data = proto_to_dict(rsp)
        respond(200, data)

def define_expire_endpoint_credential(blp):
    @blp.fxroute(
        endpoint="/endpoint/<endpoint>/<credential>",
        method="DELETE",
        description="Renew credentials for an endpoint",
        )
    async def expireEndpoint(endpoint, credential):
        req = ExpireClientAppCredential()
        req.endpoint_uuid = endpoint
        req.identity_uuid = credential
        await CuservIfx.send(req)
        respond(200)

def define_remove_endpoint(blp):
    @blp.fxroute(
        endpoint="/endpoint/<endpoint>",
        method="DELETE",
        description="Remove deployed endpoint",
        )
    async def expireEndpoint(endpoint):
        req = RemoveClientAppEndpoint()
        req.endpoint_uuid = endpoint
        await CuservIfx.send(req)
        respond(200)

def define_get_keys(blp):
    class RetrieveKeysRequest(PagedRequestModel):
        service: str = field(description="Service to query")

    class RetrieveKeysResponse(PagedResponseModel):
        results: list = field(
            description="The page of results",
            marshmallow_field=fields.List(
                fields.Nested(rkproto_cuserv_ClientAppKey)
            )
        )
    @blp.fxroute(
        endpoint="/keys",
        method="GET",
        description="Retrieve key objects created for a service",
        schema=RetrieveKeysRequest,
        location='query',
        resp_schemas={
            200: RetrieveKeysResponse,
        })
    async def getKeys(args):

        # Input
        page = int(args.get('page', 1))
        page_size = int(args.get('pageSize', 100))

        # Send protobuf
        msg = RetrieveClientAppKeys()
        msg.service_uuid = args['service']
        msg.chunk = page - 1 if page > 0 else page
        msg.chunk_size = page_size
        rsp = await CuservIfx.send(msg, RetrieveClientAppKeysResponse)

        # Output
        data = serialize_pagination(rsp.pagination)
        rsp_dict = proto_to_dict(rsp)
        data['results'] = rsp_dict['keys'] if 'keys' in rsp_dict else []
        respond(200, data)

# TODO: This should be configured on the back-end
#       As a mapping of service type to possible dest+port combos
def define_get_addresses(blp):
    class DeviceAddresses(Model):
        addresses: List[str] = field(description="The likely device addresses")

    @blp.fxroute(
        endpoint="/endpoint/address",
        method="GET",
        description="Retrieve the list of addresses the endpoint might use to contact us",
        resp_schemas={
            200: DeviceAddresses,
        })
    async def getAddresses():
        origins = await WebConfig.get_origins()
        final_origins = []
        for origin in origins:
            split = urlsplit(origin)
            loc = split.netloc
            if ':' in loc:
                loc = loc[0:loc.rfind(':')]
            final_origins.append(loc)

        data = {
            'addresses': final_origins,
        }

        respond(200, data)

def define_get_platforms(blp):
    @blp.fxroute(
        endpoint="/endpoint/platforms",
        method="GET",
        description="Retrieve the list of valid platforms that can be deployed",
        schema=rkproto_cuserv_GetClientAppPlatforms,
        location='query',
        resp_schemas={
            200: rkproto_cuserv_GetClientAppPlatformsResponse,
        })
    async def getPlatforms(args):
        req = args_to_proto(args, GetClientAppPlatforms)
        rsp = await CuservIfx.send(req, GetClientAppPlatformsResponse)
        data = proto_to_dict(rsp)
        respond(200, data)
