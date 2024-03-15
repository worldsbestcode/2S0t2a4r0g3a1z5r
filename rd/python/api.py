from rkweb.api import BaseApi

from desktop import DesktopBlueprint
from files import FilesBlueprint
from fido import FidoBlueprint

class DesktopApi(BaseApi):
    def __init__(self, app):
        super().__init__(app=app)

    def get_api_name(self) -> str:
        return "rd"

    def register_routes(self):
        self.add_blueprint(DesktopBlueprint())
        self.add_blueprint(FilesBlueprint())
        self.add_blueprint(FidoBlueprint())
