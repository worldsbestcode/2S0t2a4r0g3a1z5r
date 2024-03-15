from rkweb.api import BaseApi

from dashboard import DashboardBlueprint
from changepw import ChangePwBlueprint
from restart import RestartBlueprint
from status import StatusBlueprint
from info import InfoBlueprint
from hardware import HardwareBlueprint
from profiles import ProfileBlueprint

class HomeApi(BaseApi):
    def __init__(self, app):
        super().__init__(app=app)

    def get_api_name(self) -> str:
        return "home"

    def register_routes(self):
        self.add_blueprint(DashboardBlueprint())
        self.add_blueprint(ChangePwBlueprint())
        self.add_blueprint(RestartBlueprint())
        self.add_blueprint(StatusBlueprint())
        self.add_blueprint(InfoBlueprint())
        self.add_blueprint(HardwareBlueprint())
        self.add_blueprint(ProfileBlueprint())
