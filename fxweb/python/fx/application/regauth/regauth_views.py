"""
@file      regauth_views.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Implements the URIs that serve the files for the regauth views
"""
import urllib
from flask import request, jsonify, make_response, redirect, url_for
from flask_login import current_user

from app_csrf import csrf_required
from app_sanitize import sanitize_request, validate_request_json_is_dict
from application_log import ApplicationLogger as Logger
from base import server_views, server_files
from js_encoding import json_uri_component
from lib.utils.response_generator import APIResponses
from lib.utils.view_router import Route
from lib.auth import rkweb_session, rkweb_sync
from regauth import regauth_files
from regauth_login_response import RALoginResponse

from rk_application import views as rk_application_views
from rk_host_application.rk_host_exceptions import FailedRAVD
from server_request import ServerRequest
from server_views import ServerLoginView, ServerDefaultView, ServerLoginCredentials

def map_views(program):
    # API endpoints
    endpoints = {
        '/'                                                 : server_views.ServerDefaultView,
        '/object'                                           : server_views.ServerObjectView,
        '/logininfo'                                        : server_views.ServerLoginInfoView,
        '/systemInfo'                                       : rk_application_views.SystemInfoView,
        '/approve'                                          : RAApproveView,
        '/renew'                                            : RARenewView,
        '/download'                                         : RADownloadView,
        '/formdata'                                         : RAFormDataView,
    }

    # Web views
    views = {
        '/anonymous'                                    : RAAnonymousLoginView,
        '/download'                                     : RAAppDownloadView,
    }

    # Protected js file downloads
    files = {
        '/<filename>'                                   : server_files.ServerAppFiles,
        '/directives/<filename>'                        : server_files.ServerAppDirectivesFiles,
        '/components/<filename>'                        : server_files.ServerAppComponentsFiles,
        '/components/idioms/<filename>'                 : server_files.ServerAppComponentsIdiomsFiles,
        '/components/sections/<filename>'               : server_files.ServerAppComponentsSectionsFiles,
        '/components/sections/csrView/<filename>'       : regauth_files.RAAppComponentsSectionsCsrviewFiles,
        '/components/sections/submitterView/<filename>' : regauth_files.RAAppComponentsSectionsSubmitterviewFiles,
        '/components/sections/downloadView/<filename>'  : regauth_files.RAAppComponentsSectionsDownloadviewFiles,
    }

    # Prefix API with project name and API version
    final_views = {}
    for prefix, view in endpoints.items():
        final_views['/regauth/v1' + prefix] = view

    for prefix, view in views.items():
        final_views['/regauth' + prefix] = view

    for prefix, view in files.items():
        final_views['/regauth' + prefix] = view

    return final_views


class RAApproveView(ServerDefaultView):
    """
    Approver View that handles approving CSRs
    """
    decorators = [sanitize_request, csrf_required]

    def __init__(self, server_interface):
        super(RAApproveView, self).__init__(server_interface)

    def post(self, *args, **kwargs):
        """
        Performs the approval action
        """
        post_data = request.get_json()
        frontend_response = {}

        if post_data["method"] == "create":
            frontend_response = self.server_interface.approve(ServerRequest(request, post_data["approveData"]))
        elif post_data["method"] == "revoke":
            backend_request = ServerRequest(request, post_data["revokeData"])
            frontend_response = self.server_interface.revoke(backend_request)

        return jsonify(result="Success" if frontend_response else "Failure", objectData=frontend_response)


class RARenewView(ServerDefaultView):
    """
    Approver view that handles renewing CSRs.
    """
    decorators = [sanitize_request, csrf_required]

    def __init__(self, server_interface):
        super(RARenewView, self).__init__(server_interface)

    def post(self, *args, **kwargs):
        """
        Performs the renewal action.
        """
        post_data = request.get_json()
        frontend_response = {}

        frontend_response = self.server_interface.renew(
            ServerRequest(request, post_data["renewData"]))

        return jsonify(result="Success" if frontend_response else "Failure", objectData=frontend_response)


