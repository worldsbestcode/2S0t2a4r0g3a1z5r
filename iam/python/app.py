from rkweb.app import BaseApp

from api import IamApi

class App(BaseApp):
    def __init__(self):
        super().__init__(
            app_name=__name__,
            api_name="iam",
            api_title="Identity & Access Management",
            api_version=1,
            api_class=IamApi
        )
