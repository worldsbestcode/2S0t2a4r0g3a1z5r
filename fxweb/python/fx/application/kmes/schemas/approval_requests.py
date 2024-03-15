"""
@file      kmes/schemas/approval_requests.py
@author    Dalton McGee (dmcgee@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Request validation schemas for Approval Requests
"""

from marshmallow import Schema, fields, pre_load

from lib.utils.hapi_excrypt_map import RevocationReasons

from .shared_schemas import (
    Enum,
    LdapLoginMixin,
    PaginationMixin,
    RequestId,
    UniqueId,
    require_at_least_one,
)


class ListApprovalRequests(PaginationMixin, Schema):
    _object_filters = ["x509", "objectSigning"]
    _status_filters = ["pending", "signed", "approved", "denied"]

    approvalGroupId = UniqueId()
    signed = fields.Boolean(missing=False)
    pending = fields.Boolean(missing=False)
    denied = fields.Boolean(missing=False)
    approved = fields.Boolean(missing=False)
    x509 = fields.Boolean(missing=False)
    objectSigning = fields.Boolean(missing=False)

    @pre_load()
    def set_filter(self, data, **kwargs):
        # First check Object filters
        # Set all Object filters to true if none are supplied
        if not any(filter_ in data.keys() for filter_ in self._object_filters):
            for filter_ in self._object_filters:
                if filter_ in self.declared_fields:
                    data.update({filter_: True})

        # Second check Status filters
        # Set all Status filters to true if none are supplied
        if not any(filter in data.keys() for filter in self._status_filters):
            data.update({filter: True for filter in self._status_filters})

        return data


class DeleteApprovalRequest(Schema):
    requestId = RequestId(required=True)


class ApproveDenyApprovalRequest(Schema):
    requestId = RequestId()
    requestIds = fields.List(RequestId())
    approve = fields.Boolean(required=True)
    notes = fields.String()

    require_at_least_one("requestId", "requestIds")


class RenewRequest(LdapLoginMixin, Schema):
    requestId = RequestId(required=True)


class RevokeRequest(LdapLoginMixin, Schema):
    requestId = RequestId(required=True)
    reason = Enum(
        RevocationReasons,
        exclude=[
            RevocationReasons.unused,
            RevocationReasons.remove_from_crl,
            RevocationReasons.certificate_hold,
        ],
        required=True,
    )
    details = fields.String()
