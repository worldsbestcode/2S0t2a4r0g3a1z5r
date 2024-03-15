import os
import subprocess

from typing import List

from flask import request, send_file
from werkzeug.utils import secure_filename
from marshmallow.validate import OneOf

from rkweb.lilmodels.base import Model, field

from session import DesktopSession

from rkweb.auth import login_required
from rkweb.flaskutils import Blueprint, abort, respond
from rkweb.session import AuthSession

# Blueprint
blp = Blueprint("files", "files", url_prefix="/files", description="Manage remote desktop shared files")
def FilesBlueprint():
    return blp

def get_file_type(filepath):

    # Use 'file' to detect file type magic
    stdout_data = []
    proc = subprocess.Popen(
                executable="/usr/bin/file",
                args=["/usr/bin/file", filepath],
                stdout=subprocess.PIPE,
            )
    for line in proc.stdout:
        stdout_data.append(line.decode('utf-8'))
    proc.wait()

    value = ""
    if len(stdout_data) > 0:
        value = stdout_data[0]

    # Parse file output
    ret = "bin"
    if value.find("ASCII") != -1:
        ret = "txt"
    elif value.find("PEM") != -1:
        ret = "pem"
    elif value.find("POSIX tar") != -1:
        if filepath.endswith(".fxb") or filepath.endswith(".fxe"):
            ret = "fxb"
        else:
            ret = "tar"
    elif value.find("Zip archive") != -1:
        ret = "zip"
    elif value.find("ISO") != -1:
        ret = "iso"
    # Use asn1parse to detect DER format
    elif value.find("data") != -1:
        proc = subprocess.Popen(
                    executable="/usr/bin/openssl",
                    args=["/usr/bin/openssl",
                        "asn1parse",
                        "-inform", "DER",
                        "-in", filepath],
                    stdout=subprocess.PIPE,
                )
        for line in proc.stdout:
            ...
        proc.wait()
        if proc.returncode == 0:
            ret = "der"

    return ret

# GET /files -> Retrieve file list
class FileInfo(Model):
    name: int = field(description="File name including directory prefix")
    size: int = field(description="Size in bytes")

    fileType: str = field(
        description="File type",
        validate=OneOf([
            "bin",
            "der",
            "fxb",
            "iso",
            "pem",
            "tar",
            "txt",
            "zip",
        ]),
    )

class FileList(Model):
    files: List[FileInfo] = field(description="List of files available for download")

@blp.fxroute(
    endpoint="",
    method="GET",
    description="Get list of available files for download",
    resp_schemas={
        200: FileList,
    })
@login_required()
async def list():
    # Need to get our VNC session
    desktop_sess = DesktopSession.check()

    # Get base directory
    directory = desktop_sess.get_file_dir()

    # Build up file list
    files = []
    directories = [directory]
    while len(directories) > 0:
        cur_dir = directories[0]
        directories.pop(0)

        # Enforce some arbitrary max depth
        depth = cur_dir.count('/') + cur_dir.count('\\')
        if depth > 8:
            continue

        # For each file
        for filename in os.listdir(cur_dir):
            fullpath = os.path.join(cur_dir, filename)

            # Directory: Add to list to perform recursive list
            if os.path.isdir(fullpath):
                directories.append(fullpath)
                continue

            # Get file info
            file_size = os.path.getsize(fullpath)

            # Detect file type
            file_type = get_file_type(fullpath)

            # Add to output minus the base directory
            files.append({
                'name': fullpath[len(directory)+1:],
                'size': file_size,
                'fileType': file_type,
            })

    # Respond to client
    respond(200, {'files': files})


# GET /files/download?file=%s
class RetrieveFile(Model):
    file: str = field(description="File with full path to download")

@blp.fxroute(
    endpoint="/download",
    method="GET",
    description="Download file",
    schema=RetrieveFile,
    location="query",
    )
@login_required()
async def downloadFile(args):
    # Need to get our VNC session
    desktop_sess = DesktopSession.check()

    # Get base directory
    directory = desktop_sess.get_file_dir()

    # Sane validate file isn't doing anything sneaky
    file = args.get('file')
    if file.find('..') != -1:
        abort(400, "Invalid file name.")

    # Validate file exists
    fullpath = os.path.join(directory, file)
    if not os.path.isfile(fullpath):
        abort(400, "File not found.")

    # Send file
    return send_file(fullpath, as_attachment=True)


