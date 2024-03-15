"""

@file      kmes/translators/system.py
@author    Jamal Al(jal@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translators defined for the System method view
"""

from marshmallow import ValidationError

from base.base_translator import BaseTranslator
from kmes.kmes_parsers import parse_weekdays, serialize_weekdays
from kmes.schemas import system as schemas
from lib.utils import hapi_parsers as parsers


class RetrieveAutoBackup(BaseTranslator):
    """
    JSON to Excrypt map to get the info of autobackup.
    """

    request_schema = None

    def __init__(self, server_interface):
        fixed_values = {
            "OP": "automated_backup:get",
        }

        response_map = {
            "AN": "status",
            "BB": "message",
            "EN": ("enabled", parsers.parse_bool),
            "WK": ("frequency", int),
            "WD": ("weekDays", parse_weekdays),
            "DT": "lastBackupDate",
            "MI": ("storageMirrors", parsers.parse_csv),
        }
        super().__init__(
            server_interface, "System", "SETT", response_map=response_map, fixed_values=fixed_values
        )


class UpdateAutoBackup(BaseTranslator):
    """
    JSON to Excrypt map to update info of autobackup.
    """

    request_schema = schemas.UpdateAutoBackup()

    def __init__(self, server_interface):
        fixed_values = {
            "OP": "automated_backup:modify",
        }

        request_map = {
            "enabled": ("EN", parsers.serialize_bool),
            "beginDate": "DT",
            "frequency": "WK",
            "weekDays": ("WD", serialize_weekdays),
            "storageMirrors": ("MI", parsers.serialize_csv),
        }
        response_map = {
            "AN": "status",
            "BB": "message",
        }

        super().__init__(
            server_interface, "System", "SETT", request_map, response_map, fixed_values=fixed_values
        )


class RetrieveCertificates(BaseTranslator):
    request_schema = None

    def __init__(self, server_interface):
        fixed_values = {"OP": "x509:get"}

        response_map = {
            "AN": "status",
            "BB": "message",
            "CS": ("pkiCacheSize", int),
            "NO": ("expireNotification", int),
            "CN": ("allowDuplicateNames", parsers.parse_bool),
            "NV": ("allowInvalidCerts", parsers.parse_bool),
            "SE": ("appendRandom64Bit", parsers.parse_bool),
        }

        super().__init__(
            server_interface, "System", "SETT", response_map=response_map, fixed_values=fixed_values
        )


class UpdateCertificates(BaseTranslator):
    request_schema = schemas.UpdateCertificates()

    def __init__(self, server_interface):
        fixed_values = {"OP": "x509:modify"}

        request_map = {
            "pkiCacheSize": "CS",
            "expireNotification": "NO",
            "allowDuplicateNames": ("CN", parsers.serialize_bool),
            "allowInvalidCerts": ("NV", parsers.serialize_bool),
            "appendRandom64Bit": ("SE", parsers.serialize_bool),
        }

        response_map = {"AN": "status", "BB": "message"}

        super().__init__(
            server_interface, "System", "SETT", request_map, response_map, fixed_values
        )


class RetrieveGlobalPermissions(BaseTranslator):
    """
    JSON to Excrypt map to get system global permissions.
    """

    request_schema = None

    def __init__(self, server_interface):

        fixed_values = {
            "OP": "global_permissions:get",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "PM": ("permissions.types", parsers.parse_csv),
            "PD": ("permissions.descriptions", parsers.parse_csv),
            "PS": ("permissions.setting", parsers.parse_csv),
            "PP": ("permissions.settingOptions", parsers.parse_csv_list),
        }
        super().__init__(
            server_interface, "System", "SETT", response_map=response_map, fixed_values=fixed_values
        )

    def finalize_response(self, response):
        if not response.success:
            return response

        response["permissions"] = parsers.unpivot_dict(response["permissions"])
        return response


