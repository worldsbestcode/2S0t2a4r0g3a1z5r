#!/usr/bin/env python3

import zmq
import zmq.asyncio

# protobuf imports
from rkproto.comm.RequestMessage_pb2 import RequestMessage
from rkproto.comm.ResponseMessage_pb2 import ResponseMessage
from rkproto.comm.ResponseMessage_pb2 import ResponseCode as RC

from google.protobuf import json_format

from rkweb.session import AuthSession
from rkweb.flaskutils import abort, respond

zmq_context = zmq.asyncio.Context()

class IpcError(RuntimeError):
    """
    Raised when a service responds with an error.

    code: rkproto.comm.ResponseMessage_pb2_ResponseCode.Code
    field: Programmatic friendly string to narrow down the error case
    msg: Human friendly error description
    """
    def __init__(self, code, field, msg):
        super().__init__(msg)
        self.code = code
        self.field = field
        self.msg = msg

class IpcUtils(object):
    @staticmethod
    def __localhost():
        """ Retrieve the IP to use for ZMQ TCP/IPC """
        return "127.0.0.1"

    @staticmethod
    def __new_conn(port, verbose = False):
        """ Open new connection to service """

        ip = IpcUtils.__localhost()
        # Open ZMQ connection
        socket = zmq_context.socket(zmq.REQ)
        dest = "tcp://{}:{}".format(ip, port)
        if verbose:
            print("Connecting to {}.".format(dest))
        socket.connect(dest)
        return socket

    @staticmethod
    async def send(port, msg, resp_type = None, auth_token = None, verbose = False, timeout = 5 * 1000):
        """
        Send a protobuf object to a microservice

        Args:
            port: The microservice API port
            msg: The request object (input)
            resp_type: The response object class type
            auth_token: The authorization token to use
            verbose: True=Print traffic
        Returns:
            Response type
        """

        # Wrap in request message envelope
        envelope = RequestMessage()
        if auth_token:
            envelope.auth_token = auth_token
        envelope.params.Pack(msg, "fx/")

        # Serialize to JSON
        data = json_format.MessageToJson(envelope, including_default_value_fields=True)
        # Send asynchronously
        json_response = await IpcUtils.send_json(port=port, data=data, verbose=verbose, timeout=timeout)

        # Deserialize response
        response = ResponseMessage()
        json_format.Parse(json_response, response)
        # Check success
        if not response.success:
            # Log any IPC errors
            print("IPC error (Port: {}, Code: {}, Field: {}): {}".format(port, response.error_code, response.error_field, response.error_string))
            # Auth token expired or no longer valid for some other reason
            if response.error_code == RC.InvalidAuthToken:
                # Force a logout
                print("Forcing logout on invalid authorization token error.")
                AuthSession.logout()
                abort(401, "Authorization token expired")
            raise IpcError(response.error_code, response.error_field, response.error_string)

        # Deserialize message specific response object
        if resp_type:
            resp_obj = resp_type()
            response.params.Unpack(resp_obj)
            return resp_obj
        return None

    @staticmethod
    async def send_json(port, data, verbose = False, timeout = 5000):
        """ Send string data to a microservice synchronously """

        socket = IpcUtils.__new_conn(port=port, verbose=verbose)
        if verbose:
            print("Sending: {}".format(data))

        # Send poll (Static 1s timeout)
        poller = zmq.asyncio.Poller()
        poller.register(socket, zmq.POLLOUT)
        if not await poller.poll(timeout=1000):
            raise IpcError(RC.IpcError, "pysend", "Failed to send IPC request from web service.")
        await socket.send_string(data)

        # Recv poll (default 5s timeout)
        poller.unregister(socket)
        poller.register(socket, zmq.POLLIN)
        if not await poller.poll(timeout=timeout):
            raise IpcError(RC.Timeout, "pyrecv", "Timeout waiting for IPC response to web service.")
        response_data = await socket.recv_string()

        if verbose:
            print("Received: {}".format(response_data))
        return response_data

def handle_ipc_error(error):
    # Default is internal error if we don't know how to categorize the error
    code = 500 # INTERNAL ERROR

    if error.code in [
            RC.NotLoggedIn,
            RC.InvalidAuthToken,
            RC.AuthFailure]:
        code = 401 # UNAUTHORIZED
    elif error.code in [
            RC.NotAuthorized]:
        code = 403 # FORBIDDEN
    elif error.code in [
            RC.ArgumentMissing,
            RC.ArgumentParseError,
            RC.ArgumentInvalid,
            RC.InvalidSelection]:
        code = 400 # BAD REQUEST
    elif error.code in [
            RC.AlreadyExists,
            RC.OperationInProgress,
            RC.NoOperationInProgress,
            RC.AlreadyConnected]:
        code = 409 # CONFLICT
    elif error.code in [
            RC.OperationAborted]:
        code = 410 # GONE
    elif error.code in [
            RC.UnknownCommand,
            RC.NotFound]:
        code = 404 # NOT FOUND
    elif error.code in [
            RC.NotSupported]:
        code = 405 # METHOD NOT ALLOWED
    elif error.code in [
            RC.Timeout]:
        code = 408 # REQUEST TIMEOUT
    elif error.code in [
            RC.Unknown]:
        code = 418 # I'M A TEAPOT
    elif error.code in [
            RC.InternalError,
            RC.Unspecified]:
        code = 500 # INTERNAL ERROR
    elif error.code in [
            RC.ServiceDisabled]:
        code = 503 # SERVICE UNAVAILABLE
    elif error.code in [
            RC.CommandError,
            RC.CommunicationError,
            RC.DeviceError,
            RC.IpcError,
            RC.NotConnected,
            RC.Tls,
            RC.FileError,
            RC.DatabaseError]:
        code = 502 # BAD GATEWAY

    # Response JSON
    data = {}
    data['status'] = "Failure"
    data['message'] = error.msg
    data['code'] = error.code
    data['type'] = RC.Code.Name(error.code)
    if error.field and len(error.field) > 0:
        data['field'] = error.field

    from flask import jsonify
    ret = jsonify(data)
    ret.status_code = code
    return ret

