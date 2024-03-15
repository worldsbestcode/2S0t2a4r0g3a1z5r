"""
@file      app_database.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Wrapper for database connections
"""

import contextlib
import psycopg2

class AppDatabase(object):
    '''
    Base class wrapper for making database connections
    using psycopg2
    '''
    def __init__(self, db_name="postgres", user_name="postgres", app_name="ra"):
        self.db_name = db_name
        self.user_name = user_name
        self.app_name = app_name

    @contextlib.contextmanager
    def db_connection(self):
        '''
        Yields a cursor to the database
        '''
        with psycopg2.connect(dbname=self.db_name, user=self.user_name) as connection:
            yield connection.cursor()

    def db_query(self, query, query_params):
        '''
        Performs a SQL query
        '''
        rows = []
        with self.db_connection() as cursor:
            cursor.execute(query, query_params)
            rows = cursor.fetchall()
        return rows
