from rkweb.app import BaseApp

from api import GcseApi

from flask import jsonify

class App(BaseApp):
    def __init__(self):
        super().__init__(
            app_name=__name__,
            api_name="gcse",
            api_title="Google Client Side Encryption",
            api_version=1,
            api_class=GcseApi
        )

        # Custom Google CSE 404
        @self.errorhandler(404)
        def custom_404(error):
            response = {
                'code': 5, # NOT_FOUND
                'message': 'Not found',
            }
            return jsonify(response), 404
