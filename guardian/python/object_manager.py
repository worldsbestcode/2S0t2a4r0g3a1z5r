from ipc import IpcUtils

from rkproto.mo.ObjectChange_pb2 import ObjectChange, ObjectChangeResponse
from rkproto.mo.ObjectDelete_pb2 import ObjectDelete, ObjectDeleteResponse
from rkproto.mo.ObjectFilter_pb2 import ObjectFilter
from rkproto.mo.ObjectSelect_pb2 import ObjectSelect
from rkproto.mo.ObjectResults_pb2 import ObjectResults

class ObjectManager(object):
    def __init__(self, port, auth_token = None):
        self.port = port
        self.auth_token = auth_token

    async def add(self, obj, auth_token = None):
        """
        Add an object to the microservice

        Args:
            obj: The protobuf object
            auth_token: The latest authorization token to use
        Returns:
            Object UUID string
        """
        return await self.__do_add_modify(ObjectChange.Create, obj, auth_token)

    async def modify(self, obj, auth_token = None):
        """
        Modify an existing object in the microservice

        Args:
            obj: The protobuf object
            auth_token: The latest authorization token to use
        Returns:
            Object UUID string
        """
        return await self.__do_add_modify(ObjectChange.Update, obj, auth_token)

    async def remove(self, uuid, auth_token = None):
        """
        Removes an existing object from the microservice

        Args:
            uuid: The object UUID
            auth_token: The latest authorization token to use
        Returns:
            Object UUID string
        """
        if not auth_token:
            auth_token = self.auth_token

        msg = ObjectDelete()
        msg.uuid = uuid
        rsp = ObjectDeleteResponse()
        await IpcUtils.send(port=self.port, msg=msg, resp_obj=rsp, auth_token=auth_token)
        return rsp.uuid

    async def select(self, uuid, selected_obj, auth_token = None):
        """
        Select an existing object from the microservice by UUID

        Args:
            uuid: The object UUID
            selected_obj: Object to store the result into
            auth_token: The latest authorization token to use
        """
        if not auth_token:
            auth_token = self.auth_token

        msg = ObjectSelect()
        msg.uuid.append(uuid)
        rsp = ObjectResults()
        await IpcUtils.send(port=self.port, msg=msg, resp_obj=rsp, auth_token=auth_token)
        if rsp.total_results == 0:
            raise RuntimeError("No results.")
        rsp.results[0].Unpack(selected_obj)

    # TODO: Some way to output object types not Any
    async def filter(self, object_filter: ObjectFilter, auth_token = None):
        """
        Select a list of objects by filter

        Args:
            object_filter: ObjectFilter instance
            auth_token: The latest authorization token to use
        Returns:
            Tuple (total_results, results dictionary)
        """
        if not auth_token:
            auth_token = self.auth_token

        rsp = ObjectResults()
        await IpcUtils.send(port=self.port, msg=object_filter, resp_obj=rsp, auth_token=auth_token)
        return (rsp.total_results, rsp.results)

    async def __do_add_modify(self, action, obj, auth_token):
        if not auth_token:
            auth_token = self.auth_token

        msg = ObjectChange()
        msg.operation = action
        msg.obj.Pack(obj, "fx/")
        rsp = ObjectChangeResponse()
        await IpcUtils.send(port=self.port, msg=msg, resp_obj=rsp, auth_token=auth_token)
        return rsp.uuid

