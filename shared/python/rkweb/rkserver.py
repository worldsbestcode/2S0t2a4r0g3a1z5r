import asyncio

from rkweb.security import is_api_user

class ExcryptMsg(object):
    def __init__(self, data = ''):
        self.tags = {}
        self.from_string(data)

    def set_tag(self, tag, value):
        # Sanitize input
        value = str(value)
        for ch in "[;]<#>":
            value = value.replace(ch, '_')
        self.tags[tag] = value

    def clear_tag(self, tag):
        self.tags.pop(tag)

    def get_tag(self, tag):
        if tag in self.tags:
            return self.tags[tag]
        return ''

    def from_string(self, data):
        self.tags = {}
        pos = 0
        if data[pos] == '[':
            pos += 1
        while pos < len(data):
            field_len = 0
            end_tag = data.find(';', pos)
            if end_tag == -1:
                end_tag = data.find(']', pos)
            if end_tag == -1:
                end_tag = len(data)
            value = data[pos:end_tag]
            if len(value) >= 2:
                self.tags[value[0:2]] = value[2:]
            pos = end_tag + 1

    def to_string(self):
        ret = '['
        if 'AO' in self.tags:
            ret += 'AO' + self.tags['AO'] + ';'
        for tag in self.tags:
            if tag in ['AO', 'AG']:
                continue
            ret += tag + self.tags[tag] + ';'
        if 'AG' in self.tags:
            ret += 'AG' + self.tags['AG'] + ';'
        ret += ']'
        return ret

    def to_error(self):
        err = None
        if 'ER' in self.tags:
            err = self.get_tag("ER")
        elif 'BB' in self.tags:
            if 'AN' in self.tags and len(self.tags['AN']) == 2:
                err = "{" + self.get_tag('AN') + "} " + self.get_tag('BB')
            else:
                err = self.get_tag('BB')

        if not err:
            err = "Unknown";

        return err

    def __str__(self):
        return self.to_string()

class ServerConn(object):
    async def read_response(self, reader):
        in_data = ""
        complete = False
        while not complete:
            in_data += (await reader.read(32768)).decode('utf-8')
            complete = in_data.find(']') >= 0

        return in_data, complete

    @staticmethod
    def get_sockfile(client = False):
        directory = '/var/run/fx/sockets/server/'
        if client:
            socketfile = 'rest_client.sock' if is_api_user() else 'web_client.sock'
        else:
            socketfile = 'rest_hapi.sock' if is_api_user() else 'web_hapi.sock'
        return directory + socketfile

    async def send_excrypt(self, msg, verbose = False):

        # Serialize
        out_data = str(msg)

        # Print debug
        if verbose:
            print("Send: {}".format(out_data))

        # Open connection to socket
        reader, writer = await asyncio.open_unix_connection(ServerConn.get_sockfile())

        # Lazily forcing everything to get sent at once or fail
        sent = writer.write(out_data.encode('utf-8'))
        await writer.drain()

        # hardcode 2 second timeout
        in_data = ""
        complete = False
        try:
            in_data, complete = await asyncio.wait_for(self.read_response(reader), timeout=2)
        except asyncio.TimeoutError as e:
            pass
        finally:
            writer.close()
            await writer.wait_closed()

        # Did we get a response?
        if not complete:
            raise RuntimeError("Timeout waiting for Excrypt response from server.")

        # Print debug
        if verbose:
            print("Recv: {}".format(in_data))

        return ExcryptMsg(in_data)

