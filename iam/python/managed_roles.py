from rkweb.auth import login_required
from rkweb.flaskutils import Blueprint, respond, abort

from typing import List
from marshmallow import fields, validate
from rkweb.lilmodels.base import Model, field

from rkweb.rkserver import ServerConn, ExcryptMsg
from rkweb.session import AuthSession

import json
import base64

# Blueprint
def ManagedRolesBlueprintV1():
    blp = Blueprint(
        "Managed Roles",
        "managed-roles",
        url_prefix="/managed-roles",
        description="Information about managed roles",
    )
    define_list(blp)
    return blp

def check_error(rsp: ExcryptMsg) -> None:
    if rsp.get_tag("AN") != "Y":
        msg = rsp.to_error()
        if rsp.get_tag("AN") == "P":
            abort(401, msg)
        else:
            abort(400, msg)

def define_list(blp):
    class ManagedRole(Model):
        id: str = field(description="Database identifier (internal use - deprecated)")
        uuid: str = field(description="Unique identifier")
        name: str = field(description="Role name")
        roleType: str = field(description="Role type (Primary, Auxiliary)")
        managedType: str = field(description="Permission level over this role (Viewable, Assignable, Controllable)")
        hardened: bool = field(description="If the role is managed by the HSM")
        management: bool = field(description="If this is a management role or an application partition")

    class ManagedService(Model):
        uuid: str = field(description="Unique identifier")
        name: str = field(description="Service name")
        hardened: bool = field(description="If this service requires hardened role to manage")

    class ManagedRolesList(Model):
        managedRoles: List[ManagedRole] = field(
            description="List of roles you can manage")

        managedServices: List[ManagedService] = field(
            description="List of services you can manage")

    @blp.fxroute(
        endpoint="",
        method="GET",
        description="Retrieve a list managed roles",
        resp_schemas={
            200: ManagedRolesList,
        })
    @login_required()
    async def getManagedRoles():
        session = AuthSession.get()
        jwt = session.get_token()

        # Request all auth mechanisms
        req = ExcryptMsg("[AORKMR;]")
        req.set_tag("JW", jwt)
        rsp = await ServerConn().send_excrypt(req)
        check_error(rsp)

        rkResults = json.loads(base64.b64decode(rsp.get_tag("BO")).decode('utf-8'))
        respond(200, rkResults)
