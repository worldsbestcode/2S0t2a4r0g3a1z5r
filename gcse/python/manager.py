from rkweb.object_manager import ObjectManager

from rkproto.gcse.User_pb2 import User, User_Stub

class UserManager(ObjectManager):
    def __init__(self):
        super().__init__(5080, User, User_Stub)