class RAFormDataView(ServerDefaultView):
    """
    Form Data View that handles getting form data
    """
    decorators = [sanitize_request, csrf_required]

    _REQUEST_TYPES = {
        'csr_upload': {
            'name': 'csr_upload',
            'mo_type': 'CERT_REQ',
            'fields': ['request', 'parseCSR']
        },
        'ldap_auth': {
            'name': 'ldap_auth',
            'fields': ['policyID', 'ldapUsername', 'ldapPassword']
        },
        'hash_upload': {
            'name': 'hash_upload',
            'mo_type': 'SIGNABLE_OBJ',
            'fields': ['padding', 'saltLength']
        },
        'v3_extensions_per_profile': {
            'name': 'v3_extensions_per_profile',
            'fields': ['objectID']
        },
        'v3_extensions_per_cert': {
            'name': 'v3_extensions_per_cert',
            'fields': ['objectID']
        },
        'issuance_policies': {
            'name': 'issuance_policies'
        }
    }

    def __init__(self, server_interface):
        super(RAFormDataView, self).__init__(server_interface)

    def post(self, *args, **kwargs):
        """
        Retrieve form data
        """
        post_data = request.get_json()
        frontend_response = {}

        if post_data["method"] == "retrieve":
            frontend_response = self.server_interface.formdata(
                ServerRequest(request, post_data["formData"]),
                self._REQUEST_TYPES,
                post_data.get('name')
            )

        return jsonify(result="Success" if frontend_response else "Failure", formData=frontend_response)


class AnonymousLoginResponse(RALoginResponse):
    """Manages a response for the anonymous login"""
    def __init__(self, _login):
        super(AnonymousLoginResponse, self).__init__()
        self._login = _login

    def parse_response(self, context, full_auth, response):
        """Create a response from parsed credentials
        Arguments:
            context: The user's context
            full_auth: True if the credential is fully authenticated
            response: The parsed credentials
        Returns: frontend_response with redirect
        """
        download_token = request.args.get('uniqueID')
        if full_auth:
            if download_token:
                frontend_response = self.download_response(download_token)
            else:
                frontend_response = self.authenticated_response()

            # Set the CSRF cookie
            frontend_response.set_cookie(key='FXSRF-TOKEN', value=context.csrf_token)

        else:
            frontend_response = self.unprotected_login()

        return frontend_response

    def anonymous_login(self, is_current_authed):
        """
        Handle RA specific redirect to app/landing if already authenticated
        :return a response to the redirect
        """
        if is_current_authed:
            response = self.authenticated_response()
        else:
            response, _ = self._login()
        return response


class RAAnonymousLoginView(ServerLoginView):
    """An anonymous login view for the RA
    This class will automatically login anonymous clients
    """
    decorators = [sanitize_request]

    anonymous_request = {
        'authType': 'anonymous',
    }

    def __init__(self, server_interface):
        super(RAAnonymousLoginView, self).__init__(server_interface)
        self._login_response = AnonymousLoginResponse(lambda: self._login(self.anonymous_request))

    def get(self, *args, **kwargs):
        """Redirects to the login page, the app page, or download page
        depending on stored download token
        :return a response containing the redirect
        """
        uniqueID = request.args.get('uniqueID')
        response = self._login_response.anonymous_login(self._is_current_authed())

        return response

    def _credentials(self, login_data):
        """Wrapper around ServerLoginCredentials.anonymous
        Arguments:
            login_data: the json login data from the command
        Returns: A UserPassCredential or None on error
        """
        return ServerLoginCredentials.anonymous(login_data)

    def _has_credentials(self, login_status):
        """Overrides the _has_credentials response
        Arguments:
            login_status: The server login result to parse
        Returns:
            frontend: Containing the frontend response
            login_status: with the server login result
        """
        # Get user context
        user = self._get_current_user()
        success, context = self._context.get_context(user)

        # Create response
        full_auth, response = self._response.parse_credentials(login_status)
        frontend = self._login_response.parse_response(context, full_auth, response)

        return frontend, login_status


