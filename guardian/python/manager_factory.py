from object_manager import ObjectManager
from session import UserSession

class ManagerFactory(object):
    @staticmethod
    def guardian():
        return ObjectManager(24518, UserSession.auth_token())

