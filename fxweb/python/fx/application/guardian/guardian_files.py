"""
@file      guardian_files.py
@author    James Espinoza(jespinoza@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Implements the URIs that serve the files for the guardian views
"""
from flask import abort, make_response
from flask_login import login_required
from app_csrf import csrf_required

from static_content_view import StaticContentView
from server_authentication import ServerAuthentication


class GuardianAppComponentsSectionsNodeviewFiles(StaticContentView):
    """
    Serve files for /app/components/sections/nodeView/<filename>
    """
    decorators = [login_required]

    def __init__(self, server_interface):
        super(GuardianAppComponentsSectionsNodeviewFiles, self).__init__(
                server_interface, "/components/sections/nodeView/")


class GuardianAppComponentsSectionsConfigFiles(StaticContentView):
    """
    Serve files for /app/components/sections/config/<filename>
    """
    decorators = [login_required]

    def __init__(self, server_interface):
        super(GuardianAppComponentsSectionsConfigFiles, self).__init__(
                server_interface, "/components/sections/config/")


class GuardianAppComponentsSectionsPeerFiles(StaticContentView):
    """
    Serve files for /app/components/sections/peer/<filename>
    """
    decorators = [login_required]

    def __init__(self, server_interface):
        super(GuardianAppComponentsSectionsPeerFiles, self).__init__(
            server_interface,
            "/components/sections/peer/",
        )

class GuardianDownloadView(StaticContentView):
    """Serve the temporary download files"""

    decorators = [csrf_required]

    def __init__(self, server_interface):
        super(GuardianDownloadView, self).__init__(server_interface,
                                                   '/download/')

    def get(self, *args, **kwargs):
        """Return the report file if it exists"""
        user = ServerAuthentication.get_current_user()
        if user.temporary_file is None:
            abort(404)

        response = make_response("")
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['X-Accel-Redirect'] = "/protected_download" + user.temporary_file
        response.headers['Content-Type'] = "text/plain"
        return response
