from rkweb.app import BaseApp

from api import DesktopApi

class App(BaseApp):
    def __init__(self):
        super().__init__(app_name=__name__, api_name="rd", api_title="Futurex Remote Desktop", api_version=1, api_class=DesktopApi)

