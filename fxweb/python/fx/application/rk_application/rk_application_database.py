"""
@file      rk_application_database.py
@author    James Espinoza(jespinoza@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2016

@section DESCRIPTION
Performs queries on the RemoteKey database common to all RK based applications
"""

from app_database import AppDatabase
from urllib.parse import urlsplit

class RKApplicationDatabase(AppDatabase):
    '''
    Contains methods for common RK queries
    '''
    def __init__(self, db_name, app_name):
        self.db_name = db_name
        self.user_name = "futurex"
        self.app_name = app_name

    def get_config(self, item_name):
        '''
        Get the item's value from the cofiguration table
        '''
        try:
            return self.db_query(
                "SELECT value FROM configuration WHERE item=%s", [item_name]
            )[0][0]
        except (LookupError, ValueError):
            return None

    def get_device_addresses(self):
        '''
        Gets a list of all the device's interface's addresses.
        '''
        try:
            return self.db_query("SELECT device_address FROM ethernet_configuration", None)
        except (LookupError, ValueError):
            return None

    def get_vrrp_addresses(self):
        '''
        Gets a list of all the device's vrrp addresses.
        '''
        try:
            query = ("SELECT value FROM ethernet_attributes WHERE key='vrrpvip' AND ethernet_name IN "
                     "(SELECT ethernet_name FROM ethernet_attributes WHERE key='vrrpenabled' and value='1')")
            return self.db_query(query, None);
        except (LookupError, ValueError):
            return None

    def get_web_server_port(self):
        '''
        Gets the port the web server is serving connections with.
        '''
        try:
            return self.db_query("SELECT value FROM configuration WHERE item='dashboard_listen_port'", None)[0][0]
        except (LookupError, ValueError):
            return None

    def get_expected_origins(self):
        '''
        Define the expected "Origin" header value from configured interface addressess.
        '''
        list_origins = []
        scheme = "https"

        host_name = self.get_config("csr_host_name")

        if host_name is not None:
            host_name_split = urlsplit(host_name)
            scheme = host_name_split.scheme
            list_origins.append(scheme + "://" + host_name_split.netloc)

        # Then, grab all of the ethernet device addresses, because
        # they will be valid as well.
        list_device_addresses = self.get_device_addresses()
        list_vrrp_addresses = self.get_vrrp_addresses()
        listen_port = self.get_web_server_port()
        listen_port = "443" if listen_port is None else listen_port

        # TODO: DHCP will leave these addresses as 0.0.0.0 even though
        # an actual address is in use. Need a portable way to query this.
        for address in list_device_addresses + list_vrrp_addresses:
            if "0.0.0.0" not in address:
                list_origins.append(scheme + "://" + address[0] + ":" + listen_port)
                if scheme == 'https' and listen_port == '443':
                    list_origins.append(scheme + "://" + address[0])

        return list_origins

    def get_jwt_headers(self):
        """Get possible headers used by JWT
        Returns: A list of custom headers
        """
        headers = ['Authorization']
        custom = self.get_config('jwt_custom_http_header')
        if custom:
            # nginx always converts underscores to dashes because of wsgi rules
            custom = custom.replace("_", "-")

            # Custom headers are checked first
            headers.insert(0, custom)

        return headers

    def get_api_key_headers(self):
        """Get possible headers used by API Keys
        Returns: A list of custom headers
        """
        headers = ['X-API-Key']
        custom = self.get_config('api_key_custom_http_header')
        if custom:
            # nginx always converts underscores to dashes because of wsgi rules
            custom = custom.replace("_", "-")

            # Custom headers are checked first
            headers.insert(0, custom)

        return headers
