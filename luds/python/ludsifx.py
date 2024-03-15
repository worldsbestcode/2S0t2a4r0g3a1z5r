from rkweb.ipc import IpcUtils
from rkweb.session import AuthSession

class LudsIfx(object):
    @staticmethod
    async def send(msg, rsp_type = None):
        return await IpcUtils.send(port=5033, msg=msg, resp_type=rsp_type, auth_token=AuthSession.auth_token())
