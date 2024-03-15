from flask.views import MethodView
from flask_smorest import Blueprint

from session import UserSession

from mm_rkproto.guardian.Device import rkproto_guardian_Device
from mm_rkproto.mo.ObjectFilter import rkproto_mo_ObjectFilter
from mm_rkproto.mo.ObjectResults import rkproto_mo_ObjectResults

# Blueprint
blp = Blueprint("devices", "devices", url_prefix="/devices", description="Manage Futurex appliances")
def DevicesBlueprint():
    return blp

# Filter
@blp.route("")
class DeviceFilter(MethodView):
    @blp.arguments(rkproto_mo_ObjectFilter)
    @blp.response(200, rkproto_mo_ObjectResults)
    def get(self, args):
        auth_err = UserSession.check_login()
        if auth_err:
            return auth_err

        ret = rkproto_mo_ObjectResults()
        return ret

# Get by ID
@blp.route("/<uuid>")
class DeviceRetrieve(MethodView):
    @blp.response(200, rkproto_guardian_Device)
    def get(self, uuid):
        auth_err = UserSession.check_login()
        if auth_err:
            return auth_err

        ret = rkproto_guardian_Device()
        return ret

# TODO: List devices

