from flask import request, jsonify, abort
from rkweb.ipc import IpcError
from rkweb.auth import check_csrf_login
from rkweb.flaskutils import Blueprint
from rkweb.protoflask import proto_to_dict
from rkweb.session import AuthSession

# CreateKey
from mm_proto.control_plane_service import google_cloud_ekms_v0_CreateKeyRequest
from mm_proto.control_plane_service import google_cloud_ekms_v0_CreateKeyResponse
from rkproto.gekms.CreateKey_pb2 import CreateKey as fxCreateKey
from rkproto.gekms.CreateKey_pb2 import CreateKeyResponse as fxCreateKeyResponse
from proto.control_plane_service_pb2 import CreateKeyRequest
from proto.control_plane_service_pb2 import CreateKeyResponse

# DestroyKey
from mm_proto.control_plane_service import google_cloud_ekms_v0_DestroyKeyRequest
from mm_proto.control_plane_service import google_cloud_ekms_v0_DestroyKeyResponse
from rkproto.gekms.DestroyKey_pb2 import DestroyKey as fxDestroyKey
from proto.control_plane_service_pb2 import DestroyKeyRequest
from proto.control_plane_service_pb2 import DestroyKeyResponse

# CheckCryptoSpacePermissions
from mm_proto.control_plane_service import google_cloud_ekms_v0_CheckCryptoSpacePermissionsRequest
from mm_proto.control_plane_service import google_cloud_ekms_v0_CheckCryptoSpacePermissionsResponse
from rkproto.gekms.CheckCryptoSpacePermissions_pb2 import CheckCryptoSpacePermissions as fxCheckCryptoSpacePermissions
from proto.control_plane_service_pb2 import CheckCryptoSpacePermissionsRequest
from proto.control_plane_service_pb2 import CheckCryptoSpacePermissionsResponse

# GetPublicKey
from mm_proto.external_kms import google_cloud_ekms_v0_GetPublicKeyRequest
from mm_proto.external_kms import google_cloud_ekms_v0_GetPublicKeyResponse
from rkproto.gekms.GetPublicKey_pb2 import GetPublicKey as fxGetPublicKey
from proto.external_kms_pb2 import GetPublicKeyRequest
from proto.external_kms_pb2 import GetPublicKeyResponse

# AsymmetricSign
from mm_proto.external_kms import google_cloud_ekms_v0_AsymmetricSignRequest
from mm_proto.external_kms import google_cloud_ekms_v0_AsymmetricSignResponse
from rkproto.gekms.AsymmetricSign_pb2 import AsymmetricSign as fxAsymmetricSign
from proto.external_kms_pb2 import AsymmetricSignRequest
from proto.external_kms_pb2 import AsymmetricSignResponse

# SymmetricWrap
from mm_proto.external_kms import google_cloud_ekms_v0_WrapRequest
from mm_proto.external_kms import google_cloud_ekms_v0_WrapResponse
from rkproto.gekms.SymmetricWrap_pb2 import SymmetricWrap as fxSymmetricWrap
from proto.external_kms_pb2 import WrapRequest
from proto.external_kms_pb2 import WrapResponse

# SymmetricUnwrap
from mm_proto.external_kms import google_cloud_ekms_v0_UnwrapRequest
from mm_proto.external_kms import google_cloud_ekms_v0_UnwrapResponse
from rkproto.gekms.SymmetricWrap_pb2 import SymmetricUnwrap as fxSymmetricUnwrap
from proto.external_kms_pb2 import UnwrapRequest
from proto.external_kms_pb2 import UnwrapResponse

# GetInfo
from rkproto.gekms.GetInfo_pb2 import GetInfo
from mm_proto.external_kms import google_cloud_ekms_v0_GetInfoResponse
from proto.external_kms_pb2 import GetInfoResponse

import json
from google.protobuf import json_format

from gekmsifx import GekmsIfx

from google_errors import IPC_TO_GCODE, format_ipc_error, bad_ekms_request, DEBUG

# Don't add status field normal rkweb REST adds
def gapi_respond(code: int, data: dict):
    ret = jsonify(data)
    ret.status_code = code
    if DEBUG:
        print("RSP")
        print(data)
    abort(ret)
    assert False

