"""
@file      kmes/views/certificates.py
@author    David Neathery(dneathery@futurex.com)

@section LICENSE
This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Implements the URI methods for the KMES Certificates view
"""

from flask import request

from base.server_views import ServerTranslatedView
from lib.utils.response_generator import APIResponses
from lib.utils.view_router import Route


@Route()
class Certificate(ServerTranslatedView):
    """
    View class for actions on certificates and asymmetric keys
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "Certificates")

    # @Route.post({"type": "CSR"})
    def create_from_csr(self):
        """
        Create an X.509 certificate from a certificate signing request
        """
        raise NotImplementedError

    # @Route.post({"type": "publicKey"})
    def create_from_public_key(self):
        """
        Create an X.509 certificate with given public key
        """
        raise NotImplementedError

    @Route.post({"type": "generated"})
    def generate_x509(self):
        """
        Create an X.509 certificate with a generated key pair
        """
        request_data = request.get_json()

        # Try to merge passwordExportable with securityUsage for backwards compatibility
        try:
            key_options = request_data.get("keyOptions", {})
            password_exportable = key_options.pop("passwordExportable", False)
            fw_sec_usage = key_options.setdefault("securityUsage", [])
            if password_exportable and "Password Export" not in fw_sec_usage:
                fw_sec_usage.append("Password Export")
        except (AttributeError, TypeError):
            pass

        response = self.translate("CreateX509", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        else:
            return APIResponses.failure(message=message)

    # @Route.post({"type": "EMV"})
    def generate_emv(self):
        """
        Create an EMV certificate with a generated key pair
        """
        raise NotImplementedError

    @Route.get(("id", "alias", "name", "pkiTree", "pkiTreeId"))
    def retrieve_cert(self):
        """
        Retrieve a single certificate
        """

        response = self.translate("RetrieveCert", request.args)

        status, message = response.pop("status", ""), response.pop("message", "")
        if not status and not message and response:
            return APIResponses.success(body=response)
        elif message == "NO PERMISSION":
            return APIResponses.forbidden(message=message)
        elif message:
            return APIResponses.not_found(message=message)
        else:
            return APIResponses.internal_error()

    def delete(self):
        """
        Delete a single certificate
        """
        response = self.translate("Delete", request.args)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success()
        elif status == "P":
            return APIResponses.forbidden(message)
        elif "ERROR RETRIEVING" in message:
            return APIResponses.not_found(message)
        else:
            return APIResponses.failure(message)


class CertificateAlias(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "Certificates")

    def post(self):
        """
        Create a Certificate Alias
        """
        request_data = request.get_json()

        response = self.translate("CreateAlias", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif "ERROR RETRIEVING" in message or "INVALID CERTIFICATE AUTHORITY" in message:
            return APIResponses.not_found(message=message)
        else:
            return APIResponses.failure(message=message)

    def get(self):
        """
        Retrieve Cert Alias List
        """
        request_data = request.args.to_dict(flat=True)
        response = self.translate("ListAliases", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message=message)
        elif "ERROR RETRIEVING" in message or "INVALID CERTIFICATE AUTHORITY" in message:
            return APIResponses.not_found(message=message)
        else:
            return APIResponses.bad_request(message=message)

    def delete(self):
        """
        Delete Single Certificate Alias
        """
        response = self.translate("DeleteAlias", request.args)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success()
        elif status == "P":
            return APIResponses.forbidden(message)
        elif "ERROR RETRIEVING" in message or "INVALID CERTIFICATE AUTHORITY" in message:
            return APIResponses.not_found(message)
        else:
            return APIResponses.failure(message)


class CertificateArchiveRestore(ServerTranslatedView):
    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "Certificates")

    def put(self):
        """
        Archive one or more certificates
        """
        request_data = request.get_json()
        request_data["_operation"] = request.endpoint[-7:]
        response = self.translate("ArchiveRestore", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(message, response)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.failure(message, response)


@Route()
class CertificateImport(ServerTranslatedView):
    """
    View class for importing certificates
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "Certificates")

    @Route.post({"type": "EMV"})
    def import_emv(self):
        """
        Import an EMV certificate
        """
        request_data = request.get_json()

        response = self.translate("ImportEMV", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P" or "PERMISSIONS" in message:
            return APIResponses.forbidden(message=message)
        elif "ALREADY EXISTS" in message or "CONFLICTING" in message:
            return APIResponses.conflict(message=message)
        else:
            return APIResponses.failure(message=message)

    @Route.post({"type": "X.509"})
    def import_x509(self):
        """
        Import an X.509 certificate
        """
        request_data = request.get_json()

        response = self.translate("ImportX509", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P" or "PERMISSIONS" in message:
            return APIResponses.forbidden(message=message)
        elif "ALREADY EXISTS" in message or "CONFLICTING" in message:
            return APIResponses.conflict(message=message)
        else:
            return APIResponses.failure(message=message)

    @Route.post({'type': 'PKCS12'})
    def export_pkcs12(self, *args, **kwargs):
        """
        Import PKCS12 certificate
        """
        request_data = request.get_json()

        response = self.translate('ImportPkcs12', request_data)

        status, message = response.pop('status', 'N'), response.pop('message', '')
        if status == 'Y' and not message:
            return APIResponses.get_success(body=response)
        elif message == 'NO PERMISSION' or status == 'P':
            return APIResponses.forbidden(message)
        elif message in ERROR_MSGS_ASYM_404:
            return APIResponses.not_found(message)
        else:
            return APIResponses.internal_error(message)


class CertificateExport(ServerTranslatedView):
    """
    View class for exporting Certificate(s)
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "Certificates")

    def get(self, *args, **kwargs):
        """
        Export single Certificate
        """

        export_format = request.args.get("format", "PEM")
        response = self.translate("Export", request.args)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if "certData" in response and not message:
            if export_format == "JSON":
                return APIResponses.success(body=response)
            mimetype = "application/pkix-cert"
            if export_format == "PEM":
                mimetype = "application/x-pem-file"
            return APIResponses.return_file(response["filename"], response["certData"], mimetype)
        elif message == "NO PERMISSION" or status == "P":
            return APIResponses.forbidden(message)
        elif message in (
            "INVALID CERTIFICATE AUTHORITY",
            "ERROR RETRIEVING CERTIFICATE",
        ):
            return APIResponses.not_found(message)
        else:
            return APIResponses.internal_error(message)


class CertPermissions(ServerTranslatedView):
    """
    View class for Certificate Permissions
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "Certificates")

    def get(self):
        response = self.translate("RetrievePermissions", request.args)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif status == "P":
            return APIResponses.forbidden(message)
        else:
            return APIResponses.not_found(message)

    def put(self):
        request_data = request.get_json()
        response = self.translate("UpdatePermissions", request_data)

        status, message = response.pop("status", "N"), response.pop("message", "")
        if status == "Y":
            return APIResponses.success(body=response)
        elif "FAILED TO LOOKUP" in message:
            return APIResponses.not_found(message=message)
        else:
            return APIResponses.failure(message=message)


class EmvCert(ServerTranslatedView):
    """
    View class for generating a Private Key for an EMV ICC Certificate
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, "KMES", "Certificates")

    def post(self):
        request_data = request.get_json()

        response = self.translate("GenerateEmvCert", request_data)

        status, message = response.pop("status", "Y"), response.pop("message", "")
        if status == "Y" and not message:
            return APIResponses.success(message=message, body=response)
        elif status == "P" or message == "NO PERMISSION":
            return APIResponses.forbidden(message=message)
        elif any(string in message for string in ["ERROR RETRIEVING", "INVALID CERTIFICATE"]):
            return APIResponses.not_found(message=message)
        elif "INVALID" in message:
            return APIResponses.bad_request(message=message, body=response)
        # this isn't really a conflict, but I don't know the best error here.
        elif "NOT AN ISSUER" in message:
            return APIResponses.conflict(message=message)
        else:
            return APIResponses.failure(message=message)
