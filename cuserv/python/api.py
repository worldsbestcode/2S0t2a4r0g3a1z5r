from rkweb.api import BaseApi

from templates import ServiceTemplatesBlueprintV1
from services import DeployedServicesBlueprint
from users import UsersBlueprintV1
from auditlogs import AuditLogsBlueprintV1
from clientapp import ClientAppBlueprintV1

class CustomServicesApi(BaseApi):
    def __init__(self, app):
        super().__init__(app=app)

    def get_api_name(self) -> str:
        return "cuserv"

    def register_routes(self):
        self.add_blueprint(DeployedServicesBlueprint())
        self.add_blueprint(ServiceTemplatesBlueprintV1(), (1, None))
        self.add_blueprint(UsersBlueprintV1(), (1, None))
        self.add_blueprint(AuditLogsBlueprintV1(), (1, None))
        self.add_blueprint(ClientAppBlueprintV1(), (1, None))
