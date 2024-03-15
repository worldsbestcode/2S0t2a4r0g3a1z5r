from rkweb.lilmodels.base import Model, List, field
from rkweb.lilmodels.page import PagedRequestModel, PagedResponseModel

from rkweb.auth import perm_required
from rkweb.flaskutils import Blueprint, respond
from rkweb.protoflask import serialize_pagination, proto_to_dict

from flask import request
from marshmallow import fields

from cuservifx import CuservIfx

from mm_rkproto.cuserv.RetrieveAuditLogs import rkproto_cuserv_AuditLog
from rkproto.cuserv.RetrieveAuditLogs_pb2 import RetrieveAuditLogs, RetrieveAuditLogsResponse as pbRALR
from rkproto.cuserv.ExportAuditLogs_pb2 import ExportAuditLogs, ExportAuditLogsResponse as pbEALR

# Blueprint
def AuditLogsBlueprintV1():
    blp = Blueprint("Audit logs", "auditlogs", url_prefix="/auditlogs", description="Retrieve audit logs for a service")
    define_retrieve_logs(blp)
    define_export_logs(blp)
    return blp

# Retrieve audit logs
def define_retrieve_logs(blp):
    class RetrieveAuditLogsRequest(PagedRequestModel):
        attributeQuery: str = field(
            description="Specific attribute to query. Ex: gekms_key=<uuid>",
            required=False
        )

    class RetrieveAuditLogsResponse(PagedResponseModel):
        results: list = field(
            description="The page of results",
            marshmallow_field=fields.List(
                fields.Nested(rkproto_cuserv_AuditLog)
            )
        )

    @blp.fxroute(
        endpoint="/<uuid>",
        method="GET",
        description="Retrieve audit logs for a deployed service",
        schema=RetrieveAuditLogsRequest,
        location='query',
        resp_schemas={
            200: RetrieveAuditLogsResponse,
        })
    @perm_required("Custom Services")
    async def getLogs(args, uuid):

        # Input
        page = int(args.get('page', 1))
        page_size = int(args.get('pageSize', 100))

        # Send protobuf
        msg = RetrieveAuditLogs()
        msg.service_uuid = uuid
        msg.attribute_query = args.get('attributeQuery', "")
        msg.chunk = page - 1 if page > 0 else page
        msg.chunk_size = page_size
        rsp = await CuservIfx.send(msg, pbRALR)

        # Output
        data = serialize_pagination(rsp.pagination)
        rsp_dict = proto_to_dict(rsp)
        data['logs'] = rsp_dict['logs'] if 'logs' in rsp_dict else []

        respond(200, data)

def define_export_logs(blp):
    class ExportAuditLogsRequest(Model):
        attributeQuery: str = field(
            description="Specific attribute to query. Ex: gekms_key=<uuid>",
            required=False
        )
        startDate: str = field(
            description="Start of date filter range",
            required=False
        )
        endDate: str = field(
            description="End of date filter range",
            required=False
        )
        exportFormat: str = field(
            description="Export format",
            required=False
        )

    class ExportAuditLogsResponse(Model):
        result: str = field(
            description="The results CSV"
        )

    @blp.fxroute(
        endpoint="/<uuid>/export",
        method="GET",
        description="Export audit logs for a deployed service",
        schema=ExportAuditLogsRequest,
        location='query',
        resp_schemas={
            200: ExportAuditLogsResponse,
        })
    @perm_required("Custom Services")
    async def exportLogs(args, uuid):

        # Send protobuf
        msg = ExportAuditLogs()
        msg.service_uuid = uuid
        msg.attribute_query = args.get('attributeQuery', "")
        msg.start_date = args.get('startDate', "")
        msg.end_date = args.get('endDate', "")
        msg.export_format = args.get('exportFormat', "JSON")
        rsp = await CuservIfx.send(msg, pbEALR)

        # Output
        data = proto_to_dict(rsp)
        respond(200, data)
