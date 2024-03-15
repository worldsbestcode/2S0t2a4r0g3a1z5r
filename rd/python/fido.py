import os
import json

from marshmallow.validate import OneOf

from rkweb.lilmodels.base import Model, field

from session import DesktopSession

from rkweb.auth import login_required
from rkweb.flaskutils import Blueprint, respond

# Blueprint
blp = Blueprint("fido", "fido", url_prefix="/fido", description="Integrate with FIDO tokens")
def FidoBlueprint():
    return blp

class FidoEvent(Model):
    command: str = field(
        required=False,
        description="The type of FIDO event that needs to be proxied to the token",
        validate=OneOf([
            "newCredential",
            "signChallenge",
        ]),
    )

@blp.fxroute(
    endpoint="",
    method="GET",
    description="Check if there is a FIDO event in the queue",
    resp_schemas={
        200: FidoEvent,
    })
@login_required()
async def get():
    # Need to get our VNC session
    desktop_sess = DesktopSession.check()

    # Find the event file
    filename = "/var/run/fx/tmp/rdfido/{}_out.txt".format(desktop_sess.pid)
    if not os.path.exists(filename):
        respond(200)

    # Read next event
    fp = open(filename, 'r')
    data = fp.readlines()
    fp.close()

    event = ""
    if len(data) > 0:
        event = data[0]

    # Nothing to do
    if len(event) == 0:
        respond(200)

    # Truncate events file
    fp = open(filename, 'w')
    fp.close()

    # Remove newline
    endln = event.find("\n")
    if endln != -1:
        event = event[0:endln]

    # Decode
    data = json.loads(event)

    # Respond
    respond(200, data)


class FidoAnswer(Model):
    response: str = field(
        required=False,
        description="The result of the FIDO operation",
    )

    error: str = field(
        required=False,
        description="An error to report that occurred during the FIDO operation",
    )

@blp.fxroute(
    endpoint="",
    method="POST",
    description="Answer a FIDO event",
    schema=FidoAnswer)
@login_required()
async def post(args):
    # Need to get our VNC session
    desktop_sess = DesktopSession.check()

    # Serialize to JSON
    result = json.dumps(args)

    # Write to file
    filename = "/var/run/fx/tmp/rdfido/{}_in.txt".format(desktop_sess.pid)
    fp = open(filename, 'w')
    fp.write(result)
    fp.close()

    # Respond
    respond(200)

