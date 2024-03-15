from flask import request

from base.server_views import ServerTranslatedView
from lib.utils.response_generator import APIResponses
from lib.utils.view_router import Route

@Route()
class Roles(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "Roles")

    @Route.get("*")
    def get_list(self):
        response = self.translate("List", request.args)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.not_found(message=message)

    def post(self):
        request_data = request.get_json()
        response = self.translate("Create", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.not_found(message=message)

@Route()
class RoleResource(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "Roles")

    def delete(self, uuid):
        response = self.translate("Delete", {'uuid': uuid})

        status, message = response.get("status", "N"), response.get("message", "")
        if status == "Y":
            return APIResponses.success()
        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif "UNKNOWN" in message:
            return APIResponses.not_found(message=message)
        else:
            return APIResponses.failure(message=message)

    def patch(self, uuid):
        request_data = request.get_json()
        request_data['uuid'] = uuid
        response = self.translate("Update", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.not_found(message=message)

    def get(self, uuid):
        response = self.translate("Retrieve", {'uuid': uuid})

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.not_found(message=message)
