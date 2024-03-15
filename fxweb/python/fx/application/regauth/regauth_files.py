"""
@file      regauth_files.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Implements the URIs that serve the files for the regauth views
"""

from static_content_view import StaticContentView
from auth import login_required

class RAAppComponentsSectionsCsrviewFiles(StaticContentView):
    """
    Serve files for /app/components/sections/csrView/<filename>
    """
    decorators = [login_required]

    def __init__(self, server_interface):
        super(RAAppComponentsSectionsCsrviewFiles, self).__init__(server_interface,
            "/components/sections/csrView/")

class RAAppComponentsSectionsSubmitterviewFiles(StaticContentView):
    """
    Serve files for /app/components/sections/submitterView/<filename>
    """
    decorators = [login_required]

    def __init__(self, server_interface):
        super(RAAppComponentsSectionsSubmitterviewFiles, self).__init__(server_interface,
            "/components/sections/submitterView/")

class RAAppComponentsSectionsDownloadviewFiles(StaticContentView):
    """
    Serve files for /app/components/sections/downloadView/<filename>
    """
    decorators = [login_required]

    def __init__(self, server_interface):
        super(RAAppComponentsSectionsDownloadviewFiles, self).__init__(server_interface,
            "/components/sections/downloadView/")

