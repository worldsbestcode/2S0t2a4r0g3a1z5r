from rkweb.api import BaseApi

from idp import IdpBlueprintV1
from otp import OtpBlueprintV1
from fido import FidoBlueprintV1
from managed_roles import ManagedRolesBlueprintV1

class IamApi(BaseApi):
    def __init__(self, app):
        super().__init__(app=app)

    def get_api_name(self) -> str:
        return "iam"

    def register_routes(self):
        self.add_blueprint(IdpBlueprintV1(), (1, None))
        self.add_blueprint(OtpBlueprintV1(), (1, None))
        self.add_blueprint(FidoBlueprintV1(), (1, None))
        self.add_blueprint(ManagedRolesBlueprintV1(), (1, None))
