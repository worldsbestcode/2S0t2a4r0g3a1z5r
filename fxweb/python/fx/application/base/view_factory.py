"""
@file      view_factory.py
@author    James Espinoza(jespinoza@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
A factory to return a View implementation based on input URI
"""
from form_view import FormView
from importlib import import_module
from application_log import ApplicationLogger as Logger


class ViewFactory(object):
    """
    A function to generate a view based on application type and URI
    """

    @staticmethod
    def get_views(program=None, server_type=None, ApplicationViews={}):
        product = server_type or getattr(program, 'server_type')
        if product in ApplicationViews:
            return ApplicationViews[product]

        try:
            # Example: 'from application import kmes.kmes_views as module'
            module = import_module(f'{product}.{product}_views', 'application')
        except ImportError:
            Logger.error('Failed to import application URIs.')
            raise

        try:
            # call module.map_views() to get uri->view dict
            views = getattr(module, 'map_views')(program)
        except AttributeError:
            Logger.error('Failed to load application views.')
            raise
        else:
            ApplicationViews[product] = views
            return views