class RAAppDownloadView(ServerDefaultView):
    """
    The download page
    """
    def __init__(self, server_interface):
        super(RAAppDownloadView, self).__init__(server_interface)

    def get(self, *args, **kwargs):

        # If not logged in, try to sync rkweb state first
        if not self._authenticated(current_user):
            rkweb_auth = rkweb_session()
            token = rkweb_sync(rkweb_auth)

        # Logged into fxweb already - deliver download page
        if self._authenticated(current_user):
            from base.static_content_view import create_static_response
            return create_static_response("/", "download-landing.html")

        # Get the download parameters
        uniqueID = request.args.get('uniqueID')
        anonymous = request.args.get('anon')
        # No download parameter, just go to landing page
        if not uniqueID:
            return redirect("/regauth")

        # Anonymous download - redirect to anonymous and it will then redirect back to download
        if anonymous and anonymous == "1":
            return redirect(url_for('/regauth/anonymous', uniqueID=uniqueID, _external=True, _scheme="https"))

        # Redirect to rkweb home login and tell it to redirect back here
        redirect_url = "regauth/download?uniqueID=" + uniqueID
        return redirect("/#?redirect=" + urllib.parse.quote(redirect_url).replace("/", "%2F"))


class RADownloadView(ServerDefaultView):
    """
    Handles downloading of PKCS#12 password protected files
    """
    decorators = [sanitize_request, csrf_required]
    uri_matcher = '?uniqueID=[A-F0-9]{16}'

    def __init__(self, server_interface):
        super(RADownloadView, self).__init__(server_interface)

    def post(self, *args, **kwargs):
        """
        Handles PKCS#12 download request
        """
        post_data = request.get_json()
        frontend_response = {"result": "Failure"}

        try:
            response_data = [
                post_data["uniqueID"],
                post_data["password"],
                post_data["clear_pki"]
            ]

            frontend_response = self.server_interface.download(
                ServerRequest(request, response_data))

            if frontend_response["result"] == "Success":
                current_user.reset_download_token()

        except:
            raise

        return jsonify(frontend_response)


class RAEchoView(server_views.ServerTranslatedView):
    """
    Echo system information
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, 'RA', 'System')

    def get(self):
        """
        Get system information
        """
        response = self.translate('EchoInfo', request.args)
        status, message = response.get('status', 'Y'), response.get('message', '')

        if status == 'Y':
            return APIResponses.get_success(body=response)
        elif status == 'P':
            return APIResponses.forbidden(message)
        else:
            return APIResponses.internal_error()

class RAPKIRequestView(server_views.ServerTranslatedView):
    """
    View class for Approval requests
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, 'RA', 'Approvals')

    def post(self, *args, **kwargs):
        """
        Create an approval request
        """
        # Handle various types of approval requests
        try:
            request_data = request.get_json()
            cert_request_type = request_data.get('requestType', '')

            if cert_request_type == 'PKI':
                response = self.translate('CreatePKI', request_data)
            else:
                return APIResponses.post_failure(
                    f'Unsupported approval request type: {cert_request_type}'
                )
        except (ValueError, TypeError, IndexError):
            return APIResponses.bad_request()
        except FailedRAVD as e:
            if e.status == 'P' or e.message == 'NO PERMISSION':
                return APIResponses.forbidden('Insufficient permissions to apply DN Profile')
            return APIResponses.not_found(e.message)

        # Determine status result
        status, message = response.pop('status', 'N'), response.pop('message', '')
        if status == 'Y' and not message:
            return APIResponses.post_success(body=response)
        elif status == 'P' or message == 'NO PERMISSION':
            return APIResponses.forbidden(message)
        elif 'DUPLICATE CERTIFICATE COMMON NAME' in message:
            return APIResponses.conflict(message)
        elif 'NOT FOUND' in message:
            return APIResponses.not_found(message)
        elif 'LDAP CREDENTIALS REQUIRED' in message or\
            'LDAP AUTHENTICATION FAILURE' in message:
            return APIResponses.forbidden(message)
        elif 'INVALID LDAP PASSWORD' in message or\
            'PKI GENERATION NOT ALLOWED' in message:
            return APIResponses.bad_request(message)
        else:
            return APIResponses.internal_error(message)


