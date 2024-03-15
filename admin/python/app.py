from rkweb.app import BaseApp

from api import AdminApi

from flask import jsonify

class App(BaseApp):
    def __init__(self):
        super().__init__(
            app_name=__name__,
            api_name="admin",
            api_title="Administration",
            api_version=1,
            api_class=AdminApi
        )

        # Custom Admin 404
        @self.errorhandler(404)
        def custom_404(error):
            response = {
                'code': 5, # NOT_FOUND
                'message': 'Not found',
            }
            return jsonify(response), 404
