import http
from rkweb.auth import login_required
from rkweb.flaskutils import Blueprint, respond, abort
from mm_rkproto.dki.QueryLogs import rkproto_dki_QueryLogsResponse, rkproto_dki_QueryLogs
from rkproto.dki.InjectionLog_pb2 import InjectionLog, InjectionLog_Stub
from mm_rkproto.dki.InjectionLog import rkproto_dki_InjectionLog_GET
from rkweb.protocrud import ProtoCrud

from manager import InjectionLogManager
from inject_session import InjectSession
from rkproto.mo.ObjectFilter_pb2 import ObjectFilter, FilterClause
from rkweb.protoflask import serialize_filter_results, load_paging

blp = Blueprint('injectionlogs', "logs", url_prefix='/logs/')


def LogsBlueprint():
    return blp

ProtoCrud(
    name="Injection log",
    blp=blp,
    port=InjectSession().port,
    proto_class=InjectionLog,
    proto_stub_class=InjectionLog_Stub,
    mmproto_get=rkproto_dki_InjectionLog_GET,
    mmproto_stub=None,
    mmproto_add=None,
    mmproto_modify=None,
    perm_category="Custom Services",
    delete=False,
    manage_perm="Manage")


@blp.fxroute(
    endpoint="/info/<uuid>",
    method="GET",
    description="Get logs info for session")
@login_required()
async def getLogInfo(uuid: str):
    object_filter = ObjectFilter()
    object_filter.object_type = "rkproto.dki.InjectionLog"
    object_filter.sort_attribute = "creation_date"
    object_filter.stubs = False

    session_clause = FilterClause()
    session_clause.match_type = FilterClause.MatchType.Equals
    session_clause.attribute = "session_uuid"
    session_clause.value = uuid
    object_filter.query_params.clauses.append(session_clause)

    success_clause = FilterClause()
    success_clause.match_type = FilterClause.MatchType.Equals
    success_clause.attribute = "successful"
    success_clause.value = "1"
    object_filter.query_params.intersect = True
    object_filter.query_params.clauses.append(success_clause)

    object_filter.chunk = 0
    object_filter.chunk_size = 300

    total_keys_loaded = 0
    (pagination, injection_logs) = await InjectionLogManager().filter(object_filter)

    for injection_log in injection_logs:
        total_keys_loaded += len(injection_log.injected_keys)

    respond(http.HTTPStatus.OK, {
        "sessionUuid": uuid,
        "totalDevicesLoaded": len(injection_logs),
        "totalKeysLoaded": total_keys_loaded
    })


@blp.fxroute(
    endpoint='/query',
    method="GET",
    description="Get Injection status",
    location='query',
    schema=rkproto_dki_QueryLogs,
    resp_schemas={
        http.HTTPStatus.OK: rkproto_dki_QueryLogsResponse,
    })
@login_required()
async def queryLogs(req):
    service_uuid = req.get('serviceUuid', None)
    if service_uuid is None:
        abort(http.HTTPStatus.BAD_REQUEST, 'service_uuid is required')

    session_uuid = req.get('sessionUuid', None)
    if session_uuid is None:
        abort(http.HTTPStatus.BAD_REQUEST, 'session_uuid is required')

    # Build filter
    object_filter = ObjectFilter()
    object_filter.object_type = "rkproto.dki.InjectionLog"
    object_filter.sort_attribute = "creation_date"
    object_filter.stubs = False

    load_paging(req, object_filter)

    # Filter by service uuid
    service_clause = FilterClause()
    service_clause.match_type = FilterClause.MatchType.Equals
    service_clause.attribute = "service_uuid"
    service_clause.value = service_uuid
    object_filter.query_params.intersect = True
    object_filter.query_params.clauses.append(service_clause)

    session_clause = FilterClause()
    session_clause.match_type = FilterClause.MatchType.Equals
    session_clause.attribute = "session_uuid"
    session_clause.value = session_uuid
    object_filter.query_params.clauses.append(session_clause)

    # Filter
    (pagination, injection_logs) = await InjectionLogManager().filter(object_filter)
    # Respond
    respond(http.HTTPStatus.OK, serialize_filter_results(pagination, injection_logs))
