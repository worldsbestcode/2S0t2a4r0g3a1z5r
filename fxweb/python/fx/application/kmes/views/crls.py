"""
@file      kmes/views/crls.py
@author    Dalton McGee (dmcgee@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Implements the URI methods for Certificate Revocation Lists
"""

from flask import request

from base.server_views import ServerTranslatedView
from lib.utils.response_generator import APIResponses


class Crl(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "CRLs")

    def base_crud(self, operation, request_data):
        """
        Many of the CRUD functions in this class are identical.
        This provides a template for them to use.
        """
        response = self.translate(operation, request_data)
        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(message, response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif "Unable" in message or "no associated CRL" in message:
            return APIResponses.not_found(message=message)
        else:
            return APIResponses.bad_request(message=message, body=response)

    def post(self):
        request_data = request.get_json()

        response = self.translate("Create", request_data)
        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(message=message, body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif "Unable" in message:
            return APIResponses.not_found(message=message)
        elif "already has CRL" in message:
            return APIResponses.conflict(message=message)
        else:
            return APIResponses.bad_request(message=message, body=response)

    def get(self):
        return self.base_crud("Retrieve", request.args)

    def put(self):
        return self.base_crud("Update", request.get_json())

    def delete(self):
        return self.base_crud("Delete", request.args)


class ImportExport(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "CRLs")

    def get(self):
        request_data = request.args.to_dict(flat=True)

        response = self.translate("Export", request_data)
        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            # These are important to be popped so as to not appear in the JSON response.
            filename, format_ = response.pop("filename", None), response.pop("format", None)

            # Default response is to return a PEM file, whether nothing passed or "PEM"
            if format_ == "JSON":
                return APIResponses.success(message, response)
            elif format_ == "DER":
                return APIResponses.return_file(
                    f"{filename}.crl", bytes.fromhex(response["data"]), "application/pkix-crl"
                )
            else:
                return APIResponses.return_file(
                    f"{filename}.crl", response["data"], "application/x-pem-file"
                )

        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif "Unable" in message:
            return APIResponses.not_found(message=message)
        else:
            return APIResponses.bad_request(message=message)

    def post(self):
        # Checks to see if file is uploaded or if JSON is passed in the body
        if request.files:
            data = list(request.files.values())[0].read()

            # Assumes data is Base64 Bytes (pem) and uses decode() method. Hex Bytes (der) can't be
            # decoded this way hence catching the UnicodeDecodeError and decoding with hex() method.
            try:
                data = data.decode("utf-8")
            except UnicodeDecodeError:
                data = data.hex()

            request_data = {
                "data": data,
                "certId": request.form.get("certId"),
            }
        else:
            request_data = request.get_json()

        response = self.translate("Import", request_data)
        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(message, response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif "already has CRL" in message:
            return APIResponses.conflict(message=message)
        elif "Unable" in message:
            return APIResponses.not_found(message=message)
        else:
            return APIResponses.bad_request(message=message)


class RevokeCertificate(ServerTranslatedView):
    """
    View class for revoking a Certificate using a CRL
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "CRLs")

    def put(self):
        request_data = request.get_json()
        not_found_messages = ["Unable", "Invalid", "no associated CRL"]
        response = self.translate("Revoke", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(message=message, body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif "already revoked" in message or "can only revoke certificate they issue" in message:
            return APIResponses.conflict(message=message)
        elif any(string in message for string in not_found_messages):
            return APIResponses.not_found(message=message)
        else:
            return APIResponses.bad_request(message=message, body=response)
