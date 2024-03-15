import os
import datetime

from asyncio import Lock
from urllib.parse import urlsplit

from rkweb.rkserver import ServerConn, ExcryptMsg

class WebConfig(object):
    lock = Lock()
    last_update = None

    origins = []
    jwt_headers = ["Authorization"]
    api_key_headers = ["X-API-Key"]
    max_sessions = 1
    features = {}
    is_virtual = True

    @classmethod
    async def get_origins(cls):
        await cls._refresh()
        return cls.origins

    @classmethod
    def cached_origins(cls):
        return cls.origins

    @classmethod
    async def get_jwt_headers(cls):
        await cls._refresh()
        return cls.jwt_headers

    @classmethod
    async def get_api_key_headers(cls):
        await cls._refresh()
        return cls.api_key_headers

    @classmethod
    async def get_max_sessions(cls):
        await cls._refresh()
        return cls.max_sessions

    @classmethod
    async def get_features(cls):
        await cls._refresh()
        return cls.features

    @classmethod
    async def get_virtual(cls):
        await cls._refresh()
        return cls.is_virtual

    @classmethod
    async def _refresh(cls):
        await cls.lock.acquire()
        try:
            # Only refresh once every 5 minutes
            if cls.last_update and (cls.last_update + datetime.timedelta(minutes=5)) > datetime.datetime.utcnow():
                return None

            # Try to get config from server
            server = ServerConn()
            rsp = await server.send_excrypt("[AOWEBI;]")
            if not rsp or rsp.get_tag("AN") != "Y":
                return None

            # Is docker
            cls.is_virtual = rsp.get_tag("VR") == "1"

            # Get max sessions
            cls.max_sessions = int(rsp.get_tag("MS"))

            # Get custom headers
            cls.jwt_headers = rsp.get_tag("JH").split(",")
            cls.api_headers = rsp.get_tag("AP").split(",")

            # Get origins
            cls.origins = WebConfig.parse_origins(rsp)

            # Get features
            cls.features = WebConfig.parse_features(rsp.get_tag("FE"))

            # Updated
            cls.last_update = datetime.datetime.utcnow()
        except:
            pass
        finally:
            cls.lock.release()

    # Parse valid web origins from response
    def parse_origins(rsp: ExcryptMsg):
        custom_origins = rsp.get_tag("OR").split(",")
        origin_ips = rsp.get_tag("OI").split(",")
        origin_port = rsp.get_tag("OP")

        # Create origins from IPs
        for ip in origin_ips:
            custom_origins.append("https://" + ip + ":" + origin_port)
            if origin_port == '443':
                custom_origins.append("https://" + ip)

        # Get valid hostnames from environment
        env = os.getenv('CRYPTOHUB_WEB_HOST')
        if env:
            custom_origins += env.split(',')

        # Canonicalize
        final_origins = set()
        for origin in custom_origins:

            # Wildcard, no need for anything else
            if origin == '*':
                final_origins = set()
                final_origins.add('*')
                break

            # {scheme='https', netloc='google.com:123'}
            split = urlsplit(origin)
            # As configured
            final_origins.add(split.scheme + "://" + split.netloc)

            # Account for with or without default port
            components = split.netloc.split(':')
            if len(components) == 2:
                if split.scheme == "https" and components[1] == '443':
                    final_origins.add(split.scheme + "://" + components[0])
                if split.scheme == "http" and components[1] == '80':
                    final_origins.add(split.scheme + "://" + components[0])
            else:
                final_origins.add(split.scheme + "://" + split.netloc)
                if split.scheme == "https":
                    final_origins.add(split.scheme + "://" + split.netloc + ":443")
                if split.scheme == "http":
                    final_origins.add(split.scheme + "://" + split.netloc + ":80")

        return final_origins

    # Parse the feature map into a dict
    def parse_features(values: str):
        features = {}
        pairs = values.split(",")
        for pair in pairs:
            keyValue = pair.split("=")
            if len(keyValue) == 1:
                features[keyValue[0]] = "1"
            elif len(keyValue) >= 2:
                features[keyValue[0]] = keyValue[1]
        return features
