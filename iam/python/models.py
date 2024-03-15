from typing import Union, List
from marshmallow import fields, validate
from rkweb.lilmodels.base import Model, field

def get_combined_type(provider_type: str, mech_type: str) -> str:
    if provider_type == "LDAP":
        return "LDAP"
    if provider_type == "Certificate Authority":
        if mech_type == "TLS Certificate":
            return "TLS"
        return "PKI"
    if provider_type == "JWT":
        return "JWT"
    if provider_type == "Futurex Application":
        return mech_type
    if provider_type == "Futurex HSM":
        return "Hardened " + mech_type
    return provider_type + ":" + mech_type

def get_provider_type(combined_type: str) -> str:
    if combined_type == "LDAP":
        return "LDAP"
    if combined_type == "PKI" or combined_type == "TLS":
        return "Certificate Authority"
    if combined_type == "JWT":
        return "JWT"
    if combined_type.startwith("Hardened "):
        return "Futurex HSM"
    if ":" in combined_type:
        return combined_type[0:combined_type.find(":")]
    return "Futurex Application"

def get_mech_type(combined_type: str) -> str:
    if combined_type == "LDAP":
        return "Remote Password"
    if combined_type == "TLS":
        return "TLS Certificate"
    if combined_type == "PKI":
        return "PKI Certificate"
    if combined_type == "JWT":
        return "JSON Web Token"
    if combined_type.startswith("Hardened "):
        return combined_type[9:]
    if ":" in combined_type:
        return combined_type[combined_type.find(":") + 1:]
    return combined_type

providerTypeValidator = validate.OneOf([
    "Password",
    "Hardened Password",
    "API Key",
    "Hardened API Key",
    "Smart Card",
    "Hardened Smart Card",
    "FIDO Token",
    "Hardened FIDO Token",
    "One Time Password",
    "Hardened One Time Password",
    "PKI",
    "TLS",
    "LDAP",
    "JWT",
])
userIdTypeValidator = validate.OneOf(["Username","Email","UUID"])
roleIdTypeValidator = validate.OneOf(["Name","UUID","External Name"])

class JwtAuthorizedRole(Model):
    uuid: str = field(description="UUID of role that will be authorized")
    name: str = field(description="Name of role that will be authorized")

class JwtClaim(Model):
    claim: str = field(description="Claim string")

    plural: bool = field(
        description="Whether claim can be plural",
        required=False,
        load_default=False)

    values: List[str] = field(
        description="Possible values to match against")

    requireAll: bool = field(
        description="Whether all claim values must exist",
        required=False,
        load_default=False)

class IdentityProviderJwtParams(Model):
    jwtAuthType: str = field(
        description="Authentication type",
        required=True,
        marshmallow_field=fields.String(
            validate=validate.OneOf(["HMAC","PKI","URL"]),
        )
    )

    issuer: str = field(description="JWT iss field")

    maxValidity: str = field(
        description="Max validity to enforce (if any). Requires iss in token if max validity is set.",
        required=False,
        load_default=None)

    leeway: int = field(
        description="How many seconds leeway to allow on issue/expiration times.",
        required=False,
        load_default=0)

    jwksUrl: str = field(
        description="JWKS URL for URL type authentication",
        required=False,
        load_default=None)

    jwksTlsCa: str = field(
        description="JWKS TLS verify CA",
        required=False,
        load_default=None)

    hmacKey: str = field(
        description="Base64 encoded key for HMAC type authentication",
        required=False,
        load_default=None,
        load_only=True)

    pkiVerifyCert: str = field(
        description="PKI signed JWT verify certificate",
        required=False,
        load_default=None)

    userField: str = field(
        description="Claim that contains the user's identifier",
        required=False,
        load_default="sub")

    userIdType: str = field(
        description="What user identifier to match against the user claim",
        required=False,
        load_default="Username",
        marshmallow_field=fields.String(
            validate=userIdTypeValidator,
            required=False,
            missing="Username",
        )
    )

    rolesFromToken: bool = field(
        description="Use the token to match against roles",
        required=False,
        load_default=False)

    roleField: str = field(
        description="The token claim that contains the logged in roles",
        required=False,
        load_default="roles")

    roleIdType: str = field(
        description="What role identifier to match against the roles claim",
        required=False,
        load_default="Name",
        marshmallow_field=fields.String(
            validate=roleIdTypeValidator,
            required=False,
            missing="Name",
        )
    )

    authorizedRoles: List[JwtAuthorizedRole] = field(
        description="If not taking roles from the token, these are the roles that will get authorized by the token. "
                    "This list is taken from the external identity providers mapping on the role",
        required=False,
        #dump_only=True,
        load_default=None)

    claims: List[JwtClaim] = field(
        description="Required claims",
        required=False,
        load_default=None)

