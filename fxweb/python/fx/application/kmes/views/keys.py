"""
@file      kmes/views/keys.py
@author    David Neathery(dneathery@futurex.com)

@section LICENSE
This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Implements the URI methods for the KMES keys view
"""

from flask import request

from base.server_views import ServerTranslatedView
from lib.utils.response_generator import APIResponses
from lib.utils.view_router import Route


def merge_clear_export(request_data):
    # Try to merge clearExport with securityUsage for backwards compatibility
    try:
        clear_export = request_data.pop("clearExport", False)
        fw_sec_usage = request_data.setdefault("securityUsage", [])
        if clear_export and "Clear Key Export" not in fw_sec_usage:
            fw_sec_usage.append("Clear Key Export")
    except (AttributeError, TypeError):
        pass


@Route()
class Keys(ServerTranslatedView):
    """
    View class for Symmetric Keys
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "Keys")

    @Route.delete({"hsmStorage": "trusted"})
    def delete_trusted(self):
        """
        Delete a single symmetric key
        """
        data = request.args

        response = self.translate("DeleteSymmetric", data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success()
        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif message == "KEY NOT FOUND":
            return APIResponses.not_found(message=message)
        else:
            return APIResponses.failure(message=message)

    @Route.delete({"hsmStorage": "protected"})
    def delete_protected(self):
        """Delete a protected key"""
        data = request.args

        response = self.translate("DeleteSymmetricProtected", data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success()
        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif message == "UNKNOWN HSM PROTECTED KEY":
            return APIResponses.not_found(message=message)
        else:
            return APIResponses.failure(message=message)

    @Route.post({"hsmStorage": "trusted"})
    def create_trusted_key(self):
        """
        Create a random symmetric key
        """

        request_data = request.get_json()
        merge_clear_export(request_data)
        create_response = self.translate("CreateRandomKey", request_data)

        create_status = create_response.pop("status", "N")
        create_message = create_response.pop("message", "")
        export_format = request_data.get("format", "Cryptogram")

        # create always returns the keyblock as a cryptogram, so if they requested a different one
        # replace the keyblock with a call to retrieve, which supports different formats
        if create_status == "Y" and export_format != "Cryptogram":
            retrieve_request = {"id": create_response.get("id", ""), "format": export_format}
            if "akbHeader" in request_data:
                retrieve_request["akbHeader"] = request_data["akbHeader"]

            retrieve_response = self.translate("ExportSymmetric", retrieve_request)

            # create_response returns `keyblock` and retrieve_response returns `keyBlock`
            create_response["keyblock"] = retrieve_response.get("keyBlock", "")

            message = retrieve_response.get("message", "")
            if message or retrieve_response.get("status", "N") != "Y":
                return APIResponses.multi_status(message)

        if create_status == "Y" and not create_message:
            return APIResponses.success(body=create_response)
        elif create_status == "N":
            return APIResponses.failure(create_message)
        elif create_status == "A":
            return APIResponses.conflict(create_message)
        elif create_status == "P" or "INSUFFICIENT" in create_message:
            return APIResponses.forbidden(create_message)
        elif "NOT FOUND" in create_message:
            return APIResponses.not_found(create_message)
        else:
            return APIResponses.internal_error(create_message)

    @Route.post({"hsmStorage": "protected"})
    def create_protected_key(self):
        """
        Create a random symmetric protected key
        """
        response = self.translate("CreateRandomProtectedKey", request.get_json())

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y" and not message:
            return APIResponses.success(body=response)
        elif status == "N":
            return APIResponses.failure(message)
        elif status == "A":
            return APIResponses.conflict(message)
        elif status == "P" or "INSUFFICIENT" in message:
            return APIResponses.forbidden(message)
        elif "NOT FOUND" in message:
            return APIResponses.not_found(message)
        else:
            return APIResponses.internal_error(message)


@Route()
class KeyExport(ServerTranslatedView):
    """
    View class for Symmetric Keys
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "Keys")

    @Route.post({"hsmStorage": "trusted"})
    def export_symmetric_trusted_key(self, *args, **kwargs):
        """
        Export a trusted key/cryptogram
        """
        request_data = request.get_json()
        # Support both field names, "header" or "akbHeader" for backwards compatibility
        # "header" was released to mean AKB but is ambiguous with POST taking tr31Header
        if "header" in request_data:
            request_data["akbHeader"] = request_data.pop("header")

        response = self.translate("ExportSymmetric", request_data)

        errors = (
            "INVALID GROUP NAME",
            "INVALID KEY NAME",
            "INVALID HOST NAME",
            "INVALID AKB HEADER",
            "KEY GROUP HAS NO RETRIEVAL METHOD",
            "DUPLICATE HOST NAME",
            "KEY BLOCKS NOT SUPPORTED FOR AES KEYS",
            "NO CBC WITHOUT HOST",
            "Clear export feature disabled.",
            "Failed to lookup user group.",
            "Key does not support clear export.",
            "Key is a template.",
            "CHANGING CHECKSUM LENGTH HAS NOT BEEN ENABLED",
        )

        not_found = (
            "UNKNOWN KEY GROUP",
            "KEY TRANFER KEY NOT FOUND",
            "KEY NOT FOUND",
            "HOST NOT FOUND",
            "HOST KEY NOT FOUND",
        )

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P" or "INSUFFICIENT" in message.upper():
            return APIResponses.forbidden(message)
        elif "DUPLICATE KEY NAME" in message:
            return APIResponses.conflict(message)
        elif any(err in message for err in not_found):
            return APIResponses.not_found(message)
        elif any(err in message for err in errors):
            return APIResponses.bad_request(message)
        else:
            return APIResponses.internal_error(message)

    @Route.post({"hsmStorage": "protected"}, {"name": "*", "id": "*"})
    def export_symmetric_protected_key(self, *args, **kwargs):
        """
        Export a protected key/cryptogram
        """
        request_data = request.get_json()
        response = self.translate("ExportSymmetricProtected", request_data)

        errors = (
            "INVALID NAME",
            "INVALID GROUP NAME",
            "INVALID WRAPPING KEY NAME",
            "INVALID WRAPPING KEY GROUP NAME",
            "INVALID KEY MATERIAL" "INVALID PASSWORD FORMAT",
            "MUST BE A BOOLEAN",
            "Format not supported",
            "Export type not supported",
            "Associated wrapping key does not exist",
            "Password required",
        )

        not_found = (
            "UNKNOWN APPLICATION KEY GROUP",
            "UNKNOWN APPLICATION KEY",
        )

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P" or "INSUFFICIENT" in message.upper():
            return APIResponses.forbidden(message)
        elif "DUPLICATE KEY NAME" in message:
            return APIResponses.conflict(message)
        elif any(err in message for err in not_found):
            return APIResponses.not_found(message)
        elif any(err in message for err in errors):
            return APIResponses.bad_request(message)
        else:
            return APIResponses.internal_error(message)

    @Route.post({"hsmStorage": "protected"}, {"group": "*", "groupId": "*"})
    def retrieve_symmetric_protected_key_group(self, *args, **kwargs):
        """
        Retrieve a protected key group
        """
        response = self.translate("RetrieveSymmetricProtected", request.args)

        errors = (
            "INVALID NAME",
            "INVALID PASSWORD FORMAT",
            "MUST BE A BOOLEAN",
            "Format not supported",
            "Could not parse application key cryptogram",
            "Password required",
        )

        not_found = (
            "UNKNOWN APPLICATION KEY GROUP",
            "UNKNOWN APPLICATION KEY",
            "UNKNOWN KEY",
        )

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P" or "INSUFFICIENT" in message.upper():
            return APIResponses.forbidden(message)
        elif "DUPLICATE KEY NAME" in message:
            return APIResponses.conflict(message)
        elif any(err in message for err in not_found):
            return APIResponses.not_found(message)
        elif any(err in message for err in errors):
            return APIResponses.bad_request(message)
        else:
            return APIResponses.internal_error(message)


class ImportKeys(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "Keys")

    def post(self):
        """
        Import a symmetric key
        """

        request_data = request.get_json()
        merge_clear_export(request_data)

        response = self.translate("Import", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "A":
            return APIResponses.conflict(message=message)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.failure(message=message)
