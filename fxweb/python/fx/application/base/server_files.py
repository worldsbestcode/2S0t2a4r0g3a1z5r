"""
@file      server_files.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Implements the URIs that serve the files for the base server views
"""

from static_content_view import StaticContentView
from auth import login_required

class ServerAppFiles(StaticContentView):
    """
    Serve files for /app/<filename>
    """
    decorators=[login_required]
    def __init__(self, server_interface):
        super(ServerAppFiles, self).__init__(server_interface,
            "/")

class ServerAppDirectivesFiles(StaticContentView):
    """
    Serve files for /app/directives/<filename>
    """
    decorators=[login_required]
    def __init__(self, server_interface):
        super(ServerAppDirectivesFiles, self).__init__(server_interface,
            "/directives/")

class ServerAppComponentsFiles(StaticContentView):
    """
    Serve files for /app/components/<filename>
    """
    decorators=[login_required]
    def __init__(self, server_interface):
        super(ServerAppComponentsFiles, self).__init__(server_interface,
            "/components/")

class ServerAppComponentsIdiomsFiles(StaticContentView):
    """
    Serve files for /app/components/idioms/<filename>
    """
    decorators=[login_required]
    def __init__(self, server_interface):
        super(ServerAppComponentsIdiomsFiles, self).__init__(server_interface,
            "/components/idioms/")

class ServerAppComponentsSectionsFiles(StaticContentView):
    """
    Serve files for /app/components/sections/<filename>
    """
    decorators=[login_required]
    def __init__(self, server_interface):
        super(ServerAppComponentsSectionsFiles, self).__init__(server_interface,
            "/components/sections/")
