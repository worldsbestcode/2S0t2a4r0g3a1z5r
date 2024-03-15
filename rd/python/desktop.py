import os

from flask import request
from marshmallow.validate import OneOf, Range

from rkweb.lilmodels.base import Model, field

from session import DesktopSession
from vnc import VncSession, VncSessionList

from rkweb.auth import user_login_required
from rkweb.session import AuthSession
from rkweb.flaskutils import Blueprint, abort, respond

from rkweb.license import check_licensed

# Global list of VNC sessions
global vncSessions;
vncSessions = VncSessionList()
vncSessions.reset()

# Blueprint
blp = Blueprint("desktop", "desktop", url_prefix="/desktop", description="Manage remote desktop session")
def DesktopBlueprint():
    return blp

def update_view(sess, view, check_alive):
    # rkclient is responsible for managing the IPC file
    filename = "/var/run/fx/tmp/rdviews/{}.txt".format(sess.pid)
    if check_alive and not os.path.exists(filename):
        abort(503, "Desktop session is not listening.")

    # Write the desired view for rkclient to ready
    f = open(filename, "w")
    f.write(view)
    f.close()

# Get your desktop session
# Input
class DesktopConfig(Model):
    width: int = field(
        description="The width for the remote desktop session",
        validate=Range(100, 7680),
    )
    height: int = field(
        description="The height for the remote desktop session",
        validate=Range(100, 4320),
    )
    view: str = field(
        required=False,
        description="View to start on if new session",
    )

# Output
class DesktopInfo(Model):
    port: int = field(description="The remote desktop port to use")
    sess: str = field(description="The unique session identifier")

@blp.fxroute(
    endpoint="",
    method="GET",
    description="Get remote desktop session. Spawn one if one is not started.",
    schema=DesktopConfig,
    location="query",
    resp_schemas={
        200: DesktopInfo,
    })
@check_licensed()
@user_login_required()
async def get(args):
    width = args.get('width')
    height = args.get('height')
    view = None
    try:
        view = args.get('view')
    except:
        pass

    local = request.environ['SERVER_PORT'] == '9876'

    # See if we have a VNC session
    desktop_sess = DesktopSession.get()
    vncSess = vncSessions.get_session(desktop_sess.sess)

    # Need a new VNC Session
    if not vncSess:
        vncSess = await vncSessions.new_session(width, height, view, local)
        if not vncSess:
            abort(503, "No sessions currently available.")
        elif not vncSess.internal_id:
            abort(503, "Failed to start desktop session.")
        desktop_sess.set_vnc_sess(vncSess.pid, vncSess.internal_id, vncSess.vnc_port)

    # Width/Height changed
    if vncSess.width != width or vncSess.height != height:
        vncSessions.pop(vncSess.internal_id)
        vncSess = await vncSessions.new_session(width, height, view, local)
        # Shoulda been happy with what you had
        if not vncSess:
            abort(503, "No sessions currently available.")
        elif not vncSess.internal_id:
            abort(503, "Failed to resize desktop session.")
        desktop_sess.set_vnc_sess(vncSess.pid, vncSess.internal_id, vncSess.vnc_port)

    # Update the view
    if desktop_sess.pid > 0 and view:
        update_view(desktop_sess, view, check_alive=False)

    # Output
    data = {
        'port': vncSess.vnc_port,
        'sess': vncSess.external_id,
    }

    # Give the port number to the client
    respond(200, data)

# Change which view is being displayed
# Grep REMOTE_DESKTOP_VIEWS
class ViewSelection(Model):
    view: str = field(
        description="The remote desktop view to display",
        validate=OneOf([
            'Audit Log',
            'Balanced Device',
            'CA',
            'Card Stat',
            'Card',
            'Cloud Credential',
            'Config',
            'Database',
            'Device Host',
            'File Enc',
            'Google Crypto Space',
            'Hardware',
            'Host',
            'Identity Provider',
            'Identity',
            'Job',
            'KMIP',
            'Key Group',
            'Key',
            'LDAP Directory',
            'License',
            'Notification',
            'Peer',
            'Personal Key',
            'RKMS',
            'Remote Drive',
            'Report',
            'Request Approval',
            'Role',
            'SKI',
            'Serial Device',
            'System Key',
            'System Log',
            'TLS PKI',
            'TLS Profile',
            'TLS Tunnel',
            'Template',
            'Tokenization',
            'V3 Ext',
            'Virtual HSMs',
            'Virtual HSM Hosts',
            'Web Profile',
            'Windows PKI Template',
            'X509 DN',
        ]),
    )

@blp.fxroute(
    endpoint="/view",
    method="POST",
    description="Set which remote desktop view to focus",
    schema=ViewSelection,
    )
@check_licensed()
@user_login_required()
async def post(args):
    view = args['view']

    # Need to get our VNC session
    desktop_sess = DesktopSession.check()

    # Update view
    update_view(desktop_sess, view, check_alive=True)

    # Done
    respond(200)
