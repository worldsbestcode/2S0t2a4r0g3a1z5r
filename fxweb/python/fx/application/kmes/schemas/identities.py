from marshmallow import Schema
from marshmallow.fields import Boolean, DateTime, Integer, List, Nested, String
from marshmallow.validate import OneOf, Range

from .shared_schemas import (
    PaginationMixin,
    StringEnum,
    UniqueId,
)

class Identity(Schema):
    uuid = UniqueId()
    name = String()
    passwordHex = String()
    passwordChange = Boolean()
    apiKey = Boolean()
    application = Boolean()
    roles = List(UniqueId())
    locked = Boolean()
    archive = Boolean()
    commonName = String()
    givenName = String()
    surname = String()
    mobilePhone = String()
    mobileCarrier = StringEnum([
        "None",
        "ATT",
        "Alltell",
        "Boost",
        "Comcast",
        "MTNGroup",
        "Qwest",
        "Rogers",
        "Sprint",
        "Tmobile",
        "Trac",
        "Verizon",
        "Virgin",
        "Vodacom",
    ])
    email = String()
    identityProvider = UniqueId()

class ListIdentities(PaginationMixin, Schema):
    role = UniqueId()
    roleName = String()
    application = Boolean()
    management = Boolean()
    hardened = Boolean()
    search = String()
    archive = Boolean()

class ListRoles(PaginationMixin, Schema):
    application = Boolean()
    search = String()
    archive = Boolean()

class Role(Schema):
    uuid = UniqueId()
    name = String()
    requiredLogins = Integer()
    externalName = String()
    management = Boolean()
    hardened = Boolean()
    userManagement = Boolean()
    principal = Boolean()
    ports = List(String())
    dualFactorRequired = StringEnum([
        "Never",
        "Available",
        "Always",
    ])
    upgradePerms = Boolean()
    permissions = List(String())
    mgmtPermissions = List(String())
    managedRoles = List(UniqueId())
    externalProviders = List(UniqueId())
    services = List(UniqueId())
    archive = Boolean()

class Resource(Schema):
    uuid = UniqueId()