class UpdateGlobalPermissions(BaseTranslator):
    """
    Update system global permissions
    """

    request_schema = schemas.UpdateGlobalPermissions()

    def __init__(self, server_interface):
        fixed_values = {
            "OP": "global_permissions:modify",
        }
        request_map = {
            "types": ("PM", parsers.serialize_csv),
            "settings": ("PS", parsers.serialize_csv),
        }

        response_map = {"AN": "status", "BB": "message"}
        super().__init__(
            server_interface, "System", "SETT", request_map, response_map, fixed_values
        )

    def preprocess_request(self, request):
        perms = self.server_interface.send_command("System", "internal_cached_perm_options", {})
        permissions = {
            name: options
            for name, options in zip(perms["PM"].split(","), parsers.parse_csv_list(perms["PP"]))
        }

        types, settings = [], []
        for perm in request.get("permissions", []):
            _type, setting = perm["type"], perm["setting"]

            if _type not in permissions:
                raise ValidationError(f"Invalid option {_type}")

            if setting not in permissions[_type]:
                choices = ",".join(permissions[_type])
                raise ValidationError(f"Must be one of {choices}")

            types.append(_type)
            settings.append(setting)

        request["types"] = types
        request["settings"] = settings
        return request


class RetrieveNtp(BaseTranslator):
    """
    JSON to Excrypt map to get the info of ntp.
    """

    request_schema = None

    def __init__(self, server_interface):
        fixed_values = {"OP": "ntp:get"}

        response_map = {
            "AN": "status",
            "BB": "message",
            "EN": ("enabled", parsers.parse_bool),
            "OS": ("syncOnStartup", parsers.parse_bool),
            "HL": ("host", parsers.parse_csv),
        }

        super().__init__(
            server_interface, "System", "SETT", response_map=response_map, fixed_values=fixed_values
        )


class UpdateNtp(BaseTranslator):
    """
    Edit information of ntp.
    """

    request_schema = schemas.UpdateNtp()

    def __init__(self, server_interface):
        fixed_values = {"OP": "ntp:modify"}

        request_map = {
            "enabled": ("EN", parsers.serialize_bool),
            "syncOnStartup": ("OS", parsers.serialize_bool),
            "host": ("HL", parsers.serialize_csv),
        }

        response_map = {"AN": "status", "BB": "message"}
        super().__init__(
            server_interface, "System", "SETT", request_map, response_map, fixed_values
        )


class RetrieveRaSettings(BaseTranslator):
    request_schema = None

    def parse_approval_type(self, value):
        return "User" if parsers.parse_bool(value) else "Group"

    def __init__(self, server_interface):
        fixed_values = {
            "OP": "regauth:get",
        }

        response_map = {
            "AN": "status",
            "BB": "message",
            "AL": ("allowAnonymous", parsers.parse_bool),
            "AW": ("anonymousWcce", parsers.parse_bool),
            "WP": "wccePolicy",
        }

        super().__init__(
            server_interface, "System", "SETT", response_map=response_map, fixed_values=fixed_values
        )


class UpdateRaSettings(BaseTranslator):
    request_schema = schemas.UpdateRaSettings()

    def serialize_approval_type(self, value):
        return 1 if value == "USER" else 0

    def __init__(self, server_interface):
        fixed_values = {
            "OP": "regauth:modify",
        }

        request_map = {
            "allowAnonymous": ("AL", parsers.serialize_bool),
            "anonymousWcce": ("AW", parsers.serialize_bool),
            "wccePolicy": "WP",
        }

        response_map = {"AN": "status", "BB": "message"}

        super().__init__(
            server_interface, "System", "SETT", request_map, response_map, fixed_values
        )


class RetrieveSecureMode(BaseTranslator):
    request_schema = None

    def __init__(self, server_interface):
        fixed_values = {
            "OP": "secure_mode:get",
        }

        response_map = {
            "AN": "status",
            "BB": "message",
            "FM": ("fips", parsers.parse_bool),
            "PC": ("pci", parsers.parse_bool),
        }

        super().__init__(
            server_interface, "System", "SETT", response_map=response_map, fixed_values=fixed_values
        )


class UpdateSecureMode(BaseTranslator):
    request_schema = schemas.UpdateSecureMode()

    def __init__(self, server_interface):
        fixed_values = {
            "OP": "secure_mode:modify",
        }

        request_map = {
            "fips": ("FM", parsers.serialize_bool),
            "pci": ("PC", parsers.serialize_bool),
        }

        response_map = {
            "AN": "status",
            "BB": "message",
            "JI": "jobId",
        }

        super().__init__(
            server_interface, "System", "SETT", request_map, response_map, fixed_values
        )
