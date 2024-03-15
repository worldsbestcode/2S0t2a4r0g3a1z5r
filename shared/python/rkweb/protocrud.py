from functools import partial

from typing import List

import json
from marshmallow import fields
from google.protobuf import json_format

from rkweb.lilmodels.base import Model, field
from rkweb.lilmodels.page import PagedRequestModel, PagedResponseModel

from rkweb.ipc import IpcUtils
from rkweb.auth import login_required, perm_required
from rkweb.session import AuthSession
from rkweb.flaskutils import Blueprint, respond
from rkweb.protoflask import serialize_filter_results, load_paging

from rkweb.object_manager import ObjectManager

from rkproto.mo.PermChange_pb2 import PermChange
from rkproto.mo.ObjectInfo_pb2 import PermEntry as PermEntry_pb
from rkproto.mo.ObjectFilter_pb2 import ObjectFilter

class CreateResponse(Model):
    uuid: str = field(description="UUID of the new object")

class PermEntry(Model):
    roleUuid: str = field(description="UUID of the role to modify permission")
    perms: int = field(description="""Permission bit flags

View: 0x01
Use: 0x02
Modify: 0x04
Delete: 0x08
Add: 0x10
Owner: 0x20
""")

class PermissionChange(Model):
    permissions: List[PermEntry] = field(description="Permission changes")