# Special login check handler that catches errors and responds in gRPC
from functools import wraps
from werkzeug.exceptions import HTTPException
from rkproto.comm.ResponseMessage_pb2 import ResponseCode as RC
def gapi_login_required():
    def wrapper(func):
        @wraps(func)
        async def check_csrf_login_wrapper(*args, **kwargs):
            process_func = None
            # Do login check with special error response handler
            try:
                await check_csrf_login()
                process_func = func
            except HTTPException as e:
                error = IpcError(RC.NotLoggedIn, "auth", "Authentication error")
                format_ipc_error(None, error)
            # Forward to view
            if process_func:
                return await process_func(*args, **kwargs)
        return check_csrf_login_wrapper
    return wrapper

# Convert input dictionary to protobuf request message
from keys import justifications
def req_to_proto(req, proto):
    # Canonicalize any unknown justification to REASON_UNSPECIFIED
    topdict = req
    empty = False

    # Create the top level key
    field_name = ""
    if 'additionalContext' in topdict:
        topdict = topdict['additionalContext']
        field_name = 'additionalContext.'
    if not 'accessReasonContext' in topdict:
        empty = True
        topdict['accessReasonContext'] = {}

    # No reason = KAJ_UNAVAILABLE
    if empty and not 'reason' in topdict['accessReasonContext']:
        topdict['accessReasonContext']['reason'] = 'KAJ_UNAVAILABLE'
    # Empty reason = default enum value (REASON_UNSPECIFIED) not serialized by GRPC
    elif not empty and not 'reason' in topdict['accessReasonContext']:
        topdict['accessReasonContext']['reason'] = 'REASON_UNSPECIFIED'
    # Unknown reason = KAJ_UNKNOWN
    elif not topdict['accessReasonContext']['reason'] in justifications:
        topdict['accessReasonContext']['reason'] = 'KAJ_UNKNOWN'

    if DEBUG:
        print("Final Reason: ", topdict['accessReasonContext']['reason'])

    # Convert request dictionary to protobuf object
    json_format.Parse(json.dumps(req), proto, ignore_unknown_fields=True)

# Blueprint
def GapiBlueprintV0():
    blp = Blueprint("Google External Key Management", "gapi", url_prefix="", description="Implements the Google External Key Management API")
    define_create_key(blp)
    define_destroy_key(blp)
    define_check_perms(blp)
    define_get_key(blp)
    define_sign(blp)
    define_wrap(blp)
    define_unwrap(blp)
    define_get_info(blp)
    return blp

def define_create_key(blp):
    @blp.fxroute(
        endpoint="/cryptospaces/<cryptospace>:createKey",
        method="POST",
        description="Create a key in a cryptospace",
        schema=google_cloud_ekms_v0_CreateKeyRequest,
        resp_schemas={
            200: google_cloud_ekms_v0_CreateKeyResponse,
        },
        schema_error_handler=bad_ekms_request)
    @gapi_login_required()
    async def createKey(req, cryptospace):
        try:
            if DEBUG:
                print("CREATE KEY")
                print(AuthSession.auth_token())
                print("CRYPTOSPACE: " + cryptospace)
                print(request.get_data().decode('utf-8'))
                print("")

            # To protobuf
            wrapper = fxCreateKey()
            req_to_proto(req, wrapper.gapi)
            # Put inside our wrapper
            wrapper.request_uri =  request.base_url
            wrapper.crypto_space = cryptospace
            # Forward to microservice
            rspWrapper = await GekmsIfx.send(wrapper, fxCreateKeyResponse)
            rsp = rspWrapper.gapi
            # From protobuf
            data = proto_to_dict(rsp)
            gapi_respond(200, data)
        except IpcError as e:
            return format_ipc_error(CreateKeyRequest, e)

