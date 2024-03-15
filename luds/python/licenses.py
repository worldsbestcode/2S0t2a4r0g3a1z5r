from rkweb.flaskutils import Blueprint, respond, unauthorized
from rkweb.protoflask import proto_to_dict

from mm_rkproto.luds.RetrieveLicenses import rkproto_luds_RetrieveLicenses
from mm_rkproto.luds.RetrieveLicenses import rkproto_luds_RetrieveLicensesResponse

from rkproto.luds.RetrieveLicenses_pb2 import RetrieveLicenses, RetrieveLicensesResponse

from ludsifx import LudsIfx

# Blueprint
def LicensesBlueprintV1():
    blp = Blueprint("Licenses", "licenses", url_prefix="/licenses",
        description="Get device licenses")
    define_get(blp)
    return blp

def define_get(blp):
    @blp.fxroute(
        endpoint="",
        method="GET",
        description="Retrieve licenses",
        resp_schemas={
            200: rkproto_luds_RetrieveLicensesResponse,
        })
    async def get():
        rsp = await LudsIfx().send(RetrieveLicenses(), RetrieveLicensesResponse)
        data = proto_to_dict(rsp)
        respond(200, data)
