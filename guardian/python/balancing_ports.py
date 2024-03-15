# Flask family
from flask.views import MethodView
from marshmallow import Schema, fields

# Project dependencies
from session import UserSession
from flaskutils import Blueprint, respond
from protoutils import ProtoUtils
from manager_factory import ManagerFactory

# Marshmallow schema
from mm_rkproto.guardian.BalancingPort import rkproto_guardian_BalancingPort_Stub
from mm_rkproto.guardian.BalancingPort import rkproto_guardian_BalancingPort

# Protobuf data models
# Even if it is not instantiated directly in this file, needs to be imported to deserialize IPC responses
from rkproto.mo.ObjectFilter_pb2 import ObjectFilter, FilterClause
from rkproto.guardian.BalancingPort_pb2 import BalancingPort, BalancingPort_Stub

# Blueprint
blp = Blueprint("balancingPorts", "balancingPorts", url_prefix="/balancingPorts", description="Manage balancing ports")
def BalancingPortsBlueprint():
    return blp

# List groups schema
class BalancingPortList(Schema):
    results = fields.List(
        fields.Nested(rkproto_guardian_BalancingPort_Stub),
        required=True,
        description="List of balancing ports with basic information",
    )

# Get stubs
@blp.fxroute(
    endpoint="/list",
    method="GET",
    description="List balancing ports",
    resp_schemas={
        200: BalancingPortList,
    })
async def list():
    # Check login
    UserSession.check_login()

    # Instantiate manager
    manager = ManagerFactory.guardian()

    # Build filter
    obj_filter = ObjectFilter()
    obj_filter.object_type = "rkproto.guardian.BalancingPort"
    obj_filter.sort_attribute = "name"
    obj_filter.stubs = True
    obj_filter.chunk_size = 0

    # Query objects
    (total, results) = await manager.filter(obj_filter)

    # Construct response
    serial_results = []
    for result in results:
        serial_results.append(ProtoUtils.to_json(result))
    ret = {
        'results': serial_results
    }

    return ret

# Get full details of a specific port
@blp.fxroute(
    endpoint="/<uuid>",
    method="GET",
    description="Get balancing port",
    resp_schemas={
        200: rkproto_guardian_BalancingPort,
    })
async def get(uuid):
    # Check login
    UserSession.check_login()

    # Instantiate manager
    manager = ManagerFactory.guardian()

    # Query objects
    port = BalancingPort()
    await manager.select(uuid, port)

    return ProtoUtils.to_json(port)

# Delete a port
@blp.fxroute(
    endpoint="/<uuid>",
    method="DELETE",
    description="Remove balancing port",
    )
async def delete(uuid):
    # Check login
    UserSession.check_login()

    # Instantiate manager
    manager = ManagerFactory.guardian()

    # Query objects
    await manager.remove(uuid)

    respond()

# Add/Update a balancing port
@blp.fxroute(
    endpoint="/",
    method="POST",
    description="Add or modify balancing port",
    schema=rkproto_guardian_BalancingPort,
    )
async def post(args):
    # Check login
    UserSession.check_login()

    # Decode object
    obj = BalancingPort();
    ProtoUtils.from_json(args, obj)

    # Instantiate manager
    manager = ManagerFactory.guardian()

    # Save
    uuid = None
    if obj.obj_info.uuid and len(obj.obj_info.uuid) > 0:
        uuid = await manager.modify(obj)
    else:
        uuid = await manager.add(obj)

    respond(code=200, data={'uuid': uuid})

