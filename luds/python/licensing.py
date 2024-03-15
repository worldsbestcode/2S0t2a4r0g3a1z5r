from rkweb.auth import login_required, perm_required
from rkweb.flaskutils import Blueprint, respond
from rkweb.protoflask import args_to_proto, proto_to_dict

from mm_rkproto.luds.UpdateLicense import rkproto_luds_UpdateLicense
from mm_rkproto.luds.UpdateLicense import rkproto_luds_UpdateLicenseResponse

from rkproto.luds.UpdateLicense_pb2 import UpdateLicense, UpdateLicenseResponse

from ludsifx import LudsIfx

# Blueprint
def LicensingBlueprintV1():
    blp = Blueprint("Licensing", "licensing", url_prefix="/licensing",
        description="Get or update licensing information")
    define_get(blp)
    define_post(blp)
    return blp

def define_get(blp):
    @blp.fxroute(
        endpoint="",
        method="GET",
        description="Retrieve licensing configuration",
        resp_schemas={
            200: rkproto_luds_UpdateLicenseResponse,
        })
    @perm_required("System:Administration")
    async def get():
        rsp = await LudsIfx().send(UpdateLicense(), UpdateLicenseResponse)
        data = proto_to_dict(rsp)
        respond(200, data)

def define_post(blp):
    @blp.fxroute(
        endpoint="",
        method="POST",
        description="Update licensing configuration",
        schema=rkproto_luds_UpdateLicense,
        )
    @login_required()
    async def post(args):
        req = args_to_proto(args, UpdateLicense)
        await LudsIfx().send(req, UpdateLicenseResponse)
        respond(200)
