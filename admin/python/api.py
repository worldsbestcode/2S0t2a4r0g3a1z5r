from rkweb.api import BaseApi

from notifications import NotificationsBlueprintV1
from major_keys import MajorKeysBlueprintV1
from status import StatusBlueprintV1
from networking import NetworkingBlueprintV1
from date_time import DateTimeBlueprintV1
from peer import PeerBlueprintV1
from default_login import DefaultLoginBlueprintV1
from remote_drives import RemoteDrivesBlueprintV1

class AdminApi(BaseApi):
    def __init__(self, app):
        super().__init__(app=app)

    def get_api_name(self) -> str:
        return "admin"

    def register_routes(self):
        self.add_blueprint(NotificationsBlueprintV1(), (1, None))
        self.add_blueprint(MajorKeysBlueprintV1(), (1, None))
        self.add_blueprint(StatusBlueprintV1(), (1, None))
        self.add_blueprint(NetworkingBlueprintV1(), (1, None))
        self.add_blueprint(DateTimeBlueprintV1(), (1, None))
        self.add_blueprint(PeerBlueprintV1(), (1, None))
        self.add_blueprint(DefaultLoginBlueprintV1(), (1, None))
        self.add_blueprint(RemoteDrivesBlueprintV1(), (1, None))
