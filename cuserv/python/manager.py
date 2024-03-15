from rkweb.object_manager import ObjectManager

from rkproto.cuserv.ServiceTemplate_pb2 import ServiceTemplate, ServiceTemplate_Stub
from rkproto.cuserv.CustomService_pb2 import CustomService, CustomService_Stub
from rkproto.cuserv.Instructions_pb2 import Instructions, Instructions_Stub
from rkproto.cuserv.ClientAppEndpoint_pb2 import ClientAppEndpoint, ClientAppEndpoint_Stub

class TemplateManager(ObjectManager):
    def __init__(self):
        super().__init__(5055, ServiceTemplate, ServiceTemplate_Stub)

class InstructionsManager(ObjectManager):
    def __init__(self):
        super().__init__(5055, Instructions, Instructions_Stub)

class ServiceManager(ObjectManager):
    def __init__(self):
        super().__init__(5055, CustomService, CustomService_Stub)

class ClientAppEndpointManager(ObjectManager):
    def __init__(self):
        super().__init__(5055, ClientAppEndpoint, ClientAppEndpoint_Stub)
