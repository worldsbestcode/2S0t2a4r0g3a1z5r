import re
from flask import jsonify, abort

from rkproto.comm.ResponseMessage_pb2 import ResponseCode as RC

from rkweb.ipc import IpcError

# XXX: Switch this to true to get extra prints
#      useful for debugging compatibility tests
DEBUG=False

GCODE_TO_INT = {
    'OK': 0,
    'CANCELLED': 1,
    'UNKNOWN': 2,
    'INVALID_ARGUMENT': 3,
    'DEADLINE_EXCEEDED': 4,
    'NOT_FOUND': 5,
    'ALREADY_EXISTS': 6,
    'PERMISSION_DENIED': 7,
    'UNAUTHENTICATED': 16,
    'RESOURCE_EXHAUSTED': 8,
    'FAILED_PRECONDITION': 9,
    'ABORTED': 10,
    'OUT_OF_RANGE': 11,
    'UNIMPLEMENTED': 12,
    'INTERNAL': 13,
    'UNAVAILABLE': 14,
    'DATA_LOSS': 15,
}

GCODE_TO_HTTP = {
    'OK':                   200,
    'CANCELLED':            499,
    'UNKNOWN':              500,
    'INVALID_ARGUMENT':     400,
    'DEADLINE_EXCEEDED':    504,
    'NOT_FOUND':            404,
    'ALREADY_EXISTS':       409,
    'PERMISSION_DENIED':    403,
    'UNAUTHENTICATED':      401,
    'RESOURCE_EXHAUSTED':   429,
    'FAILED_PRECONDITION':  400,
    'ABORTED':              409,
    'OUT_OF_RANGE':         400,
    'UNIMPLEMENTED':        501,
    'INTERNAL':             500,
    'UNAVAILABLE':          503,
    'DATA_LOSS':            500,
}

IPC_TO_GCODE = {
    RC.Success: 'OK',
    RC.Unknown: 'UNKNOWN',
    RC.Unspecified: 'UNKNOWN',
    RC.CommandError: 'UNKNOWN',
    RC.ArgumentInvalid: 'INVALID_ARGUMENT',
    RC.ArgumentMissing: 'INVALID_ARGUMENT',
    RC.Timeout: 'DEADLINE_EXCEEDED',
    RC.NotFound: 'NOT_FOUND',
    RC.UnknownCommand: 'NOT_FOUND',
    RC.AlreadyExists: 'ALREADY_EXISTS',
    RC.OperationInProgress: 'FAILED_PRECONDITION',
    RC.AlreadyConnected: 'ALREADY_EXISTS',
    RC.NotAuthorized: 'PERMISSION_DENIED',
    RC.InvalidAuthToken: 'PERMISSION_DENIED',
    RC.AuthFailure: 'PERMISSION_DENIED',
    RC.NotLoggedIn: 'UNAUTHENTICATED',
    RC.InvalidSelection: 'RESOURCE_EXHAUSTED',
    RC.NoOperationInProgress: 'FAILED_PRECONDITION',
    RC.OperationAborted: 'ABORTED',
    RC.ArgumentParseError: 'OUT_OF_RANGE',
    RC.NotSupported: 'UNIMPLEMENTED',
    RC.InternalError: 'INTERNAL',
    RC.Tls: 'INTERNAL',
    RC.FileError: 'INTERNAL',
    RC.DatabaseError: 'INTERNAL',
    RC.ServiceDisabled: 'UNAVAILABLE',
    RC.NotConnected: 'UNAVAILABLE',
    RC.CommunicationError: 'UNAVAILABLE',
    RC.DeviceError: 'UNAVAILABLE',
    RC.IpcError: 'UNAVAILABLE',
    # Google codes with no mapping
    'CANCELLED': 'CANCELLED',
    'DATA_LOSS': 'DATA_LOSS',
}

# Reply without adding in rkweb 'status' field
def respond(code, data):
    ret = jsonify(data)
    ret.status_code = code
    if DEBUG:
        print("GRSP")
        try:
            print(data)
        except:
            pass
    abort(ret)
    assert False

# Convert rkweb IPC error to gRPC Status message
def format_ipc_error(obj_type, ipc_error: IpcError, body: dict=None):
    """
    Create and return a formatted flask.Response object
    """
    if DEBUG:
        print(" IPC(0): {} ({})".format(RC.Code.Name(ipc_error.code), ipc_error.code))

    # Handle key retrieval error
    # This might be not found, it might be invalid UUID format
    if ipc_error.field == "retrieve_key":
        ipc_error.code = RC.NotFound

    # Handle cryptospace retrieval error
    # This might be not found, it might be invalid UUID format
    if ipc_error.field == "uuid":
        ipc_error.code = RC.NotFound

    # Still generating a previously requested key
    if ipc_error.field == "pending_key":
        ipc_error.code = RC.OperationInProgress

    # Special justification error response
    if ipc_error.code == RC.NotAuthorized and ipc_error.field == 'reason':
        prefix = ""
        if obj_type:
            prefix = obj_type.DESCRIPTOR.full_name + "."
        fields = [
            prefix + "additionalContext.accessReasonContext.reason",
        ]
        matches = re.findall(r"'(.*?)'", ipc_error.msg)
        for match in matches:
            fields.append(match)
        return bad_ekms_request(fields=fields, gret=IPC_TO_GCODE[ipc_error.code], message=ipc_error.msg)

    # Not found is schema error
    if ipc_error.code == RC.NotFound:
        prefix = ""
        if obj_type:
            prefix = obj_type.DESCRIPTOR.full_name + "."
        return bad_ekms_request([prefix + ipc_error.field], gret='NOT_FOUND', message='Not found')

    # Schema validation handle gRPC BadRequest object
    if ipc_error.code in [RC.ArgumentMissing, RC.ArgumentInvalid, RC.ArgumentParseError]:
        prefix = ""
        if obj_type:
            prefix = obj_type.DESCRIPTOR.full_name + "."
        return bad_ekms_request([prefix + ipc_error.field], message=RC.Code.Name(ipc_error.code))

    g_code = IPC_TO_GCODE[ipc_error.code]
    response_data = {}
    response_data['code'] = GCODE_TO_INT.get(g_code, 5)
    response_data['message'] = ipc_error.msg

    if body:
        response_data['details'] = body

    resp_code = GCODE_TO_HTTP.get(g_code, 500)
    if DEBUG:
        print(" IPC(1): {} ({})".format(RC.Code.Name(ipc_error.code), ipc_error.code))
        print(" GCODE: {} ({})".format(g_code, response_data['code']))
        print(" HTTP: {}".format(resp_code))
    respond(resp_code, response_data)

# Create gRPC BadRequest response
def bad_ekms_request(fields: list=None, gret='INVALID_ARGUMENT', message='Schema violation'):
    """
    Creates ekms bad request message body
    """
    bad_req = {}
    bad_req['@type'] = 'type.googleapis.com/google.rpc.BadRequest'
    fields_val_list = []
    for field in fields:
        field_val = {'field': field}
        fields_val_list.append(field_val)

    bad_req['fieldViolations'] = fields_val_list
    response_data = {
        'code': GCODE_TO_INT[gret],
        'message': message,
        'details': [bad_req],
    }

    if DEBUG:
        print("SCHEMA ERROR ({})".format(GCODE_TO_HTTP[gret]))
        print(response_data)
    respond(GCODE_TO_HTTP[gret], response_data)
