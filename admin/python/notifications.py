from rkweb.auth import perm_required
from rkweb.flaskutils import Blueprint, respond
from rkweb.lilmodels.base import Model, field
from rkweb.protoflask import serialize_filter_results

from typing import List
from marshmallow import fields

from mm_rkproto.admin.AdminNotification import rkproto_admin_AdminNotification
from mm_rkproto.admin.AdminNotification import rkproto_admin_AdminNotification_ADD
from mm_rkproto.admin.AdminNotification import rkproto_admin_AdminNotification_GET
from mm_rkproto.admin.AdminNotification import rkproto_admin_AdminNotification_MODIFY
from mm_rkproto.admin.AdminNotification import rkproto_admin_AdminNotification_Stub

from rkproto.mo.ObjectFilter_pb2 import ObjectFilter
from rkproto.admin.AdminNotification_pb2 import AdminNotification, AdminNotification_Stub

from manager import AdminNotificationManager

# Blueprint
def NotificationsBlueprintV1():
    blp = Blueprint("Admin Notifications", "notifications", url_prefix="/notifications", description="Manage Admin Notifications")
    define_crud(blp)
    define_list(blp)
    return blp

# CRUD operations
def define_crud(blp):
    from rkweb.protocrud import ProtoCrud
    ProtoCrud(
        name="Admin Notification",
        blp=blp,
        port=5090,
        proto_class=AdminNotification,
        proto_stub_class=AdminNotification_Stub,
        mmproto_get=rkproto_admin_AdminNotification_GET,
        mmproto_stub=None,
        mmproto_add=rkproto_admin_AdminNotification_ADD,
        mmproto_modify=rkproto_admin_AdminNotification_MODIFY,
        perm_category="System",
        manage_perm="Administration")

def define_list(blp):
    class NotificationsList(Model):
        results: List[rkproto_admin_AdminNotification_GET] = field(
            description="The pending admin notifications",
            marshmallow_field=fields.List(
                fields.Nested(rkproto_admin_AdminNotification_GET)
            )
        )

    @blp.fxroute(
        endpoint="/",
        method="GET",
        description="Retrieve all admin notifications",
        resp_schemas={
            200: NotificationsList,
        })
    @perm_required("System:Administration")
    async def list():

        # Build filter
        obj_filter = ObjectFilter()
        obj_filter.object_type = AdminNotification.DESCRIPTOR.full_name
        obj_filter.sort_attribute = 'creation_date'
        obj_filter.ascending = True
        obj_filter.stubs = False
        obj_filter.chunk_size = 10000

        # Filter
        (pagination, objs) = await AdminNotificationManager().filter(obj_filter)

        # Respond
        respond(200, serialize_filter_results(pagination, objs))
