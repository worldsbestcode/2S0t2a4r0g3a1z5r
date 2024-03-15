from rkweb.app import BaseApp

from api import LudsApi

from flask import jsonify

class App(BaseApp):
    def __init__(self):
        super().__init__(
            app_name=__name__,
            api_name="luds",
            api_title="Licensing and Update Distribution System",
            api_version=1,
            api_class=LudsApi
        )
