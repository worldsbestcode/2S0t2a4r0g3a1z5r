import os

from typing import List

from rkweb.lilmodels.base import Model, field

from rkweb.auth import login_required
from rkweb.config import WebConfig
from rkweb.session import AuthSession
from rkweb.flaskutils import Blueprint, abort, respond, unauthorized
from rkweb.rkserver import ExcryptMsg, ServerConn

# Blueprint
blp = Blueprint("dashboard", "dashboard", url_prefix="/dashboard", description="Get dashboard information")
def DashboardBlueprint():
    return blp

async def get_features() -> dict:
    # Get features from server
    server = ServerConn()
    msg = ExcryptMsg("[AOSETT;]")
    msg.set_tag("OP", "features:get")
    msg.set_tag("JW", AuthSession.auth_token())
    rsp = await server.send_excrypt(msg)

    # Put apps features into dict
    ret = {}
    app_feats = rsp.get_tag("FE")
    for feat in app_feats.split(","):
        components = feat.split("=")
        if len(components) > 1:
            ret[components[0]] = components[1]
        else:
            ret[components[0]] = 1

    # Put firmware features into dict
    fw_feats = rsp.get_tag("FW")
    for feat in fw_feats.split(","):
        if feat.startswith("PRODROLES"):
            ret["PRODROLES"] = feat[len("PRODROLES"):]
        elif feat.startswith("RATE"):
            ret["RATE"] = feat[len("RATE"):]
        elif feat.startswith("VIRTUALHSM"):
            qty = feat[len("VIRTUALHSM"):]
            if int(qty) > 0:
                ret["VIRTUALHSM"] = qty
        else:
            ret[feat] = "1"

    # Virtual or physical hardware?
    if rsp.get_tag("VR") == "0":
        ret["Hardware"] = "1"
    else:
        ret["Virtual"] = "1"

    return ret

# GET /services
class Service(Model):
    name: str = field(description="The short human readable name of the service")
    description: str = field(description="The short human readable description of the service")
    icon: str = field(description="The path of the icon that represents the service relative to /")
    url: str = field(description="The URL of the service relative to /")

class ServiceCategory(Model):
    name: str = field(description="The short human readable name of the service category")
    description: str = field(description="The short human readable description of the service category")
    icon: str = field(description="The path of the icon that represents the service category relative to /")

    services: List[Service] = field(description="Information about the services available for this category")

class Services(Model):
    categories: List[ServiceCategory] = field(
        description="Information about the services available for the logged in context"
    )

def has_config_perm(perms):
    if any(perm in [
            'Communication:Ethernet Settings',
            'Communication:Network Settings',
            'Communication:Port Settings',
            'Communication:TCP Settings',
            'Communication:TLS Settings',
            'Device:Backup',
            'Device:Config',
            'Device:Feature Request',
            'Device:Firmware Update',
            'Device:Restore',
            'Device:Time',
            'Device:Zeroize',
            'Major Keys:Load',
            'Major Keys:Partial Load',
            'Security:Key Settings',
            'Security:Secure Mode',
            'Security:System Settings',
            'Security:TLS Resign',
            'Security:TLS Resign',
            'System:Keys',
            'System:Orphan Keeper',
            'System:PKI Settings',
            'System:Prune File System',
            ] for perm in perms):
        return True
    return False

