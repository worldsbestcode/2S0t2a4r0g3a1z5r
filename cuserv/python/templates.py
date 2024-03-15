from rkweb.lilmodels.base import Model, List, field
from rkweb.lilmodels.page import PagedRequestModel, PagedResponseModel

from rkweb.auth import perm_required
from rkweb.config import WebConfig
from rkweb.flaskutils import Blueprint, respond, abort
from rkweb.protoflask import serialize_filter_results, load_paging, args_to_proto, proto_to_dict

from flask import request
from marshmallow import fields

# Marshmallow
from mm_rkproto.cuserv.ServiceTemplate import rkproto_cuserv_ServiceTemplate
from mm_rkproto.cuserv.ServiceTemplate import rkproto_cuserv_ServiceTemplate_ADD
from mm_rkproto.cuserv.ServiceTemplate import rkproto_cuserv_ServiceTemplate_GET
from mm_rkproto.cuserv.ServiceTemplate import rkproto_cuserv_ServiceTemplate_MODIFY
from mm_rkproto.cuserv.ServiceTemplate import rkproto_cuserv_ServiceTemplate_Stub
from mm_rkproto.cuserv.ImportTemplate import rkproto_cuserv_ImportTemplate
from mm_rkproto.cuserv.ImportTemplate import rkproto_cuserv_ImportTemplateResponse
from mm_rkproto.cuserv.ExportTemplate import rkproto_cuserv_ExportTemplateResponse

from mm_rkproto.cuserv.Instructions import rkproto_cuserv_Instructions
from mm_rkproto.cuserv.RetrieveInstructions import rkproto_cuserv_RetrieveInstructionSetupsResponse

# Protobufs
from rkproto.mo.ObjectFilter_pb2 import ObjectFilter, FilterClause, FilterComposite
from rkproto.cuserv.ServiceTemplate_pb2 import ServiceTemplate, ServiceTemplate_Stub
from rkproto.cuserv.RetrieveTemplateCategories_pb2 import RetrieveTemplateCategories, RetrieveTemplateCategoriesResponse
from rkproto.cuserv.ImportTemplate_pb2 import ImportTemplate, ImportTemplateResponse
from rkproto.cuserv.ExportTemplate_pb2 import ExportTemplate, ExportTemplateResponse

from rkproto.cuserv.Instructions_pb2 import Instructions
from rkproto.cuserv.RetrieveInstructions_pb2 import RetrieveInstructionSetups
from rkproto.cuserv.RetrieveInstructions_pb2 import RetrieveInstructionSetupsResponse

from manager import TemplateManager, InstructionsManager
from cuservifx import CuservIfx

# Blueprint
def ServiceTemplatesBlueprintV1():
    blp = Blueprint("Service Templates", "templates", url_prefix="/templates", description="Manage service templates")
    define_crud(blp)
    define_list(blp)
    define_get_categories(blp)
    define_import(blp)
    define_export(blp)
    define_instruction_setups(blp)
    define_get_instruction_setup(blp)
    return blp

# CRUD operations
def define_crud(blp):
    from rkweb.protocrud import ProtoCrud
    ProtoCrud(
        name="custom service template",
        blp=blp,
        port=5055,
        proto_class=ServiceTemplate,
        proto_stub_class=ServiceTemplate_Stub,
        mmproto_get=rkproto_cuserv_ServiceTemplate_GET,
        mmproto_stub=None,
        mmproto_add=rkproto_cuserv_ServiceTemplate_ADD,
        mmproto_modify=rkproto_cuserv_ServiceTemplate_MODIFY,
        perm_category="Custom Services",
        manage_perm="Manage")

# Retrieve categories
def define_get_categories(blp):
    class ServiceTemplateCategories(Model):
        categories: List[str] = field(description="The categories")

    @blp.fxroute(
        endpoint="/categories",
        method="GET",
        description="Retrieve the list of all categories",
        resp_schemas={
            200: ServiceTemplateCategories,
        })
    @perm_required("Custom Services")
    async def getCategories():

        msg = RetrieveTemplateCategories()
        rsp = await CuservIfx.send(msg, RetrieveTemplateCategoriesResponse)

        # Add 'All' first and make sure only one exists
        categories = ["All"]
        for cat in rsp.categories:
            if cat != "All":
                categories.append(cat)

        data = {
            'categories': categories
        }

        respond(200, data)

