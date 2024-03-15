import lib.utils.hapi_parsers as parsers
from base.base_translator import BaseTranslator
from kmes.schemas import identities as schemas

def serialize_perms(value: list) -> str:
    by_category = {}
    for perm in value:
        perm_parts = perm.split(':')

        cat = perm_parts[0]
        perm = ""
        if len(perm_parts) == 1:
            perm = cat
        else:
            perm = perm_parts[1]
        if not cat in by_category:
            by_category[cat] = []
        by_category[cat].append(perm)

    cat_strings = []
    for cat in by_category:
        perms = by_category[cat]
        if len(perms) == 1 and perms[0] == cat:
            cat_strings.append(cat)
        else:
            cat_strings.append(cat + ":" + "|".join(perms))
    ret = ",".join(cat_strings)
    return ret

def parse_perms(perms: str) -> list:
    final_perms = []
    categories = perms.split(',')
    for cat in categories:
        catSplit = cat.split(':')
        category = catSplit[0]
        if len(catSplit) == 1:
            final_perms.append(category)
        else:
            for perm in catSplit[1].split('|'):
                if category == perm:
                    final_perms.append(category)
                else:
                    final_perms.append(category + ":" + perm)
    return final_perms


class CreateRole(BaseTranslator):
    request_schema = schemas.Role(exclude=("uuid",))

    def __init__(self, server_interface):
        request_map = {
            "name": "NA",
            "requiredLogins": "NU",
            "externalName": "LG",
            "management": ("MN", parsers.serialize_bool),
            "hardened": ("HD", parsers.serialize_bool),
            "userManagement": ("UM", parsers.serialize_bool),
            "principal": ("OO", parsers.serialize_bool),
            "ports": ("PO", parsers.serialize_csv),
            "dualFactorRequired": "DF",
            "upgradePerms": ("UP", parsers.serialize_bool),
            "permissions": ("PR", serialize_perms),
            "mgmtPermissions": ("MP", serialize_perms),
            "managedRoles": ("MI", parsers.serialize_csv),
            "externalProviders": ("PV", parsers.serialize_csv),
            "services": ("PS", parsers.serialize_csv),
        }

        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "uuid",
        }

        super().__init__(server_interface, "Roles", "RKCW", request_map, response_map)

class UpdateRole(BaseTranslator):
    request_schema = schemas.Role(exclude=('management', 'hardened', 'userManagement', 'principal'))

    def __init__(self, server_interface):
        request_map = {
            "uuid": "ID",
            "name": "NA",
            "requiredLogins": "NU",
            "externalName": "LG",
            "ports": ("PO", parsers.serialize_csv),
            "dualFactorRequired": "DF",
            "upgradePerms": ("UP", parsers.serialize_bool),
            "permissions": ("PR", serialize_perms),
            "mgmtPermissions": ("MP", serialize_perms),
            "managedRoles": ("MI", parsers.serialize_csv),
            "externalProviders": ("PV", parsers.serialize_csv),
            "services": ("PS", parsers.serialize_csv),
            "archive": ("RA", parsers.serialize_bool),
        }

        response_map = {
            "AN": "status",
            "BB": "message",
        }

        super().__init__(server_interface, "Roles", "RKEW", request_map, response_map)

class RetrieveRole(BaseTranslator):
    request_schema = schemas.Resource()

    def __init__(self, server_interface):
        request_map = {
            "uuid": "ID",
        }

        response_map = {
            "AN": "status",
            "BB": "message",
            "NA": "name",
            "ID": "uuid",
            "NU": ("requiredLogins", int),
            "MN": ("management", parsers.parse_bool),
            "HD": ("hardened", parsers.parse_bool),
            "OO": ("principal", parsers.parse_bool),
            "LG": "externalName",
            "PO": ("ports", parsers.parse_csv),
            "DF": "dualFactorRequired",
            "UP": ("upgradePerms", parsers.parse_bool),
            "PR": ("permissions", parse_perms),
            "MI": ("managedRoles.uuid", parsers.parse_csv),
            "MA": ("managedRoles.name", parsers.parse_csv),
            "MT": ("managedRoles.managedType", parsers.parse_csv),
            "PV": ("externalProviders.uuid", parsers.parse_csv),
            "PN": ("externalProviders.name", parsers.parse_csv),
            "PS": ("services.uuid", parsers.parse_csv),
            "SN": ("services.name", parsers.parse_csv),
            "SH": ("services.hardened", parsers.parse_csv_bool),
            "AR": ("archive", parsers.parse_bool),
        }

        super().__init__(server_interface, "Roles", "RKRP;NP1", request_map, response_map)

    def finalize_response(self, response):
        if response.get("status") != "Y" or response.get("message"):
            return response

        # Transpose/unpivot groups from dict of lists to list of dicts:
        response["services"] = parsers.unpivot_dict(response["services"])
        response["managedRoles"] = parsers.unpivot_dict(response["managedRoles"])
        response["externalProviders"] = parsers.unpivot_dict(response["externalProviders"])

        return response

class ListRoles(BaseTranslator):
    request_schema = schemas.ListRoles()

    def __init__(self, server_interface):
        request_map = {
            "application": ("AP", parsers.serialize_bool),
            "search": "SE",
            "page": ("CH", (1).__rsub__),  # pages start at 1, chunks start at 0
            "pageCount": "CS",
            "archive": ("AR", parsers.serialize_bool),
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": ("roles.uuid", parsers.parse_csv),
            "UR": ("roles.name", parsers.parse_csv),
            "HD": ("roles.hardened", parsers.parse_csv_bool),
            "RT": ("roles.principal", parsers.parse_csv_bool),
            "PC": ("roles.permCount", parsers.parse_csv_int),
            "PS": ("roles.serviceCount", parsers.parse_csv_int),
            "AR": ("roles.archive", parsers.parse_csv_bool),
            "CC": ("pageCount", int),
            "CT": ("totalPages", int),
            "TO": ("totalItems", int),
        }

        super().__init__(server_interface, "Roles", "RKLG", request_map, response_map)

    def finalize_response(self, response):
        if response.get("status") != "Y" or response.get("message"):
            return response

        # Calculate current/next page
        response["currentPage"] = int(self.raw_request.get("page", 1))
        if response["currentPage"] < response["totalPages"]:
            response["nextPage"] = response["currentPage"] + 1

        response["roles"] = parsers.unpivot_dict(response["roles"])

        return response

class DeleteRole(BaseTranslator):
    request_schema = schemas.Resource()

    def __init__(self, server_interface):
        request_map = {
            "uuid": "ID",
        }

        response_map = {
            "AN": "status",
            "BB": "message",
        }

        super().__init__(server_interface, "Roles", "RKDW", request_map, response_map)
