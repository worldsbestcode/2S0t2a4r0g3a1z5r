import os
import base64
import hashlib

def rand_token(token_len):
    """
    Generates a random web-safe token with plenty of entropy
    Args:
        token_len: The number of characters in the token
    Returns:
        Token of desired length
    """
    ret = ""
    while len(ret) < token_len:
        m = hashlib.sha256()
        m.update(os.urandom(8192))
        cur = base64.b64encode(m.digest()).decode('utf-8')
        for char in ['+', '/', '=']:
            cur = cur.replace(char, '')
        ret += cur
    return ret[0:token_len]
