from rkweb.api import BaseApi

from logs import LogsBlueprint
from files import FilesBlueprint

class AppLogsApi(BaseApi):
    def __init__(self, app):
        super().__init__(app=app)

    def get_api_name(self) -> str:
        return "applogs"

    def register_routes(self):
        self.add_blueprint(LogsBlueprint())
        self.add_blueprint(FilesBlueprint())
