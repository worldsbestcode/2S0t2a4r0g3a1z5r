from rkweb.object_manager import ObjectManager

from rkproto.gekms.CryptoSpace_pb2 import CryptoSpace, CryptoSpace_Stub
from rkproto.gekms.Key_pb2 import Key, Key_Stub

class CryptoSpaceManager(ObjectManager):
    def __init__(self):
        super().__init__(5070, CryptoSpace, CryptoSpace_Stub)

class KeyManager(ObjectManager):
    def __init__(self):
        super().__init__(5070, Key, Key_Stub)
