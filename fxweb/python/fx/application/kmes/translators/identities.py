import lib.utils.hapi_parsers as parsers
from base.base_translator import BaseTranslator
from kmes.schemas import identities as schemas

import json
import binascii

def snake_to_camel_case(snake_str):
    components = snake_str.split('_')
    # Capitalize the first letter of each component except the first one
    camel_case = components[0] + ''.join(x.title() for x in components[1:])
    return camel_case

def keys_snake_to_camel(input_dict):
    if not isinstance(input_dict, dict):
        return input_dict

    output_dict = {}
    for key, value in input_dict.items():
        if isinstance(value, dict):
            # Recursively convert nested dictionaries
            value = keys_snake_to_camel(value)
        elif isinstance(value, list):
            # Recursively convert elements of lists if they are dictionaries
            value = [keys_snake_to_camel(item) if isinstance(item, dict) else item for item in value]

        new_key = snake_to_camel_case(key)
        output_dict[new_key] = value

    return output_dict

class CreateIdentity(BaseTranslator):
    request_schema = schemas.Identity(exclude=("uuid",))

    def __init__(self, server_interface):
        request_map = {
            "name": "NA",
            "passwordHex": "PX",
            "passwordChange": ("PC", parsers.serialize_bool),
            "apiKey": ("AP", parsers.serialize_bool),
            "application": ("PA", parsers.serialize_bool),
            "roles": ("RI", parsers.serialize_csv),
            "locked": ("LO", parsers.serialize_bool),
            "commonName": "CA",
            "givenName": "GA",
            "surname": "SA",
            "mobilePhone": "TX",
            "mobileCarrier": "TC",
            "email": "EM",
            "identityProvider": "AU",
        }

        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "uuid",
            "AP": "apiKey",
        }

        super().__init__(server_interface, "Identities", "RKCU", request_map, response_map)

class UpdateIdentity(BaseTranslator):
    request_schema = schemas.Identity()

    def __init__(self, server_interface):
        request_map = {
            "uuid": "ID",
            "name": "NB",
            "passwordHex": "PX",
            "passwordChange": ("PC", parsers.serialize_bool),
            "apiKey": ("AP", parsers.serialize_bool),
            "roles": ("RI", parsers.serialize_csv),
            "locked": ("LO", parsers.serialize_bool),
            "archive": ("AR", parsers.serialize_bool),
            "commonName": "CA",
            "givenName": "GA",
            "surname": "SA",
            "mobilePhone": "TX",
            "mobileCarrier": "TC",
            "email": "EM",
            "identityProvider": "AU",
        }

        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "uuid",
            "AP": "apiKey",
        }

        super().__init__(server_interface, "Identities", "RKUU", request_map, response_map)

class RetrieveIdentity(BaseTranslator):
    request_schema = schemas.Resource()

    def __init__(self, server_interface):
        request_map = {
            "uuid": "ID",
        }

        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "uuid",
            "NA": "name",
            "AP": ("application", parsers.parse_bool),
            "MR": ("management", parsers.parse_bool),
            "HD": ("hardened", parsers.parse_bool),
            "RO": ("roleNames", parsers.parse_csv),
            "RI": ("roleUuids", parsers.parse_csv),
            "LO": ("locked", parsers.parse_bool),
            "PC": "passChangedTime",
            "CP": ("passwordChange", parsers.parse_bool),
            "GA": "givenName",
            "SA": "surname",
            "CA": "commonName",
            "TX": "mobilePhone",
            "TC": "mobileCarrier",
            "EM": "email",
            "RJ": "authMechanisms",
            "AT": "authType",
            "AR": ("archive", parsers.parse_bool),
        }

        super().__init__(server_interface, "Identities", "RKRI", request_map, response_map)

    def finalize_response(self, response):
        if response.get("status") != "Y" or response.get("message"):
            return response

        # Convert role names/ids sub-csv into list of dicts
        roleNames = response['roleNames']
        roleIds = response['roleUuids']
        response.pop('roleNames')
        response.pop('roleUuids')
        roles = []
        for i in range(len(roleIds)):
            roles.append({
                'name': roleNames[i],
                'uuid': roleIds[i],
            })
        response['roles'] = roles

        # Decode auth mech info JSON
        mechInfo = binascii.unhexlify(response['authMechanisms'].encode('utf-8')).decode('utf-8')
        response['authMechanisms'] = keys_snake_to_camel(json.loads(mechInfo))['authMechanisms']

        return response

class ListIdentities(BaseTranslator):
    request_schema = schemas.ListIdentities()

    def __init__(self, server_interface):
        request_map = {
            "role": "ID",
            "roleName": "UR",
            "application": ("AP", parsers.serialize_bool),
            "management": ("MN", parsers.serialize_bool),
            "hardened": ("HD", parsers.serialize_bool),
            "search": "SE",
            "page": ("CH", (1).__rsub__),  # pages start at 1, chunks start at 0
            "pageCount": "CS",
            "archive": ("AR", parsers.serialize_bool),
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": ("identities.uuid", parsers.parse_csv),
            "DA": ("identities.username", parsers.parse_csv),
            "NA": ("identities.name", parsers.parse_csv),
            "LO": ("identities.locked", parsers.parse_csv_bool),
            "HD": ("identities.hardened", parsers.parse_csv_bool),
            "LL": ("identities.lastLogin", parsers.parse_csv),
            "RO": ("identities.roleNames", parsers.parse_csv),
            "RI": ("identities.roleUuids", parsers.parse_csv),
            "AR": ("identities.archive", parsers.parse_csv_bool),
            "CC": ("pageCount", int),
            "CT": ("totalPages", int),
            "TO": ("totalItems", int),
        }

        super().__init__(server_interface, "Identities", "RKLU", request_map, response_map)

    def finalize_response(self, response):
        if response.get("status") != "Y" or response.get("message"):
            return response

        response["currentPage"] = int(self.raw_request.get("page", 1))
        if response["currentPage"] < response["totalPages"]:
            response["nextPage"] = response["currentPage"] + 1

        # Transpose/unpivot groups from dict of lists to list of dicts:
        response["identities"] = parsers.unpivot_dict(response["identities"])

        # Convert role names/ids sub-csv into list of dicts
        for identity in response["identities"]:
            roleNames = identity['roleNames'].split('|')
            roleIds = identity['roleUuids'].split('|')
            identity.pop('roleNames')
            identity.pop('roleUuids')
            roles = []
            for i in range(len(roleIds)):
                roles.append({
                    'name': roleNames[i],
                    'uuid': roleIds[i],
                })
            identity['roles'] = roles

        return response

class DeleteIdentity(BaseTranslator):
    request_schema = schemas.Resource()

    def __init__(self, server_interface):
        request_map = {
            "uuid": "ID",
        }

        response_map = {
            "AN": "status",
            "BB": "message",
        }

        super().__init__(server_interface, "Identities", "RKDU", request_map, response_map)
