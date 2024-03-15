from enum import Enum
from flask import request

from rkweb.rand import rand_token

class ClientType(Enum):
    ApiUser = 1
    WebUser = 2
    Securus = 3

def get_client_type():
    # Detect user type
    api_user = not request.referrer and not request.origin
    securus_user = str(request.user_agent).endswith('Futurex Mobile')

    if api_user:
        return ClientType.ApiUser
    if securus_user:
        return ClientType.Securus
    return ClientType.WebUser

def is_api_user():
    return get_client_type() == ClientType.ApiUser

def new_csrf_token():
    # Don't use CSRF for API users
    client_type = get_client_type()
    return None if client_type == ClientType.ApiUser else rand_token(32)

def should_check_origin():
    # Don't check origin for Securus/REST-API clients
    client_type = get_client_type()
    return client_type == ClientType.WebUser
