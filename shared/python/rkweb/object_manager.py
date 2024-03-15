#!/usr/bin/env python3

from rkweb.flaskutils import abort

from rkweb.ipc import IpcUtils
from rkweb.session import AuthSession

from rkproto.mo.ObjectChange_pb2 import ObjectChange, ObjectChangeResponse
from rkproto.mo.ObjectDelete_pb2 import ObjectDelete, ObjectDeleteResponse
from rkproto.mo.ObjectFilter_pb2 import ObjectFilter
from rkproto.mo.ObjectSelect_pb2 import ObjectSelect
from rkproto.mo.ObjectResults_pb2 import ObjectResults

class ObjectManager(object):
    def __init__(self, port, obj_type, stub_type):
        """
        Initialize the object manager

        Args:
            port: The object microservice port
            obj_type: The protobuf object class
            stub_type: The protobuf object stub class
        """
        self.port = port
        self.obj_type = obj_type
        self.stub_type = stub_type
        self.auth_token = AuthSession.auth_token()

    async def add(self, obj):
        """
        Add an object to the microservice

        Args:
            obj: The protobuf object
        Returns:
            Object UUID string
        """
        return await self.__do_add_modify(ObjectChange.Create, obj)

    async def modify(self, obj):
        """
        Modify an existing object in the microservice

        Args:
            obj: The protobuf object
        Returns:
            Object UUID string
        """
        return await self.__do_add_modify(ObjectChange.Update, obj)

    async def remove(self, uuid):
        """
        Removes an existing object from the microservice

        Args:
            uuid: The object UUID
        Returns:
            Object UUID string
        """
        msg = ObjectDelete()
        msg.uuid = uuid
        rsp = await IpcUtils.send(port=self.port, msg=msg, resp_type=ObjectDeleteResponse, auth_token=self.auth_token)
        return rsp.uuid

    async def select(self, uuid):
        """
        Select an existing object from the microservice by UUID

        Args:
            uuid: The object UUID
        Returns:
            Selected object
        """
        msg = ObjectSelect()
        msg.uuid.append(uuid)
        rsp = await IpcUtils.send(port=self.port, msg=msg, resp_type=ObjectResults, auth_token=self.auth_token)

        # Found?
        if rsp.pagination.total == 0:
            abort(404, "No object with uuid {}".format(uuid))

        selected_obj = self.obj_type()
        rsp.results[0].Unpack(selected_obj)
        return selected_obj

    async def filter(self, object_filter: ObjectFilter):
        """
        Select a list of objects by filter

        Args:
            object_filter: ObjectFilter instance
        Returns:
            Tuple (pagination, results dictionary)
        """
        rsp = await IpcUtils.send(port=self.port, msg=object_filter, resp_type=ObjectResults, auth_token=self.auth_token)

        objs = []
        for obj in rsp.results:
            new_obj = self.stub_type() if object_filter.stubs else self.obj_type()
            obj.Unpack(new_obj)
            objs.append(new_obj)

        return (rsp.pagination, objs)

    async def __do_add_modify(self, action, obj):
        msg = ObjectChange()
        msg.operation = action
        msg.obj.Pack(obj, "fx/")
        rsp = await IpcUtils.send(port=self.port, msg=msg, resp_type=ObjectChangeResponse, auth_token=self.auth_token)
        return rsp.uuid