def define_destroy_key(blp):
    @blp.fxroute(
        endpoint="/keys/<key>:destroyKey",
        method="POST",
        description="Destroy an existing key",
        schema=google_cloud_ekms_v0_DestroyKeyRequest,
        resp_schemas={
            200: google_cloud_ekms_v0_DestroyKeyResponse,
        },
        schema_error_handler=bad_ekms_request)
    @gapi_login_required()
    async def createKey(req, key):
        try:
            if DEBUG:
                print("DESTROY KEY")
                print(AuthSession.auth_token())
                print("KEY: " + key)
                print(request.get_data().decode('utf-8'))
                print("")

            # To protobuf
            wrapper = fxDestroyKey()
            req_to_proto(req, wrapper.gapi)
            # Put inside our wrapper
            wrapper.request_uri =  request.base_url
            wrapper.key_uuid = key
            # Forward to microservice
            rsp = await GekmsIfx.send(wrapper, DestroyKeyResponse)
            # From protobuf
            data = proto_to_dict(rsp)
            gapi_respond(200, data)
        except IpcError as e:
            return format_ipc_error(DestroyKeyRequest, e)

def define_check_perms(blp):
    async def checkPerms(req, cryptospace, service_account = None):
        try:
            if DEBUG:
                print("CHECK PERMISSIONS")
                print(AuthSession.auth_token())
                print("CRYPTOSPACE: " + cryptospace)
                print("ACCOUNT: " + str(service_account))
                print(request.get_data().decode('utf-8'))
                print("")

            # To protobuf
            wrapper = fxCheckCryptoSpacePermissions()
            req_to_proto(req, wrapper.gapi)
            # Put inside our wrapper
            wrapper.request_uri =  request.base_url
            wrapper.crypto_space = cryptospace
            if service_account:
                wrapper.service_account = service_account
            # Forward to microservice
            rsp = await GekmsIfx.send(wrapper, CheckCryptoSpacePermissionsResponse)
            # From protobuf
            data = proto_to_dict(rsp)
            gapi_respond(200, data)
        except IpcError as e:
            return format_ipc_error(CheckCryptoSpacePermissionsRequest, e)

    @blp.fxroute(
        endpoint="/cryptospaces/<cryptospace>:checkCryptoSpacePermissions",
        method="POST",
        description="Checks that the identity included in the request has all of the specified permissions in the specified Crypto Space.",
        schema=google_cloud_ekms_v0_CheckCryptoSpacePermissionsRequest,
        resp_schemas={
            200: google_cloud_ekms_v0_CheckCryptoSpacePermissionsResponse,
        },
        schema_error_handler=bad_ekms_request)
    @gapi_login_required()
    async def checkSpacePerms(req, cryptospace):
        await checkPerms(req, cryptospace)

    @blp.fxroute(
        endpoint="/cryptospaces/<cryptospace>:checkProjectPermissions:<service_account>",
        method="POST",
        description="Checks a specific project has all of the specified permissions in the specified Crypto Space.",
        schema=google_cloud_ekms_v0_CheckCryptoSpacePermissionsRequest,
        resp_schemas={
            200: google_cloud_ekms_v0_CheckCryptoSpacePermissionsResponse,
        },
        schema_error_handler=bad_ekms_request)
    @gapi_login_required()
    async def checkProjectPerms(req, cryptospace, serviceAccount):
        await checkPerms(req, cryptospace, serviceAccount)

def define_get_key(blp):
    @blp.fxroute(
        endpoint="/keys/<key>:getPublicKey",
        method="POST",
        description="Retrieve public component of existing keypair",
        schema=google_cloud_ekms_v0_GetPublicKeyRequest,
        resp_schemas={
            200: google_cloud_ekms_v0_GetPublicKeyResponse,
        },
        schema_error_handler=bad_ekms_request)
    @gapi_login_required()
    async def getPublicKey(req, key):
        try:
            if DEBUG:
                print("GET PUBLIC KEY")
                print(AuthSession.auth_token())
                print("KEY: " + key)
                print(request.get_data().decode('utf-8'))
                print("")

            # To protobuf
            wrapper = fxGetPublicKey()
            req_to_proto(req, wrapper.gapi)
            # Put inside our wrapper
            wrapper.request_uri =  request.base_url
            wrapper.key_uuid = key
            # Forward to microservice
            rsp = await GekmsIfx.send(wrapper, GetPublicKeyResponse)
            # From protobuf
            data = proto_to_dict(rsp)
            gapi_respond(200, data)
        except IpcError as e:
            return format_ipc_error(GetPublicKeyRequest, e)