class IdentityProviderLdapParams(Model):

    servers: List[str] = field(
        description="LDAP URLs for server and backup addresses",
        required=True)

    tlsProfile: str = field(
        description="UUID of TLS profile for LDAPS connections",
        required=False,
        load_default=None)

    ldapTlsCa: str = field(
        description="TLS verify CA",
        required=False,
        load_default=None)

    ldapVersion: int = field(
        description="LDAP protocol version (Likely 3)",
        required=False,
        load_default=3)

    adminUser: str = field(
        description="DN of Admin user required for 'Search DN' lookup method",
        required=False,
        load_default=None)

    adminPasswordHex: str = field(
        description="Hex encoded admin user login password",
        required=False,
        load_default=None,
        load_only=True)

    lookupMethod: str = field(
        description="How to lookup the user logging in\n"
                    "Search DN: Search within the user base DN (required admin login)\n"
                    "Direct DN: Assume the user is directly under the user base DN and RDN is just the user field\n"
                    "ANR: Ambiguous Name Resolution",
        required=False,
        load_default="Search DN",
        marshmallow_field=fields.String(
            validate=validate.OneOf(["Search DN","Direct DN", "ANR"]),
            required=False,
            missing="Search DN",
        )
    )

    loginMode: str = field(
        description="Password authentication mechanism.\n"
                    "Simple, DIGEST-MD5",
        required=False,
        load_default="Simple",
        marshmallow_field=fields.String(
            validate=validate.OneOf(["Simple", "DIGEST-MD5"]),
            required=False,
            missing="Simple",
        )
    )

    userBaseDn: str = field(description="The base DN all users are under")

    userField: str = field(
        description="The LDAP attribute to match users against",
        required=False,
        load_default="cn")

    userIdType: str = field(
        description="What user identifier to match against the LDAP user attribute",
        required=False,
        load_default="Username",
        marshmallow_field=fields.String(
            validate=userIdTypeValidator,
            requied=False,
            missing="Username",
        )
    )

    memberOfField: str = field(
        description="User attribute that describes their roles",
        required=False,
        load_default="memberOf")

    roleBaseDn: str = field(
        description="Base DN to search for roles under",
        required=False,
        load_default=None)

    roleField: str = field(
        description="Role attribute that matches role identifier",
        required=False,
        load_default="ou")

    roleIdType: str = field(
        description="What role identifier to match against the LDAP role's attribute",
        required=False,
        load_default="Name",
        marshmallow_field=fields.String(
            validate=roleIdTypeValidator,
            required=False,
            missing="Name",
        )
    )

    memberField: str = field(
        description="Role attribute that describes who is in the role",
        required=False,
        load_default="member")

    lockoutThreshold: int = field(
        description="How many wrong attempts before lockout",
        required=False,
        load_default=3)

    lockoutPeriod: str = field(
        description="How long to lockout after too many failed attempts",
        required=False,
        load_default="20 Seconds")

class IdentityProviderPkiParams(Model):
    caCertificate: str = field(
        description="UUID of CA certificate that signs the identity endpoint certificates",
        required=True)

    userSource: str = field(
        description="Which certificate field to match against the user identifier",
        required=False,
        load_default="Subject-CN",
        marshmallow_field=fields.String(
            validate=validate.OneOf([
                "Subject-CN",
                "Subject-Email",
                "Subject-Custom",
                "SANs-Email",
                "SANs-DN-CN",
                "SANs-DN-Email",
                "SANs-DN-Custom",
                "SANs-OtherName",
            ]),
            required=False,
            missing="Subject-CN",
        )
    )

    userIdType: str = field(
        description="What user identifier to match against the certificate value",
        required=False,
        load_default="Username",
        marshmallow_field=fields.String(
            validate=userIdTypeValidator,
            required=False,
            missing="Username",
        )
    )

    userOid: str = field(
        description="DN field OID of entry for Custom Subject/SANs user ID type",
        required=False,
        load_default=None)

    primary: bool = field(
        description="Primary method of authentication or second factor",
        required=False,
        load_default=True)

class IdentityProvider(Model):
    uuid: str = field(
        description="UUID of identity provider",
        required=False,
        #dump_only=True,
        load_missing=None)

    name: str = field(description="Name of the identity provider")

    providerType: str = field(
        description="Type of identity provider",
        marshmallow_field=fields.String(validate=providerTypeValidator),
    )

    allowExternal: bool = field(
        description="If users that don't exist on this system can authenticate",
        required=False,
        load_default=False)

    unionRoles: bool = field(
        description="If users on this system authenticate, and the mechanism also contains roles. Union or intersect the roles?",
        required=False,
        load_default=False)

    enforceDualFactor: bool = field(
        description="If authenticating a local identity with this mechanism, does dual-factor policy still need to be enforced?",
        required=False,
        load_default=True)

    _discriminator = {
        'propertyname': 'providerType',
        'mapping': {
            "JWT": IdentityProviderJwtParams,
            "LDAP": IdentityProviderLdapParams,
            "PKI": IdentityProviderPkiParams,
            "TLS": IdentityProviderPkiParams,
        }
    }

    params: Union[
        IdentityProviderJwtParams,
        IdentityProviderLdapParams,
        IdentityProviderPkiParams
    ] = field(discriminator=_discriminator)


class IdentityProviderStub(Model):
    uuid: str = field(description="UUID of identity provider")
    name: str = field(description="Name of the identity provider")
    providerType: str = field(
        description="Type of identity provider",
        marshmallow_field=fields.String(validate=providerTypeValidator)
    )

class IdentityProviderList(Model):
    results: List[IdentityProviderStub] = field(
        description="The page of results",
        marshmallow_field=fields.List(
            fields.Nested(IdentityProviderStub.schema)
        )
    )

class CreateResponse(Model):
    uuid: str = field(description="UUID of the newly created identity provider")