# Get amount of size remaining allowed to upload
def get_free_size():
    du_data = []
    directory = DesktopSession.get().get_file_dir()
    proc = subprocess.Popen(
                executable="/usr/bin/du",
                args=["/usr/bin/du", "-s", directory],
                stdout=subprocess.PIPE,
            )
    for line in proc.stdout:
        du_data.append(line.decode('utf-8'))
    proc.wait()

    val = 0
    if len(du_data) > 0:
        pos = du_data[0].find("\t")
        if pos == -1:
            val = du_data[0]
        else:
            val = du_data[0][0:pos]
    val = int(val)

    # This is also enforced in RemoteDesktopDrive.cpp
    maxVal = 5 * 1024 * 1024 * 1024
    if val > maxVal:
        return 0
    return maxVal - val

# POST /files/upload
@blp.fxroute(
    endpoint="/upload",
    method="POST",
    description="Upload a file",
    )
async def uploadFile():
    # Need to get our VNC session
    desktop_sess = DesktopSession.check()

    # Get base directory
    directory = desktop_sess.get_file_dir()

    if 'file' not in request.files:
        abort(400, "File missing.")

    file = request.files['file']
    if file.filename == '':
        abort(400, "No file selected.")

    # Don't let them fill up their max allocated space
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0, os.SEEK_SET)
    if get_free_size() < file_size:
        abort(400, "Not enough space for file.")

    # Calculate the filename to save as
    basename = secure_filename(os.path.basename(file.filename))

    # Save to mount directory
    dest = os.path.join(directory, basename)
    if os.path.exists(dest):
        os.remove(dest)
    file.save(dest)
    os.chmod(dest, 0o0666)

    respond(200)

# GET /files/event -> Check for download event
class EventResponse(Model):
    event: str = field(
        description="Event string for what the remote desktop has for you",
        validate=OneOf(["none", "download", "upload"]),
    )

    file: str = field(description="If desktop wants you to download a file, the file path is provided.")

@blp.fxroute(
    endpoint="/event",
    method="GET",
    description="Check for file download event",
    resp_schemas={
        200: EventResponse,
    })
@login_required()
async def getEvent():
    # Need to get our VNC session
    desktop_sess = DesktopSession.check()

    # rkclient is responsible for managing the IPC file
    filename = "/var/run/fx/tmp/rdevents/{}_out.txt".format(desktop_sess.pid)
    if not os.path.exists(filename):
        # Might be local cardbrowser on the 2U, in which case RD doesn't handle files
        respond(200)

    # Read next event
    fp = open(filename, 'r')
    data = fp.readlines()
    event = "none"
    if len(data) > 0:
        event = data[0]

    # Remove newline
    endln = event.find("\n")
    if endln != -1:
        event = event[0:endln]

    # Write unused events back out
    fp = open(filename, 'w')
    for i in range(1, len(data)):
        fp.write(data[i])
    fp.close()

    filename = None
    filepos = event.find(":")
    if filepos != -1:
        filename = event[filepos + 1:]
        event = event[0:filepos]

    # Intercept token update event
    if event == "token":
        auth_sess = AuthSession.get()
        auth_sess.token = filename
        auth_sess.save()

        event = "none"
        filename = None

    data = {
        'event': event,
    }

    if filename:
        data['file'] = filename

    respond(200, data)


# POST /files/event -> Inform the desktop of a file upload event
class EventRequest(Model):
    event: str = field(
        description="Event string for action the user has completed",
        validate=OneOf(["cancel", "upload"]),
    )

    file: str = field(
        required=False,
        description="If an upload is complete, the file name of the upload.",
    )

@blp.fxroute(
    endpoint="/event",
    method="POST",
    description="Inform file upload event action",
    schema=EventRequest,
    resp_schemas={
        200: EventResponse,
    })
@login_required()
async def postEvent(args):
    # Need to get our VNC session
    desktop_sess = DesktopSession.check()

    # rkclient is responsible for managing the IPC file
    filename = "/var/run/fx/tmp/rdevents/{}_in.txt".format(desktop_sess.pid)
    if not os.path.exists(filename):
        abort(503, "Desktop session is not listening.")

    # Get event string to write to file
    event = args['event']
    if 'file' in args:
        if args['file'].find('..') != -1:
            abort(400, "Invalid file name.")
        event += ":" + secure_filename(args['file'])

    # Write event line
    fp = open(filename, 'a')
    fp.write(event + "\n")
    fp.close()

    respond(200)

