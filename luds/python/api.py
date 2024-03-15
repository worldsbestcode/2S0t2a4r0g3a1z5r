from rkweb.api import BaseApi

from mini import MiniBlueprintV1
from licenses import LicensesBlueprintV1
from licensing import LicensingBlueprintV1

class LudsApi(BaseApi):
    def __init__(self, app):
        super().__init__(app=app)

    def get_api_name(self) -> str:
        return "luds"

    def register_routes(self):
        self.add_blueprint(MiniBlueprintV1(), (1, None))
        self.add_blueprint(LicensesBlueprintV1(), (1, None))
        self.add_blueprint(LicensingBlueprintV1(), (1, None))