def define_sign(blp):
    @blp.fxroute(
        endpoint="/keys/<key>:asymmetricSign",
        method="POST",
        description="Generate signature using private key",
        schema=google_cloud_ekms_v0_AsymmetricSignRequest,
        resp_schemas={
            200: google_cloud_ekms_v0_AsymmetricSignResponse,
        },
        schema_error_handler=bad_ekms_request)
    @gapi_login_required()
    async def sign(req, key):
        try:
            if DEBUG:
                print("SIGN")
                print(AuthSession.auth_token())
                print("KEY: " + key)
                print(request.get_data().decode('utf-8'))
                print("")

            # To protobuf
            wrapper = fxAsymmetricSign()
            req_to_proto(req, wrapper.gapi)
            # Put inside our wrapper
            wrapper.request_uri =  request.base_url
            wrapper.key_uuid = key
            # Forward to microservice
            rsp = await GekmsIfx.send(wrapper, AsymmetricSignResponse)
            # From protobuf
            data = proto_to_dict(rsp)
            gapi_respond(200, data)
        except IpcError as e:
            return format_ipc_error(AsymmetricSignRequest, e)

def define_wrap(blp):
    @blp.fxroute(
        endpoint="/keys/<key>:wrap",
        method="POST",
        description="Wrap data / key material with authenticated encryption",
        schema=google_cloud_ekms_v0_WrapRequest,
        resp_schemas={
            200: google_cloud_ekms_v0_WrapResponse,
        },
        schema_error_handler=bad_ekms_request)
    @gapi_login_required()
    async def wrap(req, key):
        try:
            if DEBUG:
                print("WRAP")
                print(AuthSession.auth_token())
                print("KEY: " + key)
                print(request.get_data().decode('utf-8'))
                print("")

            # To protobuf
            wrapper = fxSymmetricWrap()
            req_to_proto(req, wrapper.gapi)
            # Put inside our wrapper
            wrapper.request_uri =  request.base_url
            wrapper.key_uuid = key
            # Forward to microservice
            rsp = await GekmsIfx.send(wrapper, WrapResponse)
            # From protobuf
            data = proto_to_dict(rsp)
            gapi_respond(200, data)
        except IpcError as e:
            return format_ipc_error(WrapRequest, e)

def define_unwrap(blp):
    @blp.fxroute(
        endpoint="/keys/<key>:unwrap",
        method="POST",
        description="Unwrap data / key material with authenticated encryption",
        schema=google_cloud_ekms_v0_UnwrapRequest,
        resp_schemas={
            200: google_cloud_ekms_v0_UnwrapResponse,
        },
        schema_error_handler=bad_ekms_request)
    @gapi_login_required()
    async def unwrap(req, key):
        try:
            if DEBUG:
                print("UNWRAP")
                print(AuthSession.auth_token())
                print("KEY: " + key)
                print(request.get_data().decode('utf-8'))
                print("")

            # To protobuf
            wrapper = fxSymmetricUnwrap()
            req_to_proto(req, wrapper.gapi)
            # Put inside our wrapper
            wrapper.request_uri =  request.base_url
            wrapper.key_uuid = key
            # Forward to microservice
            rsp = await GekmsIfx.send(wrapper, UnwrapResponse)
            # From protobuf
            data = proto_to_dict(rsp)
            gapi_respond(200, data)
        except IpcError as e:
            return format_ipc_error(UnwrapRequest, e)

def define_get_info(blp):
    @blp.fxroute(
        endpoint="/info",
        method="GET",
        description="""Retrieve information about this service.

This is aliased to /.well-known/external-key-manager/""",
        resp_schemas={
            200: google_cloud_ekms_v0_GetInfoResponse,
        },
        schema_error_handler=bad_ekms_request)
    @gapi_login_required()
    async def getInfo():
        try:
            if DEBUG:
                print("GET INFO")
                print(AuthSession.auth_token())

            req = GetInfo()
            req.request_uri =  request.base_url
            # Forward to microservice
            rsp = await GekmsIfx.send(req, GetInfoResponse)
            data = proto_to_dict(rsp)
            gapi_respond(200, data)
        except IpcError as e:
            return format_ipc_error(None, e)
