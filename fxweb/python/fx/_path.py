import os
import inspect
import sys

IGNORE_LIST = ['/kmes', '/regauth', '/byok']

def add_path(path):
    sys.path.append(path)
    for root, dirs, files in os.walk(path):
        for a_dir in dirs:
            a_path = os.path.join(root, a_dir)
            if any(ignore in a_path for ignore in IGNORE_LIST):
                continue
            sys.path.append(a_path)

# Useful program paths
BASE = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
LIBS = BASE + "/lib/"
APP = BASE + "/application/"
TESTS = BASE + '/tests/'
WEB_BASE = os.path.abspath(BASE + '/../web/shared/')

sys.path.append(BASE)
add_path(LIBS)
add_path(APP)
add_path(TESTS)
