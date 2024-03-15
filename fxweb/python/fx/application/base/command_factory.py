"""
@file      command_factory.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
A factory for the commands that the translator looks up
"""

from rk_host_application import rk_host_commands

Commands = {
    'HAPI': rk_host_commands.map_commands(),
}

class CommandFactory(object):
    @staticmethod
    def get_command(command_type, command_category, command_name, server_interface):
        selected_commands = {}
        command = None

        # Find API
        if command_type in Commands:
            selected_commands = Commands[command_type]
        else:
            raise NotImplementedError

        # Find API category
        if command_category in selected_commands:
            selected_commands = selected_commands[command_category]

        # Find command by name
        if command_name in selected_commands:
            command = selected_commands[command_name]
            command = command(server_interface=server_interface)
        else:
            command = selected_commands['default']
            command = command(server_interface=server_interface, command_name=command_name)

        return command
