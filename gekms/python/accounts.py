from rkweb.auth import login_required
from rkweb.flaskutils import Blueprint, respond

from mm_rkproto.gekms.ServiceAccountsCrud import rkproto_gekms_RetrieveServiceAccountsResponse

from rkproto.gekms.ServiceAccountsCrud_pb2 import RetrieveServiceAccounts
from rkproto.gekms.ServiceAccountsCrud_pb2 import RetrieveServiceAccountsResponse
from rkproto.gekms.ServiceAccountsCrud_pb2 import RemoveServiceAccount
from rkproto.gekms.ServiceAccountsCrud_pb2 import AddServiceAccount

from gekmsifx import GekmsIfx

from rkweb.protoflask import proto_to_dict

# Blueprint
def AccountsBlueprintV1():
    blp = Blueprint(
        "Google Service Accounts",
        "accounts",
        url_prefix="/accounts",
        description="Manage Google Service Accounts")
    define_add(blp)
    define_list(blp)
    define_remove(blp)
    return blp

def define_list(blp):
    @blp.fxroute(
        endpoint="/<service>",
        method="GET",
        description="Retrieve the Google service accounts associated with a service",
        resp_schemas={
            200: rkproto_gekms_RetrieveServiceAccountsResponse,
        })
    @login_required()
    async def getServiceAccounts(service):
        msg = RetrieveServiceAccounts()
        msg.service_uuid = service

        rsp = await GekmsIfx.send(msg, RetrieveServiceAccountsResponse)

        data = proto_to_dict(rsp)
        if not 'accounts' in data:
            data['accounts'] = []
        respond(200, data)

def define_add(blp):
    @blp.fxroute(
        endpoint="/<service>/<account>",
        method="POST",
        description="Add a service account to a deployed service",
        )
    @login_required()
    async def addServiceAccount(service, account):
        msg = AddServiceAccount()
        msg.service_uuid = service
        msg.account_name = account;

        await GekmsIfx.send(msg, None)
        respond(200)

def define_remove(blp):
    @blp.fxroute(
        endpoint="/<service>/<account>",
        method="DELETE",
        description="Remove a serivce account from a deployed service",
        )
    @login_required()
    async def removeServiceAccount(service, account):
        msg = RemoveServiceAccount()
        msg.service_uuid = service
        msg.account_name = account

        await GekmsIfx.send(msg, None)
        respond(200)