# Instantiate this to register CRUD operations for a protobuf-based object
class ProtoCrud(object):
    def __init__(
        self,
        name: str, # "custom service category"
        blp: Blueprint, # Blueprint
        port: int, # Object microservice port
        proto_class, # ServiceCategory
        proto_stub_class, # ServiceCategory_Stub
        mmproto_get, # rkproto_cuserv_ServiceCategory_GET
        mmproto_stub, # rkproto_cuserv_ServiceCategory_GET
        mmproto_add, # rkproto_cuserv_ServiceCategory_ADD
        mmproto_modify, # rkproto_cuserv_ServiceCategory_MODIFY
        perm_category: str, # "Custom Services"
        manage_perm: str = None, # "Manage" (None=Use 'Add/Modify/Delete')
        delete = True, # Add delete endpoint?
        prefix = "", # API prefix?
        proto_preparse = None, # Preparse function
        proto_postserialize = None, # Post serialize function
        ):

        # Save config
        self.port = port
        self.proto_class = proto_class
        self.proto_stub_class = proto_stub_class
        self.perm_category = perm_category
        self.manage_perm = manage_perm
        self.proto_type = proto_class.DESCRIPTOR.full_name
        self.proto_preparse = proto_preparse
        self.proto_postserialize = proto_postserialize

        # GET
        if mmproto_get:
            blp.fxroute(
                endpoint=prefix + "/<uuid>",
                method="GET",
                description="Retrieve a " + name,
                resp_schemas={
                    200: mmproto_get,
                },
            )(partial(ProtoCrud.get, self))

        # GET Stubs
        if mmproto_stub:
            class StubsResponse(PagedResponseModel):
                results: list = field(
                    description="The page of results",
                    marshmallow_field=fields.List(
                        fields.Nested(mmproto_stub)
                    )
                )

            blp.fxroute(
                endpoint=prefix + "/stubs",
                method="GET",
                description="Retrieve a page of " + name + " stubs",
                schema=PagedRequestModel,
                location='query',
                resp_schemas={
                    200: StubsResponse,
                },
            )(partial(ProtoCrud.getStubs, self))

        # ADD
        if mmproto_add:
            blp.fxroute(
                endpoint=prefix,
                method="POST",
                description="Create a new " + name,
                schema=mmproto_add,
                resp_schemas={
                    200: CreateResponse,
                },
            )(partial(ProtoCrud.post, self))

        # MODIDFY
        if mmproto_modify:
            blp.fxroute(
                endpoint=prefix + "/<uuid>",
                method="PATCH",
                description="Modify a " + name,
                schema=mmproto_modify,
            )(partial(ProtoCrud.patch, self))

        # DELETE
        if delete:
            blp.fxroute(
                endpoint=prefix + "/<uuid>",
                method="DELETE",
                description="Delete a " + name,
            )(partial(ProtoCrud.delete, self))

        # PERMISSIONS
        if perm_category:
            blp.fxroute(
                endpoint=prefix + "/permissions/<uuid>",
                method="PATCH",
                description="Modify permissions for a " + name,
                schema=PermissionChange,
            )(partial(ProtoCrud.perms, self))

    def manager(self) -> ObjectManager:
        return ObjectManager(self.port, self.proto_class, self.proto_stub_class)

    async def check_perm(perm: str) -> None:
        async def nada():
            ...
        await perm_required(perm)(nada)()

    async def check_subperm(self, subperm: str) -> None:
        if self.perm_category:
            if self.manage_perm:
                await ProtoCrud.check_perm(self.perm_category + ":" + self.manage_perm)
            else:
                await ProtoCrud.check_perm(self.perm_category + ":" + subperm)
        else:
            await self.check_login()

    async def check_login(self) -> None:
        async def nada():
            ...
        await login_required()(nada)()

    async def get(self, uuid: str) -> None:
        await self.check_login()

        # Get result
        obj = await self.manager().select(uuid)

        # Convert to dictionary
        data = json.loads(json_format.MessageToJson(obj, including_default_value_fields=True))
        if self.proto_postserialize:
            self.proto_postserialize(data)

        respond(200, data)

    async def getStubs(self, args) -> None:
        await self.check_login()

        # Build filter
        obj_filter = ObjectFilter()
        obj_filter.object_type = self.proto_type
        obj_filter.sort_attribute = 'name'
        obj_filter.ascending = True
        obj_filter.stubs = True
        load_paging(args, obj_filter)

        # Filter
        (pagination, objs) = await self.manager().filter(obj_filter)

        # Respond
        respond(200, serialize_filter_results(pagination, objs))

    async def post(self, data: dict) -> None:
        await self.check_subperm("Add")

        # 'name' needs to be moved into the ObjectInfo part of the data model
        if 'name' in data:
            data['obj_info'] = {
                'name': data['name']
            }
            data.pop('name')

        # Convert to protobuf
        proto_obj = self.proto_class()
        if self.proto_preparse:
            self.proto_preparse(data)
        json_format.Parse(json.dumps(data), proto_obj)

        # Save
        uuid = await self.manager().add(proto_obj)

        respond(200, {'uuid': uuid})

    async def patch(self, data: dict, uuid: str) -> None:
        await self.check_subperm("Modify")

        # The field mask tells the microservice which fields to update
        field_mask = []

        # Set uuid in the ObjectInfo
        obj_info = {
            'uuid': uuid
        }
        # 'name' needs to be moved into the ObjectInfo part of the data model
        if 'name' in data:
            obj_info['name'] = data['name']
            data.pop('name')
            field_mask.append("objInfo.name")

        # Insert into the field mask every attribute that was provided
        def mask_fields(path, sub_data):

            def indexes(dict_or_list):
                if type(dict_or_list) is dict:
                    return dict_or_list.keys()
                return range(len(dict_or_list))

            for key in indexes(sub_data):
                if type(sub_data) is not list:
                    path.append(key)
                    field_mask.append('.'.join(path))
                    field_mask.append(key)
                if type(sub_data[key]) is dict or type(sub_data[key]) is list:
                    mask_fields(path, sub_data[key])
                if type(sub_data) is not list:
                    path.pop()
        mask_fields([], data)

        # Put the object info and field mask in place
        data['objInfo'] = obj_info
        data['fieldMask'] = ','.join(field_mask)

        # Convert to protobuf
        proto_obj = self.proto_class()
        if self.proto_preparse:
            self.proto_preparse(data)
        json_format.Parse(json.dumps(data), proto_obj)

        # Save
        await self.manager().modify(proto_obj)

        respond(200)

    async def delete(self, uuid: str) -> None:
        await self.check_subperm("Delete")
        await self.manager().remove(uuid)
        respond(200)


    async def perms(self, data: dict, uuid: str) -> None:
        # Check class perms
        await self.check_subperm("Modify")

        # Build request
        msg = PermChange()
        msg.obj_uuid = uuid
        for change in data['permissions']:
            entry = PermEntry_pb()
            entry.role = change['roleUuid']
            entry.perm_level = int(change['perms'])
            msg.perm_changes.append(entry)

        # Process request
        await IpcUtils.send(port=self.port, msg=msg, resp_type=None, auth_token=AuthSession.auth_token())
        respond(200)