@Route()
class RAKeysView(server_views.ServerTranslatedView):
    """
    View class for Symmetric Keys
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, 'RA', 'Keys')

    @Route.get({"hsmStorage": "trusted"})
    def export_symmetric_trusted_key(self, *args, **kwargs):
        """
        Retrieve a trusted key/cryptogram
        """
        request_data = request.args.to_dict(flat=True)
        # Support both field names, "header" or "akbHeader" for backwards compatibility
        # "header" was released to mean AKB but is ambiguous with POST taking tr31Header
        if 'header' in request_data:
            request_data['akbHeader'] = request_data.pop('header')

        try:
            response = self.translate('ExportSymmetric', request_data)
        except LookupError as e:
            return APIResponses.bad_request()

        errors = (
            'INVALID GROUP NAME',
            'INVALID KEY NAME',
            'INVALID HOST NAME',
            'INVALID AKB HEADER',
            'KEY GROUP HAS NO RETRIEVAL METHOD',
            'DUPLICATE HOST NAME',
            'KEY BLOCKS NOT SUPPORTED FOR AES KEYS',
            'NO CBC WITHOUT HOST',
            'Clear export feature disabled.',
            'Failed to lookup user group.',
            'Key does not support clear export.',
            'Key is a template.',
            'CHANGING CHECKSUM LENGTH HAS NOT BEEN ENABLED',
        )

        not_found = (
            'UNKNOWN KEY GROUP',
            'KEY TRANFER KEY NOT FOUND',
            'KEY NOT FOUND',
            'HOST NOT FOUND',
            'HOST KEY NOT FOUND',
        )

        status, message = response.pop('status', 'N'), response.pop('message', '')
        if status == 'Y':
            return APIResponses.get_success(body=response)
        elif status == 'P' or 'Insufficient' in message or\
            'INSUFFICIENT' in message or\
            'User group must' in message:
            return APIResponses.forbidden(message)
        elif 'DUPLICATE KEY NAME' in message:
            return APIResponses.conflict(message)
        elif any(err in message for err in not_found):
            return APIResponses.not_found(message)
        elif any(err in message for err in errors):
            return APIResponses.bad_request(message)
        else:
            return APIResponses.internal_error(message)

    @Route.get({'hsmStorage': 'protected'},
        {'keyName': '*', 'keyId': '*'})
    def export_symmetric_protected_key(self, *args, **kwargs):
        """
        Retrieve a protected key/cryptogram
        """
        response = self.translate('ExportSymmetricProtected', request.args)

        errors = (
            'INVALID NAME',
            'INVALID GROUP NAME',
            'INVALID WRAPPING KEY NAME',
            'INVALID WRAPPING KEY GROUP NAME',
            'INVALID KEY MATERIAL'
            'INVALID PASSWORD FORMAT',
            'MUST BE A BOOLEAN',
            'Format not supported',
            'Export type not supported',
            'Associated wrapping key does not exist',
            'Password required',
        )

        not_found = (
            'UNKNOWN APPLICATION KEY GROUP',
            'UNKNOWN APPLICATION KEY',
        )

        status, message = response.pop('status', 'N'), response.pop('message', '')
        if status == 'Y':
            return APIResponses.get_success(body=response)
        elif status == 'P' or 'Insufficient' in message or\
            'INSUFFICIENT' in message or\
            'User group must' in message:
            return APIResponses.forbidden(message)
        elif 'DUPLICATE KEY NAME' in message:
            return APIResponses.conflict(message)
        elif any(err in message for err in not_found):
            return APIResponses.not_found(message)
        elif any(err in message for err in errors):
            return APIResponses.bad_request(message)
        else:
            return APIResponses.internal_error(message)

    @Route.get({'hsmStorage': 'protected'},
        {'keyGroup': '*', 'keyGroupId': '*'})
    def retrieve_symmetric_protected_key_group(self, *args, **kwargs):
        """
        Retrieve a protected key group
        """
        response = self.translate('RetrieveSymmetricProtected', request.args)

        errors = (
            'INVALID NAME',
            'INVALID PASSWORD FORMAT',
            'MUST BE A BOOLEAN',
            'Format not supported',
            'Could not parse application key cryptogram',
            'Password required',
        )

        not_found = (
            'UNKNOWN APPLICATION KEY GROUP',
            'UNKNOWN APPLICATION KEY',
            'UNKNOWN KEY',
        )

        status, message = response.pop('status', 'N'), response.pop('message', '')
        if status == 'Y':
            return APIResponses.get_success(body=response)
        elif status == 'P' or 'Insufficient' in message or\
            'INSUFFICIENT' in message or\
            'User group must' in message:
            return APIResponses.forbidden(message)
        elif 'DUPLICATE KEY NAME' in message:
            return APIResponses.conflict(message)
        elif any(err in message for err in not_found):
            return APIResponses.not_found(message)
        elif any(err in message for err in errors):
            return APIResponses.bad_request(message)
        else:
            return APIResponses.internal_error(message)

    @Route.post({'hsmStorage': 'trusted'})
    def create_trusted_key(self):
        """
        Create a random symmetric key
        """
        try:
            request_data = request.get_json()
            create_response = self.translate('CreateRandomKey', request_data)
        except ValueError as e:
            message = str(e)
            Logger.debug(message)
            return APIResponses.bad_request(message)

        create_status = create_response.pop('status', 'N')
        create_message = create_response.pop('message', '')
        export_format = request_data.get('format', 'Cryptogram')

        # create always returns the keyblock as a cryptogram, so if they requested a different one
        # replace the keyblock with a call to retrieve, which supports different formats
        if create_status == 'Y' and export_format != 'Cryptogram':
            retrieve_request = {'keyId': create_response.get('id', ''), 'format': export_format}
            if 'akbHeader' in request_data:
                retrieve_request['akbHeader'] = request_data['akbHeader']

            retrieve_response = self.translate('ExportSymmetric', retrieve_request)

            # create_response returns `keyblock` and retrieve_response returns `keyBlock`
            create_response['keyblock'] = retrieve_response.get('keyBlock', '')

            message = retrieve_response.get('message', '')
            if message or retrieve_response.get('status', 'N') != 'Y':
                return APIResponses.multi_status(message)

        if create_status == 'Y' and not create_message:
            return APIResponses.post_success(body=create_response)
        elif 'NOT FOUND' in create_message:
            return APIResponses.not_found(create_message)
        elif create_status == 'N':
            return APIResponses.post_failure(create_message)
        elif create_status == 'A':
            return APIResponses.conflict(create_message)
        elif create_status == 'P' or 'INSUFFICIENT' in create_message:
            return APIResponses.forbidden(create_message)
        else:
            return APIResponses.internal_error(create_message)

    @Route.post({'hsmStorage': 'protected'})
    def create_protected_key(self):
        """
        Create a random symmetric protected key
        """
        request_data = request.get_json()
        if request_data.get('operation', '') == 'add':
            response = self.translate('ImportProtectedKey', request_data)
        else:
            response = self.translate('CreateRandomProtectedKey', request_data)

        status, message = response.pop('status', 'N'), response.pop('message', '')
        if status == 'Y' and not message:
            return APIResponses.post_success(body=response)
        elif 'NOT FOUND' in message:
            return APIResponses.not_found(message)
        elif status == 'N':
            return APIResponses.post_failure(message)
        elif status == 'A':
            return APIResponses.conflict(message)
        elif status == 'P' or 'INSUFFICIENT' in message:
            return APIResponses.forbidden(message)
        else:
            return APIResponses.internal_error(message)


class RAKeysDecryptView(server_views.ServerTranslatedView):
    """
    View class for decryption with Symmetric Keys
    """
    errors = (
        'MISSING KEY NAME',
        'INVALID DATA HEADER',
        'CIPHER DOES NOT MATCH HEADER',
        'KEY NAME DOES NOT MATCH HEADER',
        'KEY GROUP NAME DOES NOT MATCH HEADER',
        'PADDING MODE DOES NOT MATCH HEADER',
        'KEY IS INACTIVE',
        'KEY IS EXPIRED',
        'INCORRECT KEY MODIFIER',
        'KEY TEMPLATE NOT ALLOWED',
        'INCORRECT KEY USAGE',
        'HSM POLICY DOES NOT ALLOW',
        'IV LENGTH DOES NOT MATCH CIPHER BLOCK SIZE',
    )

    def __init__(self, server_interface):
        super().__init__(server_interface, 'RA', 'Keys')

    def post(self):
        """
        Decrypt data with symmetric key
        """
        request_data = request.get_json()
        try:
            request_data['mode'] = '0'
        except TypeError:
            return APIResponses.bad_request('Invalid input type.')

        response = self.translate('GeneralEncryption', request_data)
        status, message = response.pop('status', 'Y'), response.pop('message', '')

        if response.get('result', None):
            message = 'Decryption successful'
            return APIResponses.post_success(message=message, body=response)
        elif status == 'P' or 'INSUFFICIENT PERMISSION' in message:
            return APIResponses.forbidden(message)
        elif 'UNKNOWN KEY' in message or 'UNKNOWN KEY GROUP' in message:
            return APIResponses.not_found(message)
        elif any(err in message for err in self.errors):
            return APIResponses.bad_request(message)
        else:
            return APIResponses.internal_error(message)


class RAKeysEncryptView(server_views.ServerTranslatedView):
    """
    View class for encryption with Symmetric Keys
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, 'RA', 'Keys')

    def post(self):
        """
        Encrypt data with symmetric key
        """
        request_data = request.get_json()
        try:
            request_data['mode'] = '1'
        except TypeError:
            return APIResponses.bad_request('Invalid input type.')

        response = self.translate('GeneralEncryption', request_data)
        status, message = response.pop('status', 'Y'), response.pop('message', '')

        if response.get('result', None):
            message = 'Encryption successful'
            return APIResponses.post_success(message=message, body=response)
        elif status == 'P' or 'INSUFFICIENT PERMISSION' in message:
            return APIResponses.forbidden(message)
        elif 'UNKNOWN KEY' in message or 'UNKNOWN KEY GROUP' in message:
            return APIResponses.not_found(message)
        elif any(err in message for err in RAKeysDecryptView.errors):
            return APIResponses.bad_request(message)
        else:
            return APIResponses.internal_error(message)


