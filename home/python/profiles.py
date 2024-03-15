from typing import List

from rkweb.lilmodels.base import Model, field
from rkweb.lilmodels.shared import Base64Str
from marshmallow.validate import Length

from flask import request

from rkweb.auth import login_required
from rkweb.session import AuthSession
from rkweb.flaskutils import Blueprint, abort, respond
from rkweb.rkserver import ExcryptMsg, ServerConn

# Blueprint
blp = Blueprint("profile", "profile", url_prefix="/profile", description="Get user profiles")
def ProfileBlueprint():
    return blp

class Profile(Model):
    user: str = field(description="The user the profile belongs to")
    profile: Base64Str = field(description="The data stored in the user's profile",
                               validate=Length(0, 8 * 1024))

# GET /profile
class Profiles(Model):
    profiles: List[Profile] = field(description="The logged in users' profiles")

@blp.fxroute(
    endpoint="/",
    method="GET",
    description="Get logged in users' profiles",
    resp_schemas={
        200: Profiles,
    })
@login_required()
async def get_profiles():
    # Get profiles from server
    server = ServerConn()
    msg = ExcryptMsg("[AOWEBP;]")
    msg.set_tag("OP", "list")
    msg.set_tag("JW", AuthSession.auth_token())
    rsp = await server.send_excrypt(msg)

    # Parse profiles
    profiles = []
    for profile in rsp.get_tag("PF").split(","):
        pair = profile.split(":")
        profiles.append({'user': pair[0], 'profile': pair[1]})

    respond(200, {'profiles': profiles})

# POST /profile
@blp.fxroute(
    endpoint="/",
    method="POST",
    schema=Profile,
    description="Set a user's profile")
@login_required()
async def set_profile(args):
    # Send request to server
    server = ServerConn()
    msg = ExcryptMsg("[AOWEBP;]")
    msg.set_tag("OP", "set")
    msg.set_tag("NA", args['user'])
    msg.set_tag("PF", args['profile'])
    msg.set_tag("JW", AuthSession.auth_token())
    rsp = await server.send_excrypt(msg)

    # Return error if any
    if rsp.get_tag("AN") != "Y":
        abort(500, "Failed to set user profile: " + rsp.to_error())

    respond(200)
