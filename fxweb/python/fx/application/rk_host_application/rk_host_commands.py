"""
@file      commands.py
@author    Aaron Perez(aperez@futurex.com)

@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
All the Host API commands that the translator looks up
"""

from base_command import BaseCommand, CachedCommandMixin
from rk_host_application import rk_host_exceptions


def map_commands(commands={}, register=None):
    if register:
        commands.update(register)
    return commands


class HAPICommand(BaseCommand):
    """
    Base class for behaviour common to Host API commands
    """
    def finalize_response(self, response):
        response = super().finalize_response(response)

        # Check for any generic errors that should bypass response translation
        if response.getCommand() == "ERRO":
            self.check_error(response)

        # Add the human-readable error to the generic error message
        if response.hasField("ER"):
            error = response.getField("ER")
            message = response.getField("BB")
            response["BB"] = f"{message}: {error}" if message else error

        return response

    def check_error(self, response):
        error_code = response.getField("AM")

        if error_code == "19":
            raise rk_host_exceptions.FunctionNotSupportedError
        if error_code == "50":
            raise rk_host_exceptions.UserNotLoggedInError

    def __init_subclass__(cls, name):
        # Set the AO tag for the command
        cls.name = name
        map_commands(register={name: cls})


class DefaultHAPICommand(HAPICommand, name="default"):
    """
    Default class for Host API commands
    """

    def __init__(self, server_interface, command_name):
        self.name = command_name
        super().__init__(server_interface)


class PermissionStringMapping(CachedCommandMixin, HAPICommand, name="RKPS"):
    """
    Command for getting human-readable descriptions of permissions.
    """
    def send(self, data): # TODO(@dneathery) remove when RKPS command implemented
        if data["FN"] == "types":
            return {
                "TY": "Log,User,Config,Backup,Restore,Host",
                "DS": ("View logs,Manager users,Update system configuration"
                       ",Database backup,Database restore,Manage hosts/networks")
            }
        else:
            return {
                "TY": "Add,Delete,ExportComponent,MassImport",
                "DS": "Add,Delete,Export Component,Mass Import"
            }


class PermissionLevelCommand(CachedCommandMixin, HAPICommand, name="internal_cached_perm_options"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "SETT"

    def preprocess_request(self, request):
        request["OP"] = "global_permissions:get"
        return super().preprocess_request(request)


class GeneralEncryptDecrypt(HAPICommand, name="internal_RKED"):
    """
    General purpose symmetric key encryption/decryption command RKED
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "RKED"

    def send(self, request):
        # RKED takes data in chunks, overload send to issue multiple commands
        CHUNK_SIZE = 5120
        response = {}
        request = self.build_message(request)
        data_to_send = request.getField("BO")
        while data_to_send:
            request["BO"], data_to_send = data_to_send[:CHUNK_SIZE], data_to_send[CHUNK_SIZE:]
            # Enable continuation if remaining data is larger than chunk size
            request["BN"] = "1" if data_to_send else "0"

            # Send chunk to interface
            partial_response = self.make_request(request)

            if "BO" not in partial_response:
                # No data returned, indicates an error so return only the error response
                return partial_response
            elif response:
                # Not first request, only append resulting ciphertext/plaintext
                response["BO"] += partial_response["BO"]
            else:
                # Was first request
                response = partial_response

            # Set the continuation ID if we should continue
            if "CH" not in partial_response:
                break
            request = self.build_message({"CH": response["CH"]})
        return response


class CrlAdd(HAPICommand, name="_internal_RKRL_add"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "RKRL"

    def send(self, request):
        DATA = request.get("BO", "")
        DATA_SIZE = len(DATA)
        CHUNK_SIZE = 4096
        response = {}

        for i in range(0, DATA_SIZE, CHUNK_SIZE):
            chunk_end = i + CHUNK_SIZE
            request["BN"] = 1 if chunk_end < DATA_SIZE else 0
            request["BO"] = DATA[i:chunk_end]

            if "CH" in response:
                request["CH"] = response["CH"]

            response = super().send(request)

            if response.get("AN", "N") != "Y":
                break

        return response


class CrlDownload(HAPICommand, name="_internal_RKRL_download"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "RKRL"

    def send(self, request):
        request["CH"] = 0
        response = super().send(request)
        data = ""
        DATA_SIZE = int(response.get("CT", 0))*2

        for i in range(0, DATA_SIZE, 4096):
            data += response["BO"]
            if "CH" in response:
                request["CH"] = response["CH"]
                response = super().send(request)

            if response.get("AN", "N") != "Y":
                break

        response["BO"] = data
        return response

