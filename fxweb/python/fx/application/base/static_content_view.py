"""
@file      static_content_view.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Base View for serving static content
"""

import os
import mimetypes

from fx_view import FxView
from auth import login_required
from flask import make_response
from app_config import AppConfig
from lib.utils.response_generator import APIResponses

# XXX: Requires python and js to be same on nginx/python containers
def find_file(base_uri, filename):
    """Finds the location on filesystem of the protected file the user wants
    Args:
        base_uri: The sub directory the file should be in (Ex: 'components/')
        filename: The exact name of the file (Ex: 'fxTemplate.js')

    Returns:
        The absolute filesystem path of the file referenced
        None if not found
    """
    # Truncate trailing '/'
    trunc_base_uri = base_uri
    if len(trunc_base_uri) > 0 and trunc_base_uri[-1] == "/":
        trunc_base_uri = trunc_base_uri[0:-1]

    # Find matching file in base uri relative to var/www
    for topdir in ['/var/www/' + AppConfig.server_type, '/var/www/fxweb']:
        for curdir, subdirs, files in os.walk(topdir):
            if not filename in files:
                continue
            if curdir.find(trunc_base_uri) == -1:
                continue

            return os.path.join(curdir, filename)

    return None

def create_static_response(base_uri, filename=None, code=None):
    """Create the response for the filename
    Arguments:
        base_uri: The base uri of the response redirect
        filename: The file to make a response for
        code: HTTP status code override
    Return: An HTTP response
    """
    response = None
    filepath = find_file(base_uri, filename)
    if not filepath:
        response = APIResponses.not_found("Could not locate file {} in {}".format(filename, base_uri))
    else:
        filepath = filepath.replace('/var/www/', '/protected/')

        response = make_response("")
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['X-Accel-Redirect'] = filepath
        mime, _ = mimetypes.guess_type(filepath)
        if mime is not None:
            response.headers['Content-Type'] = mime

    if code is not None:
        response.status_code = code

    return response


def unauthorized_redirect(base_uri='/'):
    """Create the redirect function
    Arguments:
        base_uri:  The base uri for the redirect response
    Returns:
        redirect_wrapper: A function to create the redirect
    """
    def redirect_wrapper():
        """Create the redirect for the unauthorized page
        If the current user hasn't logged in or their session timed out,
        redirect to login page
        Returns:
            A response containing a redirect and a 401 error
        """
        return create_static_response(base_uri, filename='unauthorized.html', code=401)

    return redirect_wrapper


class StaticContentView(FxView):
    """
    This view serves static content by redirecting to the web server
    """
    decorators = [login_required]

    def __init__(self, server_interface, base_uri):
        super(StaticContentView, self).__init__(server_interface)
        self.base_uri = base_uri

    def get(self, *args, **kwargs):
        """
        Builds the redirect response from the URI in the request
        """

        filename = kwargs.get('filename')
        return self._create_static_response(filename)

    def _create_static_response(self, filename):
        """Create the response for the filename
        Arguments:
            filename: The file to make a response for
        Return: An HTTP response
        """
        return create_static_response(self.base_uri, filename)
