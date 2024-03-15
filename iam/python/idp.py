from rkweb.auth import perm_required
from rkweb.flaskutils import Blueprint, respond, abort

from marshmallow import fields, validate
from rkweb.rkserver import ServerConn, ExcryptMsg
from rkweb.session import AuthSession

from typing import List

import json
import binascii

from models import IdentityProvider, IdentityProviderList, CreateResponse, get_combined_type
from models import get_combined_type, get_provider_type, get_mech_type

# Blueprint
def IdpBlueprintV1():
    blp = Blueprint(
        "Identity Providers",
        "idp",
        url_prefix="/idp",
        description="Manage Identity Providers",
    )
    define_get(blp)
    define_list(blp)
    define_add(blp)
    define_modify(blp)
    define_delete(blp)
    return blp

def get_combined_name(idp_name: str, mech_name: str) -> str:
    name = idp_name
    if name != mech_name:
        name += " (" + mech_name + ")"
    return name

# Retrieve stubs
def define_list(blp):
    @blp.fxroute(
        endpoint="/stubs",
        method="GET",
        description="Retrieve a list of available identity providers",
        resp_schemas={
            200: IdentityProviderList,
        })
    @perm_required("IdentityProvider")
    async def getStubs():

        jwt = AuthSession.auth_token()

        # Request all auth mechanisms
        req = ExcryptMsg("[AORKAM;]")
        req.set_tag("OP", "list")
        req.set_tag("JW", jwt)
        rsp = await ServerConn().send_excrypt(req)

        rkResults = json.loads(binascii.unhexlify(rsp.get_tag("RS")).decode('utf-8'))

        results = []
        for result in rkResults['data']:
            results.append({
                'uuid': result['uuid'],
                'name': get_combined_name(result['identity_provider']['name'], result['name']),
                'modified': result['modified'],
                'providerType': get_combined_type(result['identity_provider']['provider_type'], result['credential_type']),
            })

        # Respond
        respond(200, {'results': results})

def check_error(rsp: ExcryptMsg) -> None:
    if rsp.get_tag("AN") != "Y":
        msg = rsp.to_error()
        if rsp.get_tag("AN") == "P":
            abort(401, msg)
        else:
            abort(400, msg)

# Retrieve single auth mech
def define_get(blp):
    @blp.fxroute(
        endpoint="/<uuid>",
        method="GET",
        description="Retrieve an identity provider's information",
        resp_schemas={
            200: IdentityProvider,
        })
    @perm_required("IdentityProvider")
    async def getStubs(uuid):

        jwt = AuthSession.auth_token()

        # Request all auth mechanisms
        req = ExcryptMsg("[AORKAM;]")
        req.set_tag("OP", "get")
        req.set_tag("ID", uuid)
        req.set_tag("JW", jwt)
        rsp = await ServerConn().send_excrypt(req)
        check_error(rsp)

        rkResult = json.loads(binascii.unhexlify(rsp.get_tag("RS")).decode('utf-8'))

        def copyFields(source, dest, fields):
            for field in fields:
                if field in source:
                    dest[field] = source[field]

        result = {
            'uuid': rkResult['uuid'],
            'name': get_combined_name(rkResult['identity_provider']['name'], rkResult['name']),
            'providerType': get_combined_type(rkResult['identity_provider']['provider_type'], rkResult['credential_type']),
        }

        copyFields(rkResult, result, ['allowExternal', 'unionRoles', 'enforceDualFactor'])

        if 'jwtParams' in rkResult:
            result['params'] = {}
            copyFields(rkResult['jwtParams'], result['params'], [
                'jwtAuthType',
                'issuer',
                'maxValidity',
                'leeway',
                'jwksUrl',
                'jwksTlsCa',
                'pkiVerifyCert',
                'userField',
                'userIdType',
                'rolesFromToken',
                'roleField',
                'roleIdType',
                'authorizedRoles',
                'claims',
                ])
        elif 'pkiParams' in rkResult:
            result['params'] = {}
            copyFields(rkResult['pkiParams'], result['params'], [
                'caCertificate',
                'userSource',
                'userIdType',
                'userOid',
                ])
        elif 'ldapParams' in rkResult:
            result['params'] = {}
            copyFields(rkResult['ldapParams'], result['params'], [
                'servers',
                'tlsProfile',
                'ldapTlsCa',
                'ldapVersion',
                'adminUser',
                'lookupMethod',
                'loginMode',
                'userBaseDn',
                'userField',
                'userIdType',
                'memberOfField',
                'roleBaseDn',
                'roleField',
                'roleIdType',
                'memberField',
                'lockoutThreshold',
                'lockoutPeriod',
                ])

        # Respond
        respond(200, result)

