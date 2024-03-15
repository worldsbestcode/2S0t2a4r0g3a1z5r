"""
@file      regauth_interface.py
@author    Matthew Seaworth (mseaworth@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Registration server interface object
"""
import json
from flask_login import current_user
import binascii

from application_log import ApplicationLogger as logger
from rk_application_server_interface import RKApplicationServerInterface
from conn_exceptions import (
    ErrorOnWriteException,
    InvalidMessageException,
    MissingConnectionException
)

from rk_exceptions import (
    ObjectNotAddedException,
    ObjectNotDeletedException,
    ObjectNotModifiedException,
    ObjectNotValidatedException
)

from librk import (
        ApprovableField,
        Filter,
        ManagedObjectUtils,
        ManagedObject
)

from lib.utils.data_structures import ExcryptMessage

import librk

APPROVABLE_TYPES = [
        ManagedObject.APPROVABLE_OBJ,
        ManagedObject.SIGNABLE_OBJ,
        ManagedObject.CERT_REQ
]

class RAServerInterface(RKApplicationServerInterface):
    """
    Handles RA specific server interaction for CRUD actions and special functionality
    """
    def __init__(self, program):
        super(RAServerInterface, self).__init__(program)

    def approve(self, server_request):
        """
        Approve/Deny a CSR request
        """
        frontend_response = self._approve(server_request)

        return frontend_response

    def download(self, server_request):
        """
        Downloads a PKCS#12 request
        """
        frontend_response = self._download(server_request)

        return frontend_response

    def revoke(self, server_request):
        """Revoke a CSR
        Arguments:
            server_request: The received revoke request
        Returns: Parsed server response
        """
        return self._revoke(server_request)
    
    def renew(self, server_request):
        """Renew a CSR
        Arguments:
            server_request: The received renew request
        Returns: Parsed server response
        """
        return self._renew(server_request)

    def _approve(self, server_request):
        """
        Approve/Deny a CERT_REQ object
        """
        frontend_response = {}

        for k,v in server_request.data.items():
            for obj in v:
                # Check what type of approval this is
                approval_type = k
                if approval_type in ['CERT_REQ', 'SIGNABLE_OBJ']:
                    # Serialize into Excrypt message
                    em = ExcryptMessage()
                    em.setFieldAsString("AO", "RKY200")
                    em.setFieldAsString("AP", "Y" if obj["approved"] else "N")
                    id_tag_json = [('CR', 'csrID'), ('SO', 'hashID')]
                    for em_tag, id_json in id_tag_json:
                        id_list = obj.get(id_json)
                        if id_list:
                            em.setFieldAsString(em_tag, id_list)

                    em.setFieldAsString("NT", obj["message"])

                    # Send the approval to rkserver
                    try:
                        backend_response = self.send(em.getText())
                    except MissingConnectionException:
                        raise

                    # Handle backend_response
                    emResp = ExcryptMessage(backend_response)
                    result = True if emResp.getField("AN") == "Y" else False
                    message = emResp.getField("ER")

        frontend_response = { "result": result, "message": message }
        return frontend_response

    def _revoke(self, server_request):
        """Revoke a CSR
        Arguments:
            server_request: The received revoke request
        Returns: Parsed server response
        """
        revoke = server_request.data
        field_tags = {
            'AO': 'RKY203',
            'ID': ','.join(revoke['ids']),
            'RE': str(revoke['reason']),
            'RR': revoke.get('notes', '')
        }

        backend_response = self.send_dict(field_tags)
        return {
            'result': backend_response.getField('AN') == 'Y',
            'message': backend_response.getField('ER')
        }

    def _renew(self, server_request):
        """Renew a CSR
        Arguments:
            server_request: The received revoke request
        Returns: Parsed server response
        """
        renew = server_request.data
        field_tags = {
            'AO': 'RKY201',
            'ID': renew['id'],
        }

        backend_response = self.send_dict(field_tags)
        return {
            'result': backend_response.getField('AN') == 'Y',
            'message': backend_response.getField('ER')
        }

    def _download(self, server_request):
        """
        Download a PKCS#12 object
        """
        frontend_response = {}
        
        unique_id = server_request.data[0]
        password = server_request.data[1]
        clear_pki = server_request.data[2]

        message = ""
        name    = ""
        pki     = ""
        result  = False

        if (len(password) <= 0): 
            message = "Invalid password entered."
        else:
            em = ExcryptMessage()
            em.setFieldAsString("AO", "RKY202")
            em.setFieldAsString("UD", unique_id)
            em.setFieldAsString("PW", password)

            try:
                backend_response = self.send(em.getText())
            except MissingConnectionException:
                raise

            # Handle backend_response
            emResp = ExcryptMessage(backend_response)
            result = emResp.getField("AN") == "Y" 

            if not result:
                if emResp.hasField("ER"):
                    message = emResp.getField("ER")
                else:
                    message = "Could not download pki data."
            else:
                pki = emResp.getField("PK")
                name = emResp.getField("NA")

                if clear_pki:
                    self._clear_pki(unique_id, message)

        frontend_response = { "result": "Success" if result else "Failure", "message": message, "pki": pki, "name" : name}
        return frontend_response

    def _check_clauses(self, query):
        """Check a filter's clauses
        Parameters:
            query: the filter query object
        Returns: true on success false otherwise
        """
        if not current_user.context.is_anonymous():
            return ''

        query_type = ManagedObjectUtils.getType(query.getManager())
        if query_type not in APPROVABLE_TYPES:
            return ''

        field = int(ApprovableField.eUploaderEmails)
        if query.hasClauseField(ManagedObject.APPROVABLE_OBJ, field):
            return ''

        return 'Could not perform query without email clause'

    def _clear_pki(self, unique_id, message):
        """
        Clear a PKCS#12 object
        """
        em = ExcryptMessage()
        em.setFieldAsString("AO", "RKY204")
        em.setFieldAsString("UD", unique_id)

        try:
            backend_response = self.send(em.getText())
        except MissingConnectionException:
            raise

        # Handle backend_response
        emResp = ExcryptMessage(backend_response)
        result = emResp.getField("AN") == "Y" 

        if not result:
            if emResp.hasField("ER"):
                message = emResp.getField("ER")
            else:
                message = "Could not clear pki data."

    def _get_formdata(self, request_type, request_values):
        """
        Helper method to get form data for an object
        """
        frontend_response = None
        JSON_OBJECTS = ['csr_upload', 'hash_upload']
        try:
            name = request_type.get('name')
            if name in JSON_OBJECTS:
                # create managed object
                mo_type = ManagedObjectUtils.getType(request_type['mo_type'])
                mo = ManagedObjectUtils.createObjectFromTypeTake(mo_type, 0)

                mo_json = json.loads(mo.toJSONString())

                # Multiple fields can be expected in this request.
                fields = request_type['fields']

                for field in fields:
                    mo_json[field] = request_values[field]

                mo.fromJSONString(json.dumps(mo_json), librk.eMOActionCreate)
                self._sanitize_object(mo)

                frontend_response = {}
                frontend_response[name] = [mo.toJSONString()]

            elif name == 'ldap_auth':
                policyID = request_values['policyID']
                username = request_values['ldapUsername']
                password = request_values['ldapPassword']

                logger.info('Authenticating user \'' + username +
                            '\' via LDAP.')

                em = ExcryptMessage()
                em.setFieldAsString('AO', 'RKY207')
                em.setFieldAsString('MN', 'REG_AUTH')
                em.setFieldAsString('ID', policyID)
                em.setFieldAsString('DA', username)
                em.setFieldAsString('CH', binascii.hexlify(password.encode()).decode())

                try:
                    backend_response = self.send(em.getText())
                except MissingConnectionException:
                    raise

                # Handle backend_response
                emResp = ExcryptMessage(backend_response)
                result = True if emResp.getField("AN") == "Y" else False

                if not result:
                    if emResp.hasField("ER"):
                        message = ('Failed to authenticate LDAP user \'' +
                                   username + '\': ' + emResp.getField("ER"))
                    else:
                        message = ('Could not authenticate LDAP user \'' +
                                   username + '\'.')
                else:
                    message = ('Successfully authenticated LDAP user \'' +
                               username + '\'.')

                logger.info(message)

                ldap_auth = {}
                fields = request_type['fields']
                for field in fields:
                    ldap_auth[field] = request_values[field]

                ldap_auth['authenticated'] = result
                ldap_auth['message'] = message

                frontend_response = {}
                frontend_response['ldap_auth'] = ldap_auth

            elif name == 'v3_extensions_per_profile':
                    # Query server

                    backend_responses = self.query_rk_associated_objects(ManagedObject.X509CERT, ManagedObject.V3EXT_PROFILE, request_values['objectID'], current_user.context)

                    # Build response
                    frontend_response = self._get_mos("V3EXT_PROFILE", backend_responses)
        
            elif name == 'v3_extensions_per_cert':
                    # Query server...
                    backend_responses = self.query_rk_associated_objects(
                        ManagedObject.CERT_REQ,
                        ManagedObject.V3EXT,
                        request_values['objectID'],
                        current_user.context,
                        match_secondary_manager=False)

                    # ... build response.
                    frontend_response = self._get_mos("V3EXT_PROFILE", backend_responses)

            elif name == 'issuance_policies':
                    # Get data from request
                    mo_type = ManagedObjectUtils.getType(request_values['manager'])
                    object_id = request_values['objectID']

                    # Query server
                    backend_responses = self.query_rk_associated_objects(mo_type, ManagedObject.REG_AUTH, object_id, current_user.context)

                    # Build response
                    frontend_response = self._get_mos("REG_AUTH", backend_responses)

        except (ValueError, KeyError) as e:
            logger.error('Failed to query objects from formdata: ' + str(e))
            raise InvalidMessageException(None, "Could not parse request/response")

        return frontend_response

    def _add_whitelist(self):
        """ Gets allowed managed object types that can be added.
        Returns: A list of types that are allowed to be added.
        """
        return [
            ManagedObject.APPROVABLE_OBJ,
            ManagedObject.CERT_REQ,
            ManagedObject.SIGNABLE_OBJ,
        ]

    def _delete_whitelist(self):
        """ Gets allowed managed object types that can be deleted
        Returns: A list of types that are allowed to be deleted
        """
        return [
            ManagedObject.APPROVABLE_OBJ,
            ManagedObject.CERT_REQ,
            ManagedObject.SIGNABLE_OBJ,
        ]

    def _filter_whitelist(self):
        """ Gets allowed managed object types that can be filtered
        Returns: A list of types that are allowed to be filtered
        """
        # Many objects are accessed through form data instead of direct filter
        return [
            ManagedObject.APPROVABLE_OBJ,
            ManagedObject.APPROVAL_GROUP,
            ManagedObject.CERT_REQ,
            ManagedObject.CRL,
            ManagedObject.SIGNABLE_OBJ,
            ManagedObject.X509CERT,
            ManagedObject.X509DN_PROFILE,
        ]
