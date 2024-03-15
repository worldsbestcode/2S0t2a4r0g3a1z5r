"""
@file      kmes/translators/issuance_policies.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Translators for issuance policy views
"""

import lib.utils.hapi_parsers as parsers
from base.base_translator import BaseTranslator
from kmes.kmes_parsers import (
    parse_date,
    parse_interval,
    parse_key_types,
    serialize_date_time,
    serialize_key_types,
)
from kmes.schemas import issuance_policies as schemas
from lib.utils.container_filters import dot_notation_get
from lib.utils.hapi_excrypt_map import AsymHashTypes, RSAVerifyPadding


class CreateIssuancePolicy(BaseTranslator):
    """
    JSON to Excrypt map for creating an Issuance Policy
    """

    request_schema = schemas.IssuancePolicy(exclude=("id",))

    def __init__(self, server_interface):
        request_map = {
            "signingCertId": "PI",
            "pkiTree": "CA",
            "signingCert": "RT",
            "alias": "AL",
            "approvalGroup": "GN",
            "approvalGroupId": "GI",
            "approvalsRequired": "AP",
            "hashTypes": ("HS", lambda hashTypes: ",".join(map(AsymHashTypes.get, hashTypes))),
            "notifications.approval.enabled": ("NP", parsers.serialize_bool),
            "notifications.approval.smtpTemplate": "EA",
            "notifications.denial.enabled": ("ND", parsers.serialize_bool),
            "notifications.denial.smtpTemplate": "ED",
            "notifications.upload.enabled": ("NU", parsers.serialize_bool),
            "notifications.upload.smtpTemplate": "EU",
            "objectSigning.enabled": ("OS", parsers.serialize_bool),
            "objectSigning.paddingModes": (
                "PM",
                lambda paddingModes: ",".join(map(RSAVerifyPadding.get, paddingModes)),
            ),
            "x509Signing.enabled": ("XS", parsers.serialize_bool),
            "x509Signing.allowPkiGeneration": ("AK", parsers.serialize_bool),
            "x509Signing.allowRenewals": ("RE", parsers.serialize_bool),
            "x509Signing.extensionProfiles.name": ("EN", parsers.serialize_csv),
            "x509Signing.extensionProfiles.id": ("XI", parsers.serialize_csv),
            "x509Signing.keyTypes": ("KT", serialize_key_types),
            "x509Signing.saveCertificate": ("SK", parsers.serialize_bool),
            "x509Signing.validityPeriod.expiration": ("TU", serialize_date_time),
            "x509Signing.validityPeriod.maxDuration": ("TV", "{amount} {unit}".format_map),
            # UpdateIssuancePolicy also uses this command
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "id",
        }
        fixed_values = {"NW": 1}  # Create-only mode, do not modify if policy exists

        super().__init__(
            server_interface, "IssuancePolicies", "RAEA", request_map, response_map, fixed_values
        )

    def preprocess_request(self, request):
        ext_profiles = dot_notation_get(request, "x509Signing.extensionProfiles")
        if ext_profiles is not None:
            self._add_to_dict(
                request, "x509Signing.extensionProfiles", parsers.pivot_dict(ext_profiles), True
            )
        return request


class ListIssuancePolicies(BaseTranslator):
    """
    JSON to Excrypt map for retrieving paginated lists of Issuance Policies
    """

    request_schema = schemas.ListIssuancePolicies()

    def __init__(self, server_interface):
        request_map = {
            "permission": "PM",
            "pkiTree": "CA",
            "pkiTreeId": "AI",
            "parent": "CT",
            "parentId": "PI",
            "x509Signing": ("AX", parsers.serialize_bool),
            "objectSigning": ("AS", parsers.serialize_bool),
            "pkiGeneration": ("AP", parsers.serialize_bool),
            "page": ("CH", (1).__rsub__),  # pages start at 1, chunks start at 0
            "pageCount": "CS",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": ("policies.id", parsers.parse_csv),
            "PI": ("policies.signingCertId", parsers.parse_csv),
            "CN": ("__ca_and_name", parsers.parse_csv),
            "CC": ("pageCount", int),
            "CT": ("totalPages", int),
            "TO": ("totalItems", int),
        }

        super().__init__(server_interface, "IssuancePolicies", "RAFA", request_map, response_map)

    def finalize_response(self, response):
        if response.get("status") != "Y" or response.get("message"):
            return response

        response["currentPage"] = int(self.raw_request.get("page", 1))
        if response["currentPage"] < response["totalPages"]:
            response["nextPage"] = response["currentPage"] + 1

        # Transpose/unpivot groups from dict of lists to list of dicts:
        response["policies"] = parsers.unpivot_dict(response["policies"])

        # CN looks like "ca1name:cert1name,ca1name:cert2name,ca2name:cert1name"
        for policy, cert in zip(response["policies"], response.pop("__ca_and_name")):
            policy["pkiTree"], policy["signingCert"] = cert.split(":")

        return response


