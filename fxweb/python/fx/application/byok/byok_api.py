"""
@file      byok/byok_api.py
@author    David Neathery (dneathery@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2022

@section DESCRIPTION
Templates and API spec handlers for the VC BYOK feature
"""

from flask import render_template_string
from flask_smorest import Api as __Api

_docs_ui_template = r"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8"/>
    <title>{{title}}</title>
    <link href="{{swagger_ui_url}}swagger-ui.css" rel="stylesheet" type="text/css"/>
</head>

<body>

    <div id="swagger-ui-container"></div>

    <script src="{{swagger_ui_url}}swagger-ui-standalone-preset.js"></script>
    <script src="{{swagger_ui_url}}swagger-ui-bundle.js"></script>
    <script>

        let config = {
            requestInterceptor: _ => {
                _.headers['X-FXSRF-TOKEN'] = document.cookie.match(/FXSRF-TOKEN=([^;]+)/)?.pop() || '';
                return _;
            },
            url: "{{ url_for('api-docs.openapi_json') }}",
            dom_id: '#swagger-ui-container'
        }

        let override_config = {{ swagger_ui_config | tojson }};
        for (let attrname in override_config) { config[attrname] = override_config[attrname]; }

        window.onload = function() {
            window.ui = SwaggerUIBundle(config)
        }
    </script>

</body>

</html>
"""


class ByokApi(__Api):
    def _openapi_swagger_ui(self):
        """Render our custom Swagger UI template"""
        context = dict(
            title=self.spec.title,
            swagger_ui_url=self._swagger_ui_url,
            swagger_ui_config=self._app.config.get('OPENAPI_SWAGGER_UI_CONFIG', {}),
        )
        return render_template_string(_docs_ui_template, **context)
