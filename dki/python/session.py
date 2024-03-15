import http
from rkweb.ipc import IpcUtils
from rkweb.auth import login_required
from rkweb.session import AuthSession
from rkweb.flaskutils import Blueprint, abort, respond

from mm_rkproto.dki.StartSession import rkproto_dki_StartSession, rkproto_dki_StartSessionResponse
from mm_rkproto.dki.QuerySession import rkproto_dki_QuerySession, rkproto_dki_QuerySessionResponse
from mm_rkproto.dki.Session import rkproto_dki_Session

from rkproto.dki.StartSession_pb2 import StartSession as StartSession, StartSessionResponse
from rkproto.dki.QuerySession_pb2 import QuerySession, QuerySessionResponse
from rkproto.mo.ObjectFilter_pb2 import ObjectFilter, FilterClause
from rkweb.lilmodels.page import PagedRequestModel, PagedResponseModel
from rkweb.lilmodels.base import field

from inject_session import InjectSession
from manager import ServiceManager, TemplateManager, SessionManager
from marshmallow import fields
from rkweb.protoflask import serialize_filter_results, load_paging

from google.protobuf.json_format import MessageToDict

# Blueprint
blp = Blueprint("session",
                "session", url_prefix="/session",
                description="Manage injection session")


def SessionBlueprint():
    return blp


class StartServiceSession(rkproto_dki_StartSession):
    serviceId = fields.String(
        description="""Service Id to associate with the ped inject session.""",
        required=False
    )


class ServiceSessions(PagedRequestModel):
    serviceUuid: str = field(
        description="Service uuid used to filter",
        required=False
    )


class ServiceSessionsResponse(PagedResponseModel):
    results: list = field(
        description="The page of results",
        marshmallow_field=fields.List(
            fields.Nested(rkproto_dki_Session)
        )
    )


@blp.fxroute(
    endpoint="/start",
    method="POST",
    description="Start a new session.",
    schema=StartServiceSession,
    resp_schemas={
        http.HTTPStatus.OK: rkproto_dki_StartSessionResponse,
    })
@login_required()
async def start(req: dict):
    # Check for existing session associated with flask
    service_id = req.get('serviceId', None)

    print(f'Attempting to start session for service: {service_id}')
    inject_session = InjectSession.get(service_id)

    if inject_session.session_id:
        msg = QuerySession()
        msg.session_uuid = inject_session.session_id
        # if the session has not expired, reset the timer
        msg.keep_alive = False
        rsp = await IpcUtils.send(
            port=InjectSession.port,
            msg=msg,
            resp_type=QuerySessionResponse,
            auth_token=AuthSession.auth_token()
        )

        # If the remaining time is 0, that mean the session has been cleaned up
        if rsp.remaining_time > 0:
            print(f'Old session" {inject_session.session_id} is alive.')
            data = inject_session.to_dict()
            respond(http.HTTPStatus.OK, data)

    device_group = req.get('deviceGroup', None)
    if device_group is None:
        abort(http.HTTPStatus.BAD_REQUEST, "Device Group is required.")

    custom_service = await ServiceManager().select(service_id)

    template_uuid = custom_service.template_uuid
    service_template = await TemplateManager().select(template_uuid)
    vendor = service_template.params.details.vendor

    auth_token = AuthSession.auth_token()
    # Start new session
    msg = StartSession()
    msg.device_group = device_group
    msg.service_uuid = service_id
    msg.company_name = vendor

    rsp = await IpcUtils.send(
        port=InjectSession.port,
        msg=msg,
        resp_type=StartSessionResponse,
        auth_token=auth_token
    )

    # Save to flask session
    print(f'Starting new session: {rsp.session}')
    inject_session.start(rsp.session)

    # Respond
    data = inject_session.to_dict()
    respond(http.HTTPStatus.OK, data)

@blp.fxroute(
    endpoint="/query",
    method="GET",
    location='query',
    schema=rkproto_dki_QuerySession,
    description="query session uuid.",
    resp_schemas={
        http.HTTPStatus.OK: rkproto_dki_QuerySessionResponse,
    })
@login_required()
async def query(req):

    session_uuid = req.get('sessionUuid', None)
    keep_alive = req.get('keepAlive', False)

    if session_uuid is None:
        abort(http.HTTPStatus.BAD_REQUEST, "service_uuid is required")

    msg = QuerySession()
    msg.session_uuid = session_uuid

    if isinstance(keep_alive, str):
        if keep_alive == "true":
            keep_alive = True
        else:
            keep_alive = False

    msg.keep_alive = keep_alive
    rsp = await IpcUtils.send(
        port=InjectSession.port,
        msg=msg,
        resp_type=QuerySessionResponse,
        auth_token=AuthSession.auth_token()
    )

    # Success
    respond(http.HTTPStatus.OK, MessageToDict(rsp, including_default_value_fields=True))


@blp.fxroute(
    endpoint="/stubs",
    method="GET",
    location='query',
    schema=ServiceSessions,
    description="query session uuid.",
    resp_schemas={
        http.HTTPStatus.OK: ServiceSessionsResponse
    })
@login_required()
async def stubs(req):
    service_uuid = req.get('serviceUuid', None)
    if service_uuid is None:
        abort(http.HTTPStatus.BAD_REQUEST, 'service_uuid is required')

    object_filter = ObjectFilter()
    object_filter.object_type = "rkproto.dki.Session"
    object_filter.sort_attribute = "start_time"
    object_filter.ascending = False
    object_filter.stubs = False

    load_paging(req, object_filter)

    service_clause = FilterClause()
    service_clause.match_type = FilterClause.MatchType.Equals
    service_clause.attribute = "service_uuid"
    service_clause.value = service_uuid
    object_filter.query_params.intersect = True
    object_filter.query_params.clauses.append(service_clause)

    (pagination, sessions) = await SessionManager().filter(object_filter)
    respond(http.HTTPStatus.OK, serialize_filter_results(pagination, sessions))
