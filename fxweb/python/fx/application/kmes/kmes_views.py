"""
@file      kmes/kmes_views.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE
This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2019

@section DESCRIPTION
Implements the URIs for the KMES views
"""

import typing

from regauth import regauth_views

from .views import (
    approval_groups,
    approval_requests,
    certificate_signing,
    certificates,
    crls,
    crypto,
    extension_profiles,
    features,
    gcse_views,
    identities,
    issuance_policies,
    keys,
    login,
    logout,
    object_signing,
    pki_generation,
    pki_trees,
    roles,
    system,
    tlsprofiles,
    token_profiles,
    web_server,
)

if typing.TYPE_CHECKING:
    from flask.views import MethodView

    from base.global_container import GlobalContainer


def map_views(program: "GlobalContainer") -> typing.Dict[str, "MethodView"]:

    views_by_version = {
        8: {
            "/identities": identities.Identities,
            "/identities/<uuid>": identities.IdentityResource,
            "/roles": roles.Roles,
            "/roles/<uuid>": roles.RoleResource,
            "/tls-profiles": tlsprofiles.TlsProfiles,
            "/tls-profiles/<uuid>": tlsprofiles.TlsProfileResource,
        },
        7: {
            "/approval-groups": approval_groups.ApprovalGroups,
            "/approval-groups/permissions": approval_groups.Permissions,
            "/certificates": certificates.Certificate,
            "/certificates/aliases": certificates.CertificateAlias,
            "/certificates/archive": certificates.CertificateArchiveRestore,
            "/certificates/restore": certificates.CertificateArchiveRestore,
            "/certificates/emv": certificates.EmvCert,
            "/certificates/import": certificates.CertificateImport,
            "/certificates/permissions": certificates.CertPermissions,
            "/crls": crls.Crl,
            "/crls/export": crls.ImportExport,
            "/crls/import": crls.ImportExport,
            "/crls/revoke": crls.RevokeCertificate,
            "/crypto/decrypt": crypto.Decrypt,
            "/crypto/encrypt": crypto.Encrypt,
            "/crypto/random": crypto.Random,
            "/crypto/sign": crypto.Sign,
            "/crypto/verify": crypto.Verify,
            "/extension-profiles": extension_profiles.X509ExtensionProfiles,
            "/extension-profiles/permissions": extension_profiles.X509ExtensionPermissions,
            "/features": features.Features,
            "/issuance-policies": issuance_policies.IssuancePolicy,
            "/keys": keys.Keys,
            "/keys/export": keys.KeyExport,
            "/keys/import": keys.ImportKeys,
            "/login": login.Login,
            "/logout": logout.Logout,
            "/pki-trees": pki_trees.PkiTree,
            "/pki-trees/permissions": pki_trees.PkiTreePermissions,
            "/ra-requests": approval_requests.ApprovalReq,
            "/ra-requests/approve": approval_requests.ApproveRequest,
            "/ra-requests/deny": approval_requests.DenyRequest,
            "/ra-requests/renew": approval_requests.RenewRequest,
            "/ra-requests/revoke": approval_requests.RevokeRequest,
            "/ra-requests/certificate-signing": certificate_signing.CertSigningRequests,
            "/ra-requests/object-signing": object_signing.ObjectSigningRequests,
            "/ra-requests/pki-generation": pki_generation.PkiGenerationRequests,
            "/system/autobackup": system.AutoBackup,
            "/system/certificates": system.Certificates,
            "/system/ntp": system.Ntp,
            "/system/permissions": system.GlobalPermissions,
            "/system/ra-settings": system.RaSettings,
            "/system/security/modes": system.SecureMode,
            "/token-profiles": token_profiles.TokenProfile,
            "/token-profiles/permissions": token_profiles.Permissions,
            "/token-profiles/tokenize": token_profiles.Tokenize,
            "/token-profiles/detokenize": token_profiles.Detokenize,
            "/token-profiles/verify": token_profiles.VerifyToken,
            "/web-server": web_server.WebServer,
            "/web-server/restart": web_server.Restart,
        },
        # Legacy RA Web Endpoints
        6: {
            "/certificates": regauth_views.RAPKIView,
            "/certificates/export": regauth_views.RAExportCertificateView,
            "/certificates/import": regauth_views.RAImportCertificateView,
            "/certificates/ecc-decrypt": regauth_views.RAPKIECCDecryptView,
            "/certificates/ecc-encrypt": regauth_views.RAPKIECCEncryptView,
            "/certificates/ecc-sign": regauth_views.RAPKISignView,
            "/certificates/ecc-verify": regauth_views.RAPKIECCVerifyView,
            "/certificates/rsa-decrypt": regauth_views.RAPKIRSADecryptView,
            "/certificates/rsa-encrypt": regauth_views.RAPKIRSAEncryptView,
            "/certificates/rsa-sign": regauth_views.RAPKISignView,
            "/certificates/rsa-verify": regauth_views.RAPKIRSAVerifyView,
            "/certificates/signing-requests": regauth_views.RAPKIRequestView,
            "/dn-profiles": regauth_views.RADNProfileView,
            "/echo": regauth_views.RAEchoView,
            "/keys": regauth_views.RAKeysView,
            "/keys/decrypt": regauth_views.RAKeysDecryptView,
            "/keys/encrypt": regauth_views.RAKeysEncryptView,
            "/login": login.Login,
            "/logout": logout.Logout,
            "/token-profiles/detokenize": token_profiles.Detokenize,
            "/token-profiles/tokenize": token_profiles.Tokenize,
            "/token-profiles/verify": token_profiles.VerifyToken,
        },
    }

    # Google CSE
    views_full_path_override = {
        "/v0/key-encrypt/client/<csecommand>": gcse_views.GCSECommandView,
    }

    # {6:{'/login': Login}} -> {'/kmes/v6/login': Login}
    combined_views = {}
    api_prefix = "/kmes"
    for version, views in views_by_version.items():
        for path, view_class in views.items():
            path = path.strip("/")
            combined_path = f"/{api_prefix}/v{version}/{path}"
            combined_views[combined_path] = view_class

    combined_views.update(views_full_path_override)
    return combined_views