async def get_static_services():
    # Verify login
    auth_sess = AuthSession.get()

    # Get licenses from sever
    features = await get_features()

    # Some shorthand for building the service_info list
    rd = lambda view : "/rd/#/" + view

    has_perm = lambda perm : perm in auth_sess.perms
    has_one_perm = lambda perms : any(perm in perms for perm in auth_sess.perms)

    has_feat = lambda feat : feat in features
    has_one_feat = lambda feats : any(feat in feats for feat in features)

    hsmweb = not await WebConfig.get_virtual() or os.getenv("HSM_WEB_ENABLED") == "1"

    # All of the possible services
    # Grep REMOTE_DESKTOP_VIEWS
    # XXX: Update DeployServiceCommand.cpp if you add/change a category
    service_info = [
        {
            'name': 'Key Management',
            'description': 'Manage the cryptographic keys directly',
            'icon': '/shared/static/icons/key-management.svg',
            'services': [
                {
                    'name': 'Key Database',
                    'description': 'Manage keys and key groups',
                    'icon': '/shared/static/icons/key-database.svg',
                    'url': rd('Key'),
                    'perm': not auth_sess.user_management and has_perm('Keys'),
                },
                {
                    'name': 'User Keys',
                    'description': 'Manage per-user keys',
                    'icon': '/shared/static/icons/user-keys.svg',
                    'url': rd('Personal Key'),
                    'perm': has_one_perm(['Keys:Personal Keys', 'Keys:Personal Keys Managed', 'System:All Personal Keys']),
                },
                {
                    'name': 'Secrets',
                    'description': 'Manage Key Management Interoperability Protocol objects',
                    'icon': '/shared/static/icons/secrets.svg',
                    'url': rd('KMIP'),
                    'perm': has_one_perm(['KMIPTemplate', 'SecretData']),
                },
                {
                    'name': 'Key Exchange Hosts',
                    'description': 'Manage profiles for exporting and importing symmetrics',
                    'icon': '/shared/static/icons/key-exchange-hosts.svg',
                    'url': rd('Host'),
                    'perm': has_perm('Host'),
                },
            ]
        },
        {
            'name': 'PKI Management',
            'description': 'Manage public key infrastructure certificates',
            'icon': '/shared/static/icons/pki.svg',
            'services': [
                {
                    'name': 'Certificate Management',
                    'description': 'Manage PKI certificates',
                    'icon': '/shared/static/icons/certificate-management.svg',
                    'url': rd('CA'),
                    'perm': has_perm('CertManage'),
                },
                {
                    'name': 'Registration Authority',
                    'description': 'PKI issuance with approval workflow',
                    'icon': '/shared/static/icons/registration-authority.svg',
                    'url': '/regauth/',
                    'perm': has_feat('RA') and has_one_perm(['CertManage:Upload', 'RequestApproval:Approve']),
                },
                {
                    'name': 'Certificate Templates',
                    'description': 'Manage X.509 v3 extension profiles',
                    'icon': '/shared/static/icons/certificate-templates.svg',
                    'url': rd('V3 Ext'),
                    'perm': has_perm('V3ExtProfile') and has_feat('CA'),
                },
                {
                    'name': 'Certificate DN Profiles',
                    'description': 'Manage X.509 subject profiles',
                    'icon': '/shared/static/icons/certificate-dn-profiles.svg',
                    'url': rd('X509 DN'),
                    'perm': has_perm('X509DNProfile') and has_feat('CA'),
                },
                {
                    'name': 'PKI Signing Approvals',
                    'description': 'Approve pending PKI requests and manage approval groups',
                    'icon': '/shared/static/icons/pki-signing-approvals.svg',
                    'url': rd('Request Approval'),
                    'perm': has_perm('RequestApproval') and has_feat('RA'),
                },
                {
                    'name': 'ADCS Templates',
                    'description': 'Manage Windows CA PKI templates',
                    'icon': '/shared/static/icons/adcs-templates.svg',
                    'url': rd('Windows PKI Template'),
                    'perm': has_perm('WindowsPKITemplate') and has_feat('WCCE'),
                },
            ]
        },
        {
            'name': 'Data Protection',
            'description': 'Protect important data in transit and at rest',
            'icon': '/shared/static/icons/data-protection.svg',
            'services': [
                {
                    'name': 'File Encryption',
                    'description': 'Manage file encryption profiles',
                    'icon': '/shared/static/icons/file-encryption.svg',
                    'url': rd('File Enc'),
                    'perm': has_perm('FileEnc') and has_feat('DataProtection'),
                },
                {
                    'name': 'Tokenization Profiles',
                    'description': 'Manage format preserving tokenization profiles',
                    'icon': '/shared/static/icons/tokenization-profiles.svg',
                    'url': rd('Tokenization'),
                    'perm': has_perm('Token'),
                },
            ]
        },
        {
            'name': 'Device Key Loading',
            'description': 'Point-of-Sale device key injection',
            'icon': '/shared/static/icons/key-loading.svg',
            'services': [
                {
                    'name': 'Remote Key Injection Database',
                    'description': 'Manage devices for remote key injection',
                    'icon': '/shared/static/icons/remote-key-injection-database.svg',
                    'url': rd('RKMS'),
                    'perm': has_perm('Injection Devices') and has_feat('RemotePOS'),
                },
                {
                    'name': 'Direct Key Injection Database',
                    'description': 'Manage devices for direct key injection',
                    'icon': '/shared/static/icons/direct-key-injection-database.svg',
                    'url': rd('SKI'),
                    'perm': has_perm('Injection Devices') and has_feat('DirectKeyInjection'),
                },
                {
                    'name': 'Device Hosts',
                    'description': 'Manage device hosts',
                    'icon': '/shared/static/icons/device-hosts.svg',
                    'url': rd('Device Host'),
                    'perm': has_perm('DeviceHost') and 'Gilbarco' in features and not 'Activation' in features,
                },
                {
                    'name': 'Futurex Signing',
                    'description': 'Sign Futurex HSMs',
                    'icon': '/shared/static/icons/futurex-signing.svg',
                    'url': rd('Futurex Signing'),
                    'perm': has_feat('MultiCardSigning') and has_perm('CertManage'),
                },
            ]
        },
        {
            'name': 'HSM Management',
            'description': 'Monitor and manage the hardened enterprise security platform',
            'icon': '/shared/static/icons/infrastructure-management.svg',
            'services': [
                {
                    'name': 'HSMs',
                    'description': 'Define groups of HSMs used to deploy virtual HSMs',
                    'icon': '/shared/static/icons/hsms.svg',
                    'url': rd('Virtual HSM Hosts'),
                    'perm': has_feat("VIRTUALHSM") and has_perm('Virtual HSM Host Groups'),
                },
                {
                    'name': 'Virtual HSMs',
                    'description': 'Create and manage virtual HSMs',
                    'icon': '/shared/static/icons/virtual-hsms.svg',
                    'url': rd('Virtual HSMs'),
                    'perm': has_feat("VIRTUALHSM") and (has_perm('Local Virtual HSMs') or has_perm('RemoteVHSMManagement')),
                },
                {
                    'name': 'Cluster Management',
                    'description': 'Manage clusters of HSMs and virtual HSMs for load balancing and redundancy',
                    'icon': '/shared/static/icons/cluster-management.svg',
                    'url': rd('Balanced Device'),
                    'perm': has_perm('CardGroup') and has_feat('External'),
                },
                {
                    'name': 'Key and Settings Management',
                    'description': 'Manage keys and settings for clusters of HSMs',
                    'icon': '/shared/static/icons/key-and-settings-management.svg',
                    'url': '/byok/',
                    'perm': has_perm('CardGroup') and has_feat('External'),
                },
                {
                    # Same as Encryption Devices view but for non-Guardian
                    'name': 'Application Card',
                    'description': 'Manage the internal encryption card',
                    'icon': '/shared/static/icons/application-card.svg',
                    'url': rd('Card'),
                    'perm': not has_feat('External') and auth_sess.hardened and has_perm('Device:Config'),
                },
            ]
        },
        {
            'name': 'Identity Management',
            'description': 'Manage access control for the security platform',
            'icon': '/shared/static/icons/identity-management.svg',
            'services': [
                {
                    'name': 'Identities',
                    'description': 'Manage users and application endpoint credentials',
                    'icon': '/shared/static/icons/identities.svg',
                    'url': rd('Identity'),
                    'perm': has_perm('Identity'),
                },
                {
                    'name': 'Roles',
                    'description': 'Manage authorization profiles',
                    'icon': '/shared/static/icons/roles.svg',
                    'url': rd('Role'),
                    'perm': has_one_perm(['Role', 'Tablet:Config.User Sync']),
                },
                {
                    'name': 'Identity Providers',
                    'description': 'Manage authenticaton and authorization providers',
                    'icon': '/shared/static/icons/identity-providers.svg',
                    'url': rd('Identity Provider'),
                    'perm': has_perm('IdentityProvider')
                },
                {
                    'name': 'Cloud Credentials',
                    'description': 'Manage external cloud authentication parameters',
                    'icon': '/shared/static/icons/cloud-credentials.svg',
                    'url': rd('Cloud Credential'),
                    'perm': not auth_sess.user_management and has_perm('Keys') and has_one_feat(['CloudKeyAWS', 'CloudKeyAzure']),
                },
                {
                    'name': 'Web Profiles',
                    'description': 'Manage dashboard service profiles',
                    'icon': '/shared/static/icons/web-profiles.svg',
                    'url': rd('Web Profile'),
                    'perm': has_perm('Identity'),
                },
            ]
        },
        {
            'name': 'Administration',
            'description': 'Configuration tasks and internal device management',
            'icon': '/shared/static/icons/administration.svg',
            'services': [
                {
                    'name': 'Configuration Tasks',
                    'description': 'Configure and manage the server',
                    'icon': '/shared/static/icons/configuration-tasks.svg',
                    'url': rd('Config'),
                    'perm': has_config_perm(auth_sess.perms),
                },
                {
                    'name': 'Encryption Card Web',
                    'description': 'Access the internal encryption card',
                    'icon': '/shared/static/icons/encryption-card-web.svg',
                    'url': '/hsmweb',
                    'perm': auth_sess.hardened and auth_sess.management and hsmweb,
                },
                {
                    'name': 'Synchronization Peers',
                    'description': 'Manage synchronized peers',
                    'icon': '/shared/static/icons/synchronization-peers.svg',
                    'url': rd('Peer'),
                    'perm': has_perm('Peer'),
                },
                {
                    'name': 'Internal Hard Drive Management',
                    'description': 'View and manage hardware components',
                    'icon': '/shared/static/icons/internal-hard-drive-management.svg',
                    'url': rd('Hardware'),
                    'perm': has_feat('Hardware') and has_perm('Device:Config'),
                },
                {
                    'name': 'Service Manager',
                    'description': 'Manage custom services',
                    'icon': '/shared/static/icons/service-manager.svg',
                    'url': '/cuserv/',
                    'perm': has_perm('Custom Services')
                }
            ]
        },
        {
            'name': 'Logging and Reporting',
            'description': 'Configuration reports, application logs, and audit logs',
            'icon': '/shared/static/icons/logging-reporting.svg',
            'services': [
                {
                    'name': 'Cluster Dashboard',
                    'description': 'View and download global cluster statistics and information',
                    'icon': '/shared/static/icons/cluster-dashboard.svg',
                    'url': '/guardian/',
                    'perm': has_perm('CardGroup') and has_feat('External'),
                },
                {
                    'name': 'Cluster Statistics',
                    'description': 'View statistics of HSM and virtual HSM clusters',
                    'icon': '/shared/static/icons/cluster-statistics.svg',
                    'url': rd('Card Stat'),
                    'perm': has_perm('CardGroup') and has_feat('External'),
                },
                {
                    'name': 'Audit Logs',
                    'description': 'View and export event audit logs',
                    'icon': '/shared/static/icons/audit-logs.svg',
                    'url': rd('Audit Log'),
                    'perm': has_perm('Log'),
                },
                {
                    'name': 'System Logs',
                    'description': 'View and export application logs',
                    'icon': '/shared/static/icons/system-logs.svg',
                    'url': rd('System Log'),
                    'perm': has_perm('System:System Logs'),
                },
                {
                    'name': 'Reports',
                    'description': 'Generate device reports',
                    'icon': '/shared/static/icons/reports.svg',
                    'url': rd('Report'),
                    'perm': has_perm('Report'),
                },
                {
                    'name': 'Jobs',
                    'description': 'Manager currently running tasks',
                    'icon': '/shared/static/icons/jobs.svg',
                    'url': rd('Job'),
                    'perm': True,
                },
            ]
        },
        {
            'name': 'Settings',
            'description': 'Configure this device',
            'icon': '/shared/static/icons/settings-two.svg',
            'services': [
                {
                    'name': 'Network Drives',
                    'description': 'Manage network mounted drives',
                    'icon': '/shared/static/icons/network-drives.svg',
                    'url': rd('Remote Drive'),
                    'perm': has_perm('Remote Drive'),
                },
                {
                    'name': 'Notification and Mailer Templates',
                    'description': 'Manage mailer templates for printing and e-mail',
                    'icon': '/shared/static/icons/notification-and-mailer-templates.svg',
                    'url': rd('Template'),
                    'perm': has_perm('Template'),
                },
                {
                    'name': 'TLS Profiles',
                    'description': 'Manage profiles used for TLS settings',
                    'icon': '/shared/static/icons/tls-profiles.svg',
                    'url': rd('TLS Profile'),
                    'perm': has_perm('TLSProfile') and has_one_feat(['TLSTunnel', 'Guardian']),
                },
                {
                    'name': 'TLS Tunnels',
                    'description': 'Manage TLS proxy tunnels',
                    'icon': '/shared/static/icons/tls-tunnels.svg',
                    'url': rd('TLS Tunnel'),
                    'perm': has_perm('CryptoTunnels') and has_feat('TLSTunnel'),
                },
                {
                    'name': 'LDAP Publishing Hosts',
                    'description': 'Manage LDAP directories where PKI can be published',
                    'icon': '/shared/static/icons/ldap-publishing-hosts.svg',
                    'url': rd('LDAP Directory'),
                    'perm': has_perm('LDAPDirectory') and has_feat('CA'),
                },
            ]
        },
    ]

    # Output
    categories = []
    for category in service_info:
        services = []
        for service in category['services']:
            # Has perm?
            if not service['perm']:
                continue
            services.append({
                'name': service['name'],
                'description': service['description'],
                'icon': service['icon'],
                'url': service['url'],
            })
        # Has any service in this category?
        if len(services) == 0:
            continue

        categories.append({
            'name': category['name'],
            'description': category['description'],
            'icon': category['icon'],
            'services': services,
        })

    return categories

@blp.fxroute(
    endpoint="/services",
    method="GET",
    description="Get information about what services the logged in context can visit",
    resp_schemas={
        200: Services,
    })
@login_required()
async def get():

    # Get the applicable static services
    dashboard_services = await get_static_services()

    # Respond
    respond(200, {'categories': dashboard_services})
