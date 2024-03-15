from rkweb.object_manager import ObjectManager

from rkproto.admin.AdminNotification_pb2 import AdminNotification, AdminNotification_Stub

class AdminNotificationManager(ObjectManager):
    def __init__(self):
        super().__init__(5090, AdminNotification, AdminNotification_Stub)