def args_to_rkap(req: ExcryptMsg, args: dict):
    req.set_tag("JW", AuthSession.auth_token())
    if 'name' in args:
        req.set_tag("NA", args['name'])

    if not 'providerType' in args:
        return

    req.set_tag("AT", get_provider_type(args['providerType']))

    if 'allowExternal' in args:
        req.set_tag("RU", "0" if args['allowExternal'] else "1")
    if 'unionRoles' in args:
        req.set_tag("UA", "1" if args['unionRoles'] else "0")
    if 'enforceDualFactor' in args:
        req.set_tag("EF", "1" if args['enforceDualFactor'] else "0")

    if args['providerType'] == 'JWT':
        params = args['params']
        req.set_tag('IS', params['issuer'])
        req.set_tag('KT', params['jwtAuthType'])
        if params['jwtAuthType'] == 'URL':
            req.set_tag('AK', params['jwksUrl'])
            if 'jwksTlsCa' in params:
                req.set_tag('JK', params['jwksTlsCa'])
        elif params['jwtAuthType'] == 'HMAC':
            req.set_tag('BE', '1')
            if 'hmacKey' in params:
                req.set_tag('AK', params['hmacKey'])
        elif params['jwtAuthType'] == 'PKI':
            if 'pkiVerifyCert' in params:
                req.set_tag('VK', params['pkiVerifyCert'])

        if 'leeway' in params:
            req.set_tag('LW', params['leeway'])
        if 'maxValidity' in params:
            req.set_tag('VL', params['maxValidity'])

    elif args['providerType'] == 'LDAP':
        params = args['params']

        req.set_tag('AD', ",".join(params['servers']))
        if 'ldapTlsCa' in params:
            req.set_tag('LK', params['ldapTlsCa'])
        if 'tlsProfile' in params:
            req.set_tag('TI', params['tlsProfile'])
        if 'ldapVersion' in params:
            req.set_tag('VS', params['ldapVersion'])
        if 'adminUser' in params:
            req.set_tag('AU', params['adminUser'])
        if 'adminPasswordHex' in params:
            req.set_tag('PX', params['adminPasswordHex'])
        if 'lookupMethod' in params:
            req.set_tag('LL', params['lookupMethod'])
        if 'loginMode' in params:
            req.set_tag('LM', params['loginMode'])
        if 'userBaseDn' in params:
            req.set_tag('UD', params['userBaseDn'])
        if 'userField' in params:
            req.set_tag('UF', params['userField'])
        if 'userIdType' in params:
            req.set_tag('UI', params['userIdType'])
        if 'memberOfField' in params:
            req.set_tag('OF', params['memberOfField'])
        if 'roleBaseDn' in params and params['roleBaseDn']:
            req.set_tag('RD', params['roleBaseDn'])
        if 'roleField' in params:
            req.set_tag('RF', params['roleField'])
        if 'roleIdType' in params:
            req.set_tag('RI', params['roleIdType'])
        if 'memberField' in params:
            req.set_tag('MF', params['memberField'])

    elif args['providerType'] == 'TLS':
        params = args['params']
        req.set_tag('CI', params['caCertificate'])

def args_to_rkam(req: ExcryptMsg, args: dict):
    req.set_tag("JW", AuthSession.auth_token())
    if 'name' in args:
        req.set_tag("NA", args['name'])

    if not 'providerType' in args:
        return

    req.set_tag("CT", get_mech_type(args['providerType']))

    # JWT Parameters
    if args['providerType'] == 'JWT':
        params = args['params']
        if 'userField' in params:
            req.set_tag("UF", params['userField'])
        if 'userIdType' in params:
            req.set_tag("UI", params['userIdType'])
        if 'rolesFromToken' in params:
            req.set_tag("RT", "1" if params['rolesFromToken'] else "0")
            if 'roleField' in params:
                req.set_tag("RF", params['roleField'])
            if 'roleIdType' in params:
                req.set_tag("RI", params['roleIdType'])
        if 'claims' in params:
            claims = []
            for claim in claims:
                values = []
                for value in claim['values']:
                    values.append(binascii.hexlify(value))
                if len(values) <= 0:
                    continue
                values = " ".join(values)
                fields = [
                    claim['claim'],
                    "1" if claim['plural'] else "0",
                    "1" if claim['requireAll'] else "0",
                    values,
                ]
                claims.append("|".join(fields))
            if len(claims) > 0:
                req.set_tag("CL", ",".join(claims))

    # LDAP Parameters
    elif args['providerType'] == 'LDAP':
        params = args['params']

        if 'lockoutThreshold' in params:
            req.set_tag("LT", params['lockoutThreshold'])
        if 'lockoutPeriod' in params:
            req.set_tag("LP", params['lockoutPeriod'])

    # TLS Parameters
    elif args['providerType'] == 'TLS':
        params = args['params']
        if 'userIdType' in params:
            req.set_tag("UT", params['userIdType'])
        if 'userField' in params:
            req.set_tag("US", params['userField'])
        if 'userOid' in params:
            req.set_tag("UO", params['userOid'])
        if 'primary' in params:
            req.set_tag("PR", "1" if params['primary'] else "0")

