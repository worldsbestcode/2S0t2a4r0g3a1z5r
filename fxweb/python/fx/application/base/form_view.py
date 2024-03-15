"""
@file      form_view.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Subclasses automatically have their URI registered for CSRF checking in
view_factory.py. Any view that serves forms that make requests to the middleware
should use this as their base class so that we can validate the request's
origin or referer (the URI of the form), else the "csrf_required" decorator
will return a 401. It's also important to note that static content should be
served on separate URI for two reasons:
1) It's more RESTful to not serve web pages on the same URI and frees up the
"GET" method in case query string parameters need to be used (using the API
without a web client)
2) "GET" requests don't always contain a referer or origin, so the
"csrf_required" decorator cannot be used to check requests made to that URI
"""

from static_content_view import StaticContentView
from auth import login_required


class FormView(StaticContentView):
    """
    This view is used for the URIs that serve a single-page app
    """
    decorators = [login_required]
    uri_matcher = ''

    def __init__(self, server_interface, base_uri):
        super(FormView, self).__init__(server_interface, base_uri)
