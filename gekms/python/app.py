from rkweb.app import BaseApp

from api import GekmsApi

from flask import jsonify

class App(BaseApp):
    def __init__(self):
        super().__init__(
            app_name=__name__,
            api_name="gekms",
            api_title="Google External Key Manager",
            api_version=1,
            api_class=GekmsApi
        )

        # Custom Google EKM 404
        @self.errorhandler(404)
        def custom_404(error):
            response = {
                'code': 5, # NOT_FOUND
                'message': 'Not found',
            }
            return jsonify(response), 404
