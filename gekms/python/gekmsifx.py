from rkweb.ipc import IpcUtils
from rkweb.session import AuthSession

class GekmsIfx(object):
    @staticmethod
    async def send(msg, rsp_type = None):
        return await IpcUtils.send(port=5073, msg=msg, resp_type=rsp_type, auth_token=AuthSession.auth_token())
