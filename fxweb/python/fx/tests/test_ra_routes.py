"""
@file      test_ra_routes.py
@author    James Espinoza(jespinoza@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Test cases for RA routes
"""

import unittest
import nose.tools as nt
from mock import MagicMock
import json
from flask import jsonify

from fx import Program
from app_config import AppConfig
from server_interface import ServerInterface
from uri_router import URIRouter

VERBS = ['GET', 'POST', 'PUT', 'DELETE']


class TestRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        config = AppConfig()
        config.set('flask', 'uwsgi', False)
        self.program = Program(program_config=config)
        self.program.app_type = "regauth"
        self.program.router = URIRouter(self.program)
        self.program.router.run()
        handler = self.program.server_interface.conn_handler
        handler.send = MagicMock(return_value=None)
        self.client = self.program.app.test_client()

    def test_get_object(self):
        response = self.client.get('/object')
        nt.assert_equals(response.status, '401 UNAUTHORIZED')
        nt.assert_equals(response.status_code, 401)

    def test_post_object_without_login(self):
        response = self.client.post('/object')
        nt.assert_equals(response.status, '401 UNAUTHORIZED')
        nt.assert_equals(response.status_code, 401)

    def test_put_object_without_login(self):
        response = self.client.put('/object')
        nt.assert_equals(response.status, '401 UNAUTHORIZED')
        nt.assert_equals(response.status_code, 401)

    def test_delete_object(self):
        response = self.client.delete('/object')
        nt.assert_equals(response.status, '401 UNAUTHORIZED')
        nt.assert_equals(response.status_code, 401)

    def test_get_object_fail(self):
        response = self.client.get('/object')
        nt.assert_not_equals(response.status, '404 NOT FOUND')
        nt.assert_not_equals(response.status_code, 404)

    def test_get_login(self):
        response = self.client.get('/login')
        nt.assert_equals(response.status, '200 OK')
        nt.assert_equals(response.status_code, 200)

    def test_get_login(self):
        data = json.dumps(dict(auth_type='DummyData'))
        response = self.client.post('/login', data=data,
                                    content_type='application/json')
        nt.assert_equals(response.status, '200 OK')
        nt.assert_equals(response.status_code, 200)

    def test_put_login(self):
        response = self.client.put('/login')
        nt.assert_equals(response.status, '404 NOT FOUND')
        nt.assert_equals(response.status_code, 404)

    def test_post_logout(self):
        response = self.client.post('/logout')
        nt.assert_equals(response.status, '404 NOT FOUND')
        nt.assert_equals(response.status_code, 404)

    def test_get_logout(self):
        response = self.client.get('/logout')
        nt.assert_equals(response.status, '401 UNAUTHORIZED')
        nt.assert_equals(response.status_code, 401)

    def test_get_app(self):
        response = self.client.get('/app/')
        nt.assert_equals(response.status, '404 NOT FOUND')
        nt.assert_equals(response.status_code, 404)

    def test_get_app_landing(self):
        response = self.client.get('/app/landing')
        nt.assert_equals(response.status, '401 UNAUTHORIZED')
        nt.assert_equals(response.status_code, 401)

    def test_get_app_components(self):
        response = self.client.get('/app/components/')
        nt.assert_equals(response.status, '404 NOT FOUND')
        nt.assert_equals(response.status_code, 404)

    def test_get_app_components_idioms(self):
        response = self.client.get('/app/components/idioms/')
        nt.assert_equals(response.status, '404 NOT FOUND')
        nt.assert_equals(response.status_code, 404)

    def test_get_app_components_idioms_filename(self):
        response = self.client.get('/app/components/idioms/test_idiom.html')
        nt.assert_equals(response.status, '401 UNAUTHORIZED')
        nt.assert_equals(response.status_code, 401)

    def test_get_random_uri(self):
        response = self.client.get('/foo1234')
        nt.assert_equals(response.status, '404 NOT FOUND')
        nt.assert_equals(response.status_code, 404)

    def test_get_app_components_sections(self):
        response = self.client.get('/app/components/sections/')
        nt.assert_equals(response.status, '404 NOT FOUND')
        nt.assert_equals(response.status_code, 404)

    def test_get_app_components_sections_csrview(self):
        response = self.client.get('/app/components/sections/csrview/')
        nt.assert_equals(response.status, '404 NOT FOUND')
        nt.assert_equals(response.status_code, 404)

    def test_get_app_components_sections_filename(self):
        uri = '/app/components/sections/test_section.html'
        response = self.client.get(uri)
        nt.assert_equals(response.status, '401 UNAUTHORIZED')
        nt.assert_equals(response.status_code, 401)

    def test_get_app_components_sections_csrview_filename(self):
        uri = '/app/components/sections/csrview/test_csrview.html'
        response = self.client.get(uri)
        nt.assert_equals(response.status, '404 NOT FOUND')
        nt.assert_equals(response.status_code, 404)

    def test_get_app_directives(self):
        response = self.client.get('/app/directives/')
        nt.assert_equals(response.status, '404 NOT FOUND')
        nt.assert_equals(response.status_code, 404)

    def call_client(self, uri, verb):
        """Call the client uri with given method
        Params:
            uri: The route to call
            verb: The method to call with
        Returns: Response from client
        """
        client_method = getattr(self.client, verb.lower())
        return client_method(uri, follow_redirects=True)

    def unauthorized_test(self, uri, verb):
        """Generates a test to check that the returned value is 401
        Params:
            uri: The route to check
            verb: The method to check for the given route
        """
        response = self.call_client(uri, verb)
        nt.assert_equal(response.status, '401 UNAUTHORIZED', response.data)
        nt.assert_equal(response.status_code, 401, response.data)

    def not_found_test(self, uri, verb):
        """The URI method combination should not be found"""
        # Lookup the specified function
        response = self.call_client(uri, verb)
        nt.assert_equal(response.status, '404 NOT FOUND', response.data)
        nt.assert_equal(response.status_code, 404, response.data)

    @staticmethod
    def make_name(uri, verb, test):
        route_name = '_root' if uri is '/' else uri.replace('/', '_')
        return 'test{}_{}_{}'.format(route_name, verb, test)

    @staticmethod
    def add_requires_login():
        """Protected URIs should require a login"""
        # This is the list of protected URIs, and the valid operations
        # Update this list when the API changes.
        PROTECTED_URIS = {
            '/logout': ['GET'],
            '/object': VERBS,
            '/app/landing': ['GET'],
            '/app/formdata': ['GET', 'POST'],
            '/app/components/idioms': ['GET'],
            '/app/components/sections': ['GET'],
            '/app/directives': ['GET']
        }

        # Test valid URIs, they should return 401 since we aren't logged in
        for uri, operations in PROTECTED_URIS.iteritems():
            for verb in operations:
                name = TestRoutes.make_name(uri, verb, 'should_require_login')
                setattr(TestRoutes, name,
                        lambda self, uri=uri, verb=verb:
                            self.unauthorized_test(uri, verb))

    @staticmethod
    def add_not_found():
        """Test that unprotected uris respond 404 to invalid methods"""
        UNPROTECTED_URIS = {
            '/': ['GET'],
            '/login': ['GET', 'POST'],
            '/logout': ['GET']
        }

        # For all unsupported operations, ensure that we get a 404
        for uri, operations in UNPROTECTED_URIS.iteritems():
            # Calculate the set of unsupported operations
            invalid_operations = set(VERBS) - set(operations)
            for verb in invalid_operations:
                name = TestRoutes.make_name(uri, verb, 'should_be_invalid')
                current_verb = verb
                setattr(TestRoutes, name,
                        lambda self, uri=uri, verb=verb:
                            self.not_found_test(uri, verb))


# Add dynamically generated tests to the class
TestRoutes.add_requires_login()
TestRoutes.add_not_found()
