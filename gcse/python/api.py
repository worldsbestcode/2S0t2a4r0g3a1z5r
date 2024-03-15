from rkweb.api import BaseApi

from users import UsersBlueprintV1
from keys import KeysBlueprintV1

class GcseApi(BaseApi):
    def __init__(self, app):
        super().__init__(app=app)

    def get_api_name(self) -> str:
        return "gcse"

    def register_routes(self):
        self.add_blueprint(UsersBlueprintV1(), (1, None))
        self.add_blueprint(KeysBlueprintV1(), (1, None))
