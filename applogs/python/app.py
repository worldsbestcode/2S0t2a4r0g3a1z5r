from rkweb.app import BaseApp

from api import AppLogsApi

class App(BaseApp):
    def __init__(self):
        super().__init__(app_name=__name__, api_name="applogs", api_title="Futurex Application Logs", api_version=1, api_class=AppLogsApi)