# Retrieve stubs by category
def define_list(blp):
    class ServiceTemplateStubsRequest(PagedRequestModel):
        category: str = field(description="The category", required=False)

    class ServiceTemplateStubs(PagedResponseModel):
        results: list = field(
            description="The page of results",
            marshmallow_field=fields.List(
                fields.Nested(rkproto_cuserv_ServiceTemplate_Stub)
            )
        )

    @blp.fxroute(
        endpoint="/stubs",
        method="GET",
        description="Retrieve a page of deployable service templates by category",
        schema=ServiceTemplateStubsRequest,
        location='query',
        resp_schemas={
            200: ServiceTemplateStubs,
        })
    @perm_required("Custom Services")
    async def getStubs(args):

        # Build filter
        obj_filter = ObjectFilter()
        obj_filter.object_type = "rkproto.cuserv.ServiceTemplate"
        obj_filter.sort_attribute = "name"
        obj_filter.stubs = True
        load_paging(args, obj_filter)

        # Filter by category
        obj_filter.query_params.intersect = True
        category = args.get('category')
        if category and category != 'All':
            clause = FilterClause()
            clause.match_type = FilterClause.MatchType.Equals
            clause.attribute = "categories"
            clause.value = category
            obj_filter.query_params.clauses.append(clause)

        # Filter by enabled features
        features = await WebConfig.get_features()
        type_to_feature = {
            'None': None, # Always provide some type to match against
            'ClientApplication': 'DataProtection',
            'PedInjection': 'DirectKeyInjection',
            'GoogleEkms': 'EKMS',
            'GoogleCse': 'GCSE',
        }

        typed_composite = FilterComposite()
        typed_composite.intersect = False
        for service_type in type_to_feature:
            feat = type_to_feature[service_type]
            if not feat or feat in features:
                clause = FilterClause()
                clause.match_type = FilterClause.MatchType.Equals
                clause.attribute = "type"
                clause.value = service_type
                typed_composite.clauses.append(clause)
        obj_filter.query_params.composites.append(typed_composite)

        # Filter
        (pagination, objs) = await TemplateManager().filter(obj_filter)

        # Respond
        respond(200, serialize_filter_results(pagination, objs))

# Import
def define_import(blp):
    @blp.fxroute(
        endpoint="/import",
        method="POST",
        description="Import a service template",
        schema=rkproto_cuserv_ImportTemplate,
        resp_schemas={
            200: rkproto_cuserv_ImportTemplateResponse,
        })
    @perm_required("Custom Services:Manage")
    async def importTemplate(args):

        req = args_to_proto(args, ImportTemplate)
        rsp = await CuservIfx.send(req, ImportTemplateResponse)

        data = {
            'uuid': rsp.uuid,
        }

        respond(200, data)

# Export
def define_export(blp):
    @blp.fxroute(
        endpoint="/export/<uuid>",
        method="GET",
        description="Export a service template",
        resp_schemas={
            200: rkproto_cuserv_ExportTemplateResponse,
        })
    @perm_required("Custom Services")
    async def exportTemplate(uuid):

        req = ExportTemplate()
        req.uuid = uuid
        rsp = await CuservIfx.send(req, ExportTemplateResponse)

        data = {
            'template_data': rsp.template_data,
        }

        respond(200, data)

# Get instruction setups
def define_instruction_setups(blp):
    @blp.fxroute(
        endpoint="/instructions/<uuid>",
        method="GET",
        description="Retrieve list of instruction setups for a template",
        resp_schemas={
            200: rkproto_cuserv_RetrieveInstructionSetupsResponse,
        })
    @perm_required("Custom Services")
    async def exportTemplate(uuid):

        req = RetrieveInstructionSetups()
        req.template_uuid = uuid
        rsp = await CuservIfx.send(req, RetrieveInstructionSetupsResponse)

        data = {
            'setups': []
        }
        for s in rsp.setups:
            data['setups'].append(s)

        respond(200, data)

# Get instruction setups
def define_get_instruction_setup(blp):
    @blp.fxroute(
        endpoint="/instructions/<templateUuid>/<setup>",
        method="GET",
        description="Retrieve list of instruction setups for a template",
        resp_schemas={
            200: rkproto_cuserv_Instructions,
        })
    @perm_required("Custom Services")
    async def exportInstruction(templateUuid, setup):

        # Build filter
        obj_filter = ObjectFilter()
        obj_filter.object_type = "rkproto.cuserv.Instructions"
        obj_filter.stubs = False
        obj_filter.chunk_size = 2
        obj_filter.query_params.intersect = True

        # Filter by template uuid
        clause = FilterClause()
        clause.match_type = FilterClause.MatchType.Equals
        clause.attribute = "template_uuid"
        clause.value = templateUuid
        obj_filter.query_params.clauses.append(clause)

        # Filter by setup name
        clause = FilterClause()
        clause.match_type = FilterClause.MatchType.Equals
        clause.attribute = "name"
        clause.value = setup
        obj_filter.query_params.clauses.append(clause)

        # Filter
        (pagination, objs) = await InstructionsManager().filter(obj_filter)
        if len(objs) != 1:
            abort(400, "Retrieved {} results.".format(len(objs)))

        # Serialize to JSON
        data = proto_to_dict(objs[0])

        # Embed images into Markdown
        if 'images' in data:
            setup = data['setup']
            for image in data['images']:
                find = '[img:{}]'.format(image['imageName'])
                replace = '![{}]({})'.format(image['imageName'], image['data'])
                setup = setup.replace(find, replace)
            data['setup'] = setup
            del data['images']

        # Respond
        respond(200, data)
