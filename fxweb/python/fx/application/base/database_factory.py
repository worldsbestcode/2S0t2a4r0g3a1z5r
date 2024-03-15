"""
@file      database_factory.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
A factory to return an AppDatabase implementation based on server type
"""

from rk_application_database import RKApplicationDatabase

ApplicationDatabases = RKApplicationDatabase

class DatabaseFactory(object):
    """
    Generate a database based on server type
    """
    def __init__(self, db_name):
        self.db_name = db_name

    def database_from_server_type(self, server_type):
        db = None
        try:
            db = ApplicationDatabases(self.db_name, server_type)
        except ValueError:
            pass

        return db
