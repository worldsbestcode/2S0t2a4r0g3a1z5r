from rkweb.api import BaseApi

from session import SessionBlueprint
from inject import InjectBlueprint
from slots import SlotsBlueprint
from logs import LogsBlueprint
from keys import KeysBlueprint
from device import DeviceBlueprint
from printer import PrinterBlueprint
from key_slots import KeySlotsBlueprint
from hosts import HostsBlueprint


class InjectApi(BaseApi):
    def __init__(self, app):
        super().__init__(app=app)

    def get_api_name(self) -> str:
        return "dki"

    def register_routes(self):
        self.add_blueprint(SessionBlueprint())
        self.add_blueprint(SlotsBlueprint())
        self.add_blueprint(InjectBlueprint())
        self.add_blueprint(LogsBlueprint())
        self.add_blueprint(KeysBlueprint())
        self.add_blueprint(DeviceBlueprint())
        self.add_blueprint(PrinterBlueprint())
        self.add_blueprint(KeySlotsBlueprint())
        self.add_blueprint(HostsBlueprint())