@Route()
class RAPKIView(server_views.ServerTranslatedView):
    """
    View class for Asymmetric keys
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, 'RA', 'Certificates')

    @Route.get({'requestType':'PKI'})
    def retrieve_pki(self, *args, **kwargs):
        """
        Retrieve a PKI approval request
        """

        request_data = request.args.to_dict(flat=True)

        request_data["_format"] = request_data.pop("format", "DER").upper()
        response = self.translate('RetrievePKI', request_data)

        status, message = response.pop('status', 'N'), response.pop('message', '')
        if status == 'Y' and not message:
            return APIResponses.get_success(body=response)
        elif 'PERMISSION' in message or status == 'P':
            return APIResponses.forbidden(message)
        elif 'UNKNOWN ' in message:
            return APIResponses.not_found(message)
        else:
            return APIResponses.internal_error(message)

    @Route.get({'requestType':'list'})
    def list_pkicerts(self, *args, **kwargs):
        request_data = request.args

        response = self.translate('List', request_data)

        status, message = response.pop('status', 'N'), response.pop('message', '')
        if status == 'Y' and not message:
            return APIResponses.get_success(body=response)
        elif 'PERMISSION' in message or status == 'P':
            return APIResponses.forbidden(message)
        elif ' NOT FOUND' in message or message == 'INVALID CHUNK':
            return APIResponses.not_found(message)
        else:
            return APIResponses.internal_error(message)


class RAExportCertificateView(server_views.ServerTranslatedView):
    """
    View class for exporting Certificate(s)
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, 'RA', 'Certificates')

    def get(self, *args, **kwargs):
        """
        Export single Certificate
        """

        request_data = request.args.to_dict(flat=True)

        request_data["_format"] = request_data.pop("format", "PEM").upper()
        response = self.translate('Export', request_data)

        status, message = response.pop('status', 'N'), response.pop('message', '')
        if 'certData' in response and not message:
            if request_data["_format"] != "JSON":
                return APIResponses.return_file(
                    response['filename'],
                    response['certData'],
                    'application/x-pem-file' if request_data["_format"] == "PEM" else 'application/pkix-cert'
                )
            return APIResponses.get_success(body=response)
        elif message == 'NO PERMISSION' or status == 'P':
            return APIResponses.forbidden(message)
        elif message in (
            'INVALID CERTIFICATE AUTHORITY',
            'ERROR RETRIEVING CERTIFICATE',
        ):
            return APIResponses.not_found(message)
        else:
            return APIResponses.internal_error(message)


