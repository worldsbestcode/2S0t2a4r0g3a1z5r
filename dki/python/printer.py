import http
from rkweb.ipc import IpcUtils
from rkweb.auth import login_required
from rkweb.session import AuthSession
from rkweb.flaskutils import Blueprint, abort, respond

from rkproto.dki.PrintLabel_pb2 import PrintLabel, Label
from mm_rkproto.dki.PrintLabel import rkproto_dki_PrintLabel

from manager import ServiceManager
from inject_session import InjectSession

blp = Blueprint("print", "print", url_prefix="/print", description="Manage printer settings")

def PrinterBlueprint():
    return blp


@blp.fxroute(
    endpoint="/session",
    method="POST",
    description="Print Session Labels",
    schema=rkproto_dki_PrintLabel)
@login_required()
async def print_label(req: dict):
    service_uuid = req.get('serviceUuid', None)

    if not service_uuid:
        abort(http.HTTPStatus.BAD_REQUEST, "Service UUID is required.")

    custom_service = await ServiceManager().select(service_uuid)

    msg = PrintLabel()

    session_label = Label()
    session_label.uuid = service_uuid
    session_label.title = custom_service.obj_info.name

    msg.labels.append(session_label)
    for associated_object in custom_service.related_info.associated_objects:
        if associated_object.type == "HSM trusted symmetric key":
            label = Label()
            label.uuid = associated_object.uuid
            label.title = associated_object.name
            msg.labels.append(label)

    await IpcUtils.send(
        port=InjectSession.port,
        msg=msg,
        auth_token=AuthSession.auth_token())

    respond(http.HTTPStatus.OK)
