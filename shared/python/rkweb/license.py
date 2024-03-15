from functools import wraps

from rkweb.ipc import IpcUtils
from rkweb.session import AuthSession
from rkweb.flaskutils import unauthorized

from rkproto.luds.RetrieveLicenses_pb2 import RetrieveLicenses, RetrieveLicensesResponse

class LudsIfx(object):
    @staticmethod
    async def send(msg, rsp_type = None):
        return await IpcUtils.send(port=5033, msg=msg, resp_type=rsp_type, auth_token=AuthSession.auth_token())

async def is_licensed():
    rsp = await LudsIfx().send(RetrieveLicenses(), RetrieveLicensesResponse)
    return rsp.valid

async def get_licenses(license_type):
    rsp = await LudsIfx().send(RetrieveLicenses(), RetrieveLicensesResponse)

    count = 0
    for lic in rsp.licenses:
        if lic.valid and lic.type == license_type:
            count += lic.count
    for lic in rsp.used:
        if lic.type == license_type:
            count -= lic.count

    return count if count > 0 else 0

def check_licensed():
    def wrapper(func):
        @wraps(func)
        async def license_check(*args, **kwargs):
            valid = await is_licensed()
            if not valid:
                unauthorized("Server is not licensed.")
            return await func(*args, **kwargs)
        return license_check
    return wrapper