ERROR_MSGS_ASYM_404 = (
    'Invalid certificate authority container.',
    'Invalid certificate container.',
    'ERROR RETRIEVING CERTIFICATE',
    'Failed to retrieve PKI.',
)


@Route()
class RAImportCertificateView(server_views.ServerTranslatedView):
    """
    View class for importing Certificate(s) in PKCS #12 format
    """
    def __init__(self, server_interface):
        super().__init__(server_interface, 'RA', 'Certificates')

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


class RAPKIECCDecryptView(server_views.ServerTranslatedView):
    """
    View class for ECIES decryption with a certificate
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, 'RA', 'Certificates')

    def post(self):
        request_data = request.get_json()

        response = self.translate('DecryptECIES', request_data)
        status, message = response.pop('status', 'Y'), response.pop('message', '')

        if status == 'Y' and not message:
            return APIResponses.post_success('Decryption successful', body=response)
        elif status == 'P' or message == 'NO PERMISSION':
            return APIResponses.forbidden(message)
        elif message in ERROR_MSGS_ASYM_404:
            return APIResponses.not_found(message)
        elif 'Invalid' in message:
            return APIResponses.bad_request(message)
        else:
            return APIResponses.internal_error(message)


class RAPKIECCEncryptView(server_views.ServerTranslatedView):
    """
    View class for ECIES encryption with a certificate
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, 'RA', 'Certificates')

    def post(self):
        request_data = request.get_json()

        response = self.translate('EncryptECIES', request_data)
        status, message = response.pop('status', 'Y'), response.pop('message', '')

        if status == 'Y' and not message:
            return APIResponses.post_success('Encryption successful', body=response)
        elif status == 'P' or message == 'NO PERMISSION':
            return APIResponses.forbidden(message)
        elif message in ERROR_MSGS_ASYM_404:
            return APIResponses.not_found(message)
        elif 'Invalid' in message:
            return APIResponses.bad_request(message)
        else:
            return APIResponses.internal_error(message)