def define_add(blp):
    @blp.fxroute(
        endpoint="",
        method="POST",
        description="Create an identity provider",
        schema=IdentityProvider,
        resp_schemas={
            200: CreateResponse,
        })
    @perm_required("IdentityProvider:Add")
    async def add(args):
        # Create identity provider
        req = ExcryptMsg("[AORKAP;]")
        req.set_tag("OP", "add")
        args_to_rkap(req, args)

        # Send add
        rsp = await ServerConn().send_excrypt(req)
        check_error(rsp)
        idp_uuid = rsp.get_tag('ID')

        # Create auth mechanism
        req = ExcryptMsg("[AORKAM;]")
        req.set_tag("OP", "add")
        req.set_tag("PI", idp_uuid)
        args_to_rkam(req, args)

        # Send add mech
        try:
            rsp = await ServerConn().send_excrypt(req)
            check_error(rsp)
            mech_uuid = rsp.get_tag('ID')
        # Cleanup IdP if mech failed to add
        except Exception as e:
            try:
                req = ExcryptMsg("[AORKAP;]")
                req.set_tag("OP", "delete")
                req.set_tag("ID", idp_uuid)
                req.set_tag("JW", jwt)
                await ServerConn().send_excrypt(req)
            except:
                pass
            raise e

        respond(200, {'parentUuid': idp_uuid, 'uuid': mech_uuid})

def define_modify(blp):
    @blp.fxroute(
        endpoint="/<uuid>",
        method="PATCH",
        description="Change an existing identity provider",
        schema=IdentityProvider,
        )
    @perm_required("IdentityProvider:Modify")
    async def modify(args, uuid):
        # Get authentication mechanism info
        req = ExcryptMsg("[AORKAM;]")
        req.set_tag("OP", "get")
        req.set_tag("ID", uuid)
        req.set_tag("JW", AuthSession.auth_token())
        rsp = await ServerConn().send_excrypt(req)
        check_error(rsp)

        rkResult = json.loads(binascii.unhexlify(rsp.get_tag("RS")).decode('utf-8'))
        idp_uuid = rkResult['identity_provider']['uuid']

        combined_type = get_combined_type(rkResult['identity_provider']['provider_type'], rkResult['credential_type'])
        if 'providerType' in args and args['providerType'] != combined_type:
            abort(400, "Cannot change provider type of existing identity provider.")

        # Modify identity provider
        req = ExcryptMsg("[AORKAP;]")
        req.set_tag("OP", "modify")
        req.set_tag("ID", idp_uuid)
        args_to_rkap(req, args)

        # Send modify
        rsp = await ServerConn().send_excrypt(req)
        check_error(rsp)

        # Modify auth mechanism
        req = ExcryptMsg("[AORKAM;]")
        req.set_tag("OP", "modify")
        req.set_tag("ID", uuid)
        args_to_rkam(req, args)

        # Send modify mech
        rsp = await ServerConn().send_excrypt(req)
        check_error(rsp)

        respond(200)

def define_delete(blp):
    @blp.fxroute(
        endpoint="/<uuid>",
        method="DELETE",
        description="Delete an identity provider",
        )
    @perm_required("IdentityProvider:Delete")
    async def remove(uuid):
        # Get authentication mechanism info
        req = ExcryptMsg("[AORKAM;]")
        req.set_tag("OP", "get")
        req.set_tag("ID", uuid)
        req.set_tag("JW", AuthSession.auth_token())
        rsp = await ServerConn().send_excrypt(req)
        check_error(rsp)

        rkResult = json.loads(binascii.unhexlify(rsp.get_tag("RS")).decode('utf-8'))
        idp_uuid = rkResult['identity_provider']['uuid']
        idp_name = rkResult['identity_provider']['name']
        mech_name = rkResult['name']

        # Delete identity provider if both idp/mech are treated as a single object
        if idp_name == mech_name:
            req = ExcryptMsg("[AORKAP;]")
            req.set_tag("OP", "delete")
            req.set_tag("ID", idp_uuid)
        # Delete just the auth mech if they were created separately
        else:
            req = ExcryptMsg("[AORKAM;]")
            req.set_tag("OP", "delete")
            req.set_tag("ID", uuid)
        req.set_tag("JW", AuthSession.auth_token())

        # Send delete
        rsp = await ServerConn().send_excrypt(req)
        check_error(rsp)

        respond(200)
