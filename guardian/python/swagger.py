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
                try {
                    _.headers['X-XSRF-TOKEN'] = document.cookie.match(/XSRF-TOKEN=([^;]+)/)?.pop() || '';
                } catch (error) {
                    console.error(error);
                }
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

def swagger_ui(api):
    """Render our custom Swagger UI template"""
    context = dict(
        title=api.spec.title,
        swagger_ui_url=api._swagger_ui_url,
        swagger_ui_config=api._app.config.get('OPENAPI_SWAGGER_UI_CONFIG', {}),
    )
    return render_template_string(_docs_ui_template, **context)