class RAPKIECCVerifyView(server_views.ServerTranslatedView):
    """
    View class for ECDSA signature verification with a certificate
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, 'RA', 'Certificates')

    def post(self):
        request_data = request.get_json()

        response = self.translate('VerifyECC', request_data)
        message = response.get('message', '')

        if message in ('Y', 'N'):
            response_body = {'result': message == 'Y'}
            response_message = 'Valid signature' if message == 'Y' else 'Invalid signature'
            return APIResponses.post_success(response_message, response_body)
        elif message == 'NO PERMISSION':
            return APIResponses.forbidden(message)
        elif message in ERROR_MSGS_ASYM_404:
            return APIResponses.not_found(message)
        elif 'INVALID' in message or 'Used hash type must match' in message:
            return APIResponses.bad_request(message)
        else:
            return APIResponses.internal_error(message)


class RAPKIRSADecryptView(server_views.ServerTranslatedView):
    """
    View class for RSA decryption with a certificate
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, 'RA', 'Certificates')

    def post(self):
        request_data = request.get_json()
        response = self.translate('DecryptRSA', request_data)
        status, message = response.pop('status', 'Y'), response.pop('message', '')

        if status == 'Y' and not message:
            return APIResponses.post_success('Decryption successful', body=response)
        elif status == 'P' or message == 'NO PERMISSION':
            return APIResponses.forbidden(message)
        elif message in ERROR_MSGS_ASYM_404:
            return APIResponses.not_found(message)
        elif 'INVALID' in message or 'Invalid' in message:
            return APIResponses.bad_request(message)
        else:
            return APIResponses.internal_error(message)


