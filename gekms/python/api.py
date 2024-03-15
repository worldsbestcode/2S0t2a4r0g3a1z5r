from rkweb.api import BaseApi

from gapi import GapiBlueprintV0
from keys import KeysBlueprintV1
from accounts import AccountsBlueprintV1
from cryptospaces import CryptoSpacesBlueprintV1

class GekmsApi(BaseApi):
    def __init__(self, app):
        super().__init__(app=app)

    def get_api_name(self) -> str:
        return "gekms"

    def register_routes(self):
        self.add_blueprint(GapiBlueprintV0(), "/gapi/v0")
        self.add_blueprint(KeysBlueprintV1(), (1, None))
        self.add_blueprint(AccountsBlueprintV1(), (1, None))
        self.add_blueprint(CryptoSpacesBlueprintV1(), (1, None))