class RetrieveIssuancePolicy(BaseTranslator):
    """
    JSON to Excrypt map for retrieving an Issuance Policy
    """

    request_schema = schemas.RetrieveIssuancePolicy()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "signingCertId": "PI",
            "pkiTree": "CA",
            "signingCert": "RT",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "id",
            "AL": "alias",
            "PI": "signingCertId",
            "GI": "approvalGroupId",
            "AP": ("approvalsRequired", int),
            "HS": ("hashTypes", lambda hs: [*map(AsymHashTypes.get_reverse, hs.split(","))]),
            "NP": ("notifications.approval.enabled", parsers.parse_bool),
            "EA": ("notifications.approval.smtpTemplate", lambda ea: "" if ea == "None" else ea),
            "ND": ("notifications.denial.enabled", parsers.parse_bool),
            "ED": ("notifications.denial.smtpTemplate", lambda ed: "" if ed == "None" else ed),
            "NU": ("notifications.upload.enabled", parsers.parse_bool),
            "EU": ("notifications.upload.smtpTemplate", lambda eu: "" if eu == "None" else eu),
            "OS": ("objectSigning.enabled", parsers.parse_bool),
            "PM": (
                "objectSigning.paddingModes",
                lambda pm: [*map(RSAVerifyPadding.get_reverse, pm.split(","))],
            ),
            "XS": ("x509Signing.enabled", parsers.parse_bool),
            "AK": ("x509Signing.allowPkiGeneration", parsers.parse_bool),
            "RE": ("x509Signing.allowRenewals", parsers.parse_bool),
            "XI": ("x509Signing.extensionProfiles.id", parsers.parse_csv),
            "EN": ("x509Signing.extensionProfiles.name", parsers.parse_csv),
            "KT": ("x509Signing.keyTypes", parse_key_types),
            "SK": ("x509Signing.saveCertificate", parsers.parse_bool),
            "TU": ("x509Signing.validityPeriod.expiration", parse_date),
            "TV": ("x509Signing.validityPeriod.maxDuration", parse_interval),
        }

        super().__init__(server_interface, "IssuancePolicies", "RAGA", request_map, response_map)

    def finalize_response(self, response):
        ext_profiles = dot_notation_get(response, "x509Signing.extensionProfiles")
        if ext_profiles is not None:
            response["x509Signing"]["extensionProfiles"] = parsers.unpivot_dict(ext_profiles)
        return super().finalize_response(response)


class UpdateIssuancePolicy(BaseTranslator):
    """
    JSON to Excrypt map for updating an Issuance Policy
    """

    request_schema = schemas.IssuancePolicy()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "signingCertId": "PI",
            "pkiTree": "CA",
            "signingCert": "RT",
            "alias": "AL",
            "approvalGroup": "GN",
            "approvalGroupId": "GI",
            "approvalsRequired": "AP",
            "hashTypes": ("HS", lambda hashTypes: ",".join(map(AsymHashTypes.get, hashTypes))),
            "notifications.approval.enabled": ("NP", parsers.serialize_bool),
            "notifications.approval.smtpTemplate": "EA",
            "notifications.denial.enabled": ("ND", parsers.serialize_bool),
            "notifications.denial.smtpTemplate": "ED",
            "notifications.upload.enabled": ("NU", parsers.serialize_bool),
            "notifications.upload.smtpTemplate": "EU",
            "objectSigning.enabled": ("OS", parsers.serialize_bool),
            "objectSigning.paddingModes": (
                "PM",
                lambda paddingModes: ",".join(map(RSAVerifyPadding.get, paddingModes)),
            ),
            "x509Signing.enabled": ("XS", parsers.serialize_bool),
            "x509Signing.allowPkiGeneration": ("AK", parsers.serialize_bool),
            "x509Signing.allowRenewals": ("RE", parsers.serialize_bool),
            "x509Signing.extensionProfiles.name": ("EN", parsers.serialize_csv),
            "x509Signing.extensionProfiles.id": ("XI", parsers.serialize_csv),
            "x509Signing.keyTypes": ("KT", serialize_key_types),
            "x509Signing.saveCertificate": ("SK", parsers.serialize_bool),
            "x509Signing.validityPeriod.expiration": ("TU", serialize_date_time),
            "x509Signing.validityPeriod.maxDuration": ("TV", "{amount} {unit}".format_map),
            # CreateIssuancePolicy also uses this command
        }
        response_map = {
            "AN": "status",
            "BB": "message",
            "ID": "id",
        }
        fixed_values = {"NW": 2}  # Update-only mode, do not create if non-exist

        super().__init__(
            server_interface, "IssuancePolicies", "RAEA", request_map, response_map, fixed_values
        )

    def preprocess_request(self, request):
        ext_profiles = dot_notation_get(request, "x509Signing.extensionProfiles")
        if ext_profiles is not None:
            self._add_to_dict(
                request, "x509Signing.extensionProfiles", parsers.pivot_dict(ext_profiles), True
            )
        return request


class DeleteIssuancePolicy(BaseTranslator):
    """
    JSON to Excrypt map for deleting an issuance policy
    """

    request_schema = schemas.RetrieveIssuancePolicy()

    def __init__(self, server_interface):
        request_map = {
            "id": "ID",
            "signingCertId": "PI",
            "signingCert": "RT",
            "pkiTree": "CA",
        }
        response_map = {
            "AN": "status",
            "BB": "message",
        }

        super().__init__(server_interface, "IssuancePolicies", "RADA", request_map, response_map)