class RAPKIRSAEncryptView(server_views.ServerTranslatedView):
    """
    View class for RSA encryption with a certificate
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, 'RA', 'Certificates')

    def post(self):
        request_data = request.get_json()
        response = self.translate('EncryptRSA', request_data)
        status, message = response.pop('status', 'Y'), response.pop('message', '')

        if status == 'Y' and not message:
            return APIResponses.post_success('Encryption successful', body=response)
        elif status == 'P' or message == 'NO PERMISSION':
            return APIResponses.forbidden(message)
        elif message in ERROR_MSGS_ASYM_404:
            return APIResponses.not_found(message)
        elif 'INVALID' in message or 'Invalid' in message:
            return APIResponses.bad_request(message)
        else:
            return APIResponses.internal_error(message)


class RAPKIRSAVerifyView(server_views.ServerTranslatedView):
    """
    View class for RSA signature verification with a certificate
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, 'RA', 'Certificates')

    def post(self):
        request_data = request.get_json()

        response = self.translate('VerifyRSA', request_data)
        status, message = response.pop('status', 'N'), response.pop('message', '')

        if message in ('Y', 'N'):
            response_body = {'result': message == 'Y'}
            response_message = 'Valid signature' if message == 'Y' else 'Invalid signature'
            return APIResponses.post_success(response_message, response_body)
        elif status == 'P' or message == 'NO PERMISSION':
            return APIResponses.forbidden(message)
        elif message in ERROR_MSGS_ASYM_404:
            return APIResponses.not_found(message)
        elif 'INVALID' in message or 'Encoded hash type must match' in message:
            return APIResponses.bad_request(message)
        else:
            return APIResponses.internal_error(message)


class RAPKISignView(server_views.ServerTranslatedView):
    """
    View class for signature generation with a certificate (handles both RSA and ECDSA)
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, 'RA', 'Certificates')

    def post(self):
        request_data = request.get_json()

        errors = (
            'INVALID',
            'HASH ALGORITHM NOT ALLOWED WITH HSM POLICY',
            'CERTIFICATE DOES NOT HAVE A PRIVATE KEY',
            'CERTIFICATE IS REVOKED',
            'CERTIFICATE IS NOT YET VALID',
            'CERTIFICATE IS EXPIRED',
            'HSM POLICY DISALLOWS SIGNING WITH THIS CERTIFICATE TYPE',
        )

        response = self.translate('GenerateSignature', request_data)
        status, message = response.pop('status', 'Y'), response.pop('message', '')

        if status == 'Y' and not message:
            return APIResponses.post_success('Successfully generated signature', body=response)
        elif status == 'P' or 'PERMISSION' in message :
            return APIResponses.forbidden(message)
        elif 'MULTIPLE CERTIFICATES WITH GIVEN NAME FOUND' in message:
            return APIResponses.conflict(message)
        elif message in ERROR_MSGS_ASYM_404:
            return APIResponses.not_found(message)
        elif any(err in message for err in errors):
            return APIResponses.bad_request(message)
        else:
            return APIResponses.post_failure(message)


class RADNProfileView(server_views.ServerTranslatedView):
    """
    View class for signature generation with a certificate (handles both RSA and ECDSA)
    """

    def __init__(self, server_interface):
        super().__init__(server_interface, 'RA', 'DNProfiles')

    def get(self):
        request_data = request.args

        response = self.translate('Retrieve', request_data)
        status, message = response.pop('status', 'Y'), response.pop('message', '')

        if status == 'Y':
            return APIResponses.get_success(body=response)
        elif status == 'P' or message == 'NO PERMISSION':
            return APIResponses.forbidden(message)
        elif 'INVALID X.509 DN PROFILE' in message:
            return APIResponses.not_found(message)
        else:
            return APIResponses.internal_error(message)
