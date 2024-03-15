from gevent import monkey
# The patch all function is supposed to be called as early as possible
monkey.patch_all()

from . import _path
from global_container import GlobalContainer as Program
