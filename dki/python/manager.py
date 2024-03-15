# @file      injection_log_manager.py
# @author    Dante Ruiz (druiz@futurex.com)
#
# @section LICENSE
#
# This program is the property of Futurex, LP.
#
# No disclosure, reproduction, or use of any part thereof may be made without
# express written permission of Futurex, LP.
#
# Copyright by:  Futurex, LP. 2023

from rkweb.object_manager import ObjectManager

from rkproto.dki.InjectionLog_pb2 import InjectionLog, InjectionLog_Stub
from rkproto.cuserv.CustomService_pb2 import CustomService, CustomService_Stub
from rkproto.cuserv.ServiceTemplate_pb2 import ServiceTemplate, ServiceTemplate_Stub
from rkproto.dki.Session_pb2 import Session, Session_Stub
from rkproto.dki.KeySlotReference_pb2 import KeySlotReference, KeySlotReference_Stub

from inject_session import InjectSession


class InjectionLogManager(ObjectManager):
    def __init__(self):
        super().__init__(InjectSession.port, InjectionLog, InjectionLog_Stub)


class ServiceManager(ObjectManager):
    def __init__(self):
        super().__init__(5055, CustomService, CustomService_Stub)


class TemplateManager(ObjectManager):
    def __init__(self):
        super().__init__(5055, ServiceTemplate, ServiceTemplate_Stub)


class SessionManager(ObjectManager):
    def __init__(self):
        super().__init__(InjectSession.port, Session, Session_Stub)


class KeySlotReferenceManager(ObjectManager):
    def __init__(self):
        super().__init__(InjectSession.port, KeySlotReference, KeySlotReference_Stub)
