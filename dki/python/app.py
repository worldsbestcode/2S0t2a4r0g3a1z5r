from rkweb.app import BaseApp

from api import InjectApi

class App(BaseApp):
    def __init__(self):
        super().__init__(app_name=__name__, api_name="dki", api_title="Futurex Direct Key Injection", api_version=1, api_class=InjectApi)
