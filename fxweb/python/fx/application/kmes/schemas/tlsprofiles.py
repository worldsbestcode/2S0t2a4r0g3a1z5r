from marshmallow import Schema
from marshmallow.fields import Boolean, DateTime, Integer, List, Nested, String
from marshmallow.validate import OneOf, Range

from .shared_schemas import (
    PaginationMixin,
    StringEnum,
    UniqueId,
)

class TlsProfile(Schema):
    uuid = UniqueId()
    name = String()
    certType = StringEnum([
        "User",
        "Generated",
        "FxCerts",
        "ServerAuth",
    ])
    certUuid = UniqueId()
    trustedCertUuids = List(UniqueId())
    anonymous = Boolean()
    fxcertsType = StringEnum([
        "RSA Prod",
        "RSA Admin",
        "ECC Prod",
        "ECC Admin",
    ])
    generatedType = StringEnum([
        "RSA",
        "ECC",
    ])
    sslAsTrusted = Boolean()
    ciphers = List(String())
    protocols = List(StringEnum([
        "TLSv1.0",
        "TLSv1.1",
        "TLSv1.2",
        "TLSv1.3",
    ]))

class ListTlsProfiles(PaginationMixin, Schema):
    ...

class Resource(Schema):
    uuid = UniqueId()
