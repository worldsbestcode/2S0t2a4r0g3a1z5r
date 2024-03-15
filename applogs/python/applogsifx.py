from rkweb.ipc import IpcUtils
from rkweb.session import AuthSession

class ApplogsIfx(object):
    @staticmethod
    async def send(msg, rsp_type):
        return await IpcUtils.send(port=5060, msg=msg, resp_type=rsp_type, auth_token=AuthSession.auth_token(), timeout=10 * 60 * 1000)
