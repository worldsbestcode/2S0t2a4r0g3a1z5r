from rkweb.app import BaseApp

from api import CustomServicesApi

class App(BaseApp):
    def __init__(self):
        super().__init__(app_name=__name__, api_name="cuserv", api_title="Custom Services Manager", api_version=1, api_class=CustomServicesApi)
