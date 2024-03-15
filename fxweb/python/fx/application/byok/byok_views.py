"""
@file      byok/byok_views.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2021

@section DESCRIPTION
Registers views for the VC BYOK feature
"""

from base.server_files import ServerAppFiles
from base.server_views import ServerAppView, ServerDefaultView

from byok import ByokMarshmallowPlugin
from byok.byok_api import ByokApi

API_PREFIX = '/guardian'


def _get_blueprints():
    from .views import (
        clusters,
        cskl,
        keys,
        major_keys,
        users,
    )

    return [
        clusters.bp,
        cskl.bp,
        keys.bp_keytable,
        keys.bp_keyblock,
        major_keys.bp,
        users.bp,
    ]


def map_views(program):

    API_PREFIX = '/byok/v1';

    program.app.config.update({
        'API_TITLE': 'VC BYOK',
        'API_VERSION': '1.0.0',
        'OPENAPI_VERSION': '3.0.2',
        'OPENAPI_URL_PREFIX': API_PREFIX,
        'OPENAPI_JSON_PATH': 'docs.json',
        'OPENAPI_SWAGGER_UI_PATH': 'docs',
        'OPENAPI_SWAGGER_UI_URL': '/shared/static/swagger-ui-3.51.1/',
        "OPENAPI_SWAGGER_UI_CONFIG": {
            'persistAuthorization': True,
        },
    })

    # TODO make api.handle_http_exception (and ERROR_SCHEMA) consistent with kmes web
    api = ByokApi(spec_kwargs={'marshmallow_plugin': ByokMarshmallowPlugin()})
    api.init_app(program.app)

    for bp in _get_blueprints():
        bp.register_views(server_interface=program.server_interface)
        bp.url_prefix = API_PREFIX
        api.register_blueprint(bp)

    return {
        '/byok/landing': ByokLandingView,
        '/byok/landing/': ByokLandingView,
        '/byok/<filename>': ByokAppView,
    }


class ByokLandingView(ServerAppView):
    decorators = []
    # TODO csrf


class ByokAppView(ServerAppFiles):
    decorators = []
    # TODO csrf
