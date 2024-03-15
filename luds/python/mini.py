from rkweb.flaskutils import Blueprint, respond
from rkweb.lilmodels.base import Model, field

import datetime

# Blueprint
def MiniBlueprintV1():
    blp = Blueprint("Mini", "mini", url_prefix="/mini", description="Emulate the merchandise initializer")
    define_register(blp)
    return blp

class RegisterSerial(Model):
    serial: str = field(descriotn="Device serial to register")
    # XXX: These are snake case in the real mini
    applicationVersion: str = field(description="Current application version")
    productKey: str = field(description="Key that identifies asset")
    force: bool = field(description="Force cache bust and re-query back-end server")

class LicenseFile(Model):
    product_key: str = field(
        description='Key that identifies asset')

    serial: str = field(
        description='The serial number of your deployed product.')

    license_file: str = field(
        description='The text of the license file. '
        'If there is a signature key, that means it has been signed and is ready to be loaded.')

    time_submitted_for_signing: str = field(
        description='The time the file hash was submitted to the signing server to be signed.')

    time_signed: str = field(
        description='The time the license file was signed '
        'by the signing server.')

    file_hash: str = field(
        description='The hash of the license file, minus '
        'the signature key if present.')

def define_register(blp):
    @blp.fxroute(
        endpoint="/register-serial/",
        method="POST",
        description="Register serial with Mini server",
        schema=RegisterSerial,
        resp_schemas={
            200: LicenseFile,
        })
    async def register(args):
        serial = args['serial']
        product_key = args['productKey']
        app_version = args['applicationVersion']

        # Use debug mounted scripts to generate license file
        key = "/var/www/luds/bind/ec.priv"
        from luds_genfile import create_license
        license_file = create_license(key, serial, app_version, product_key)

        now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        respond(200, {
            'product_key': product_key,
            'serial': serial,
            'license_file': license_file,
            'time_submitted_for_signing': now,
            'time_signed': now,
            'file_hash': 'DEADBEEF',
        })
