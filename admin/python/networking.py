from rkweb.auth import perm_required
from rkweb.flaskutils import Blueprint, respond
from rkweb.protoflask import args_to_proto, proto_to_dict
from rkweb.rkserver import ServerConn, ExcryptMsg
from rkweb.lilmodels.base import Model, field
from typing import List

from mm_rkproto.networking.NetworkConfig import rkproto_networking_NetworkConfig

from rkproto.networking.NetworkConfig_pb2 import GetNetworkConfig, NetworkConfig

from networkingifx import NetworkingIfx

import json
from google.protobuf import json_format

# Blueprint
def NetworkingBlueprintV1():
    blp = Blueprint("Networking", "networking", url_prefix="/networking", description="Get/Set Network Config")
    define_get(blp)
    define_set(blp)
    define_vrrp_devices(blp)
    return blp

def define_get(blp):
    @blp.fxroute(
        endpoint="",
        method="GET",
        description="Get networking configuration",
        resp_schemas={
            200: rkproto_networking_NetworkConfig,
        })
    @perm_required("System:Administration")
    async def getNetworkConfig():
        # Forward to microservice
        msg = GetNetworkConfig()
        rsp = await NetworkingIfx.send(msg, NetworkConfig)

        # Convert to dictionary
        data = proto_to_dict(rsp)
        respond(200, data)

def define_set(blp):
    @blp.fxroute(
        endpoint="",
        method="POST",
        description="Set networking configuration",
        schema=rkproto_networking_NetworkConfig)
    @perm_required("System:Administration")
    async def setNetworkConfig(req):
        # To protobuf
        msg = args_to_proto(req, NetworkConfig)

        # Forward to microservice
        await NetworkingIfx.send(msg, None)
        respond(200)

def define_vrrp_devices(blp):
    class VrrpDevice(Model):
        group: str = field(description="Balanced device group name")
        address: str = field(description="Device address")
        uuid: str = field(description="Device UUID")

    class VrrpDevices(Model):
        devices: List[str] = field(description="Possible devices to use for VRRP status check")

    @blp.fxroute(
        endpoint="/vrrp-devices",
        method="GET",
        description="Get possible VRRP devices",
        resp_schemas={
            200: VrrpDevices,
        })
    @perm_required("System:Administration")
    async def getVrrpDevices():

        server = ServerConn()
        msg = ExcryptMsg("[AOGDLB;]")
        msg.set_tag("OP", "list")
        msg.set_tag("JW", "System")
        rsp = await server.send_excrypt(msg)
        group_names = rsp.get_tag("NA").split(",")
        group_uuids = rsp.get_tag("ID").split(",")

        data = {'devices': []}
        for i in range(len(group_uuids)):
            group_name = group_names[i]
            group_uuid = group_uuids[i]

            msg = ExcryptMsg("[AOGDBD;]")
            msg.set_tag("OP", "list")
            msg.set_tag("JW", "System")
            msg.set_tag("ID", group_uuid)
            rsp = await server.send_excrypt(msg)
            device_names = rsp.get_tag("NA").split(",")
            device_uuids = rsp.get_tag("ID").split(",")
            for j in range(len(device_uuids)):
                device_name = device_names[i]
                device_uuid = device_uuids[i]
                data['devices'].append({
                    'group': group_name,
                    'address': device_name,
                    'uuid': device_uuid,
                })

        respond(200, data)
