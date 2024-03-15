from rkweb.app import BaseApp

from api import HomeApi

class App(BaseApp):
    def __init__(self):
        super().__init__(app_name=__name__, api_name="home", api_title="CryptoHub Dashboard", api_version=1, api_class=HomeApi)

