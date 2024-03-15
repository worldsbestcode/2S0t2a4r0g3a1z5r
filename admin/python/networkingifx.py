from rkweb.ipc import IpcUtils
from rkweb.session import AuthSession

class NetworkingIfx(object):
    @staticmethod
    async def send(msg, rsp_type = None):
        return await IpcUtils.send(port=5100, msg=msg, resp_type=rsp_type, auth_token=AuthSession.auth_token(), timeout=30 * 1000)
