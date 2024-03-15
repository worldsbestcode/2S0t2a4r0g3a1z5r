import os
import time
import datetime

import psutil
from signal import SIGKILL

from cachelib.file import FileSystemCache
from flask_session.sessions import FileSystemSession

from rkweb.session_config import get_session_config

from rd.session import DesktopSession

# Attempt to assume www-data
try:
    import grp
    gid = grp.getgrnam('www-data')[2]
    import pwd
    uid = pwd.getpwnam('www-data')[2]
    os.setregid(gid, gid)
    os.setreuid(uid, uid)
except:
    pass

class PruneRDThread(object):
    """
    Prunes remote desktop sessions that are no longer authenticated.
    """
    def __init__(self):
        super().__init__()

        self.running = False

        # Grab configuration
        config = get_session_config()
        self.file_mode = config['SESSION_FILE_MODE']
        self.cache_dir = config['SESSION_FILE_DIR']
        self.file_threshold = config['SESSION_FILE_THRESHOLD']
        self.session_lifetime = config['PERMANENT_SESSION_LIFETIME']

        # Open cache
        self.cache = FileSystemCache(cache_dir=self.cache_dir, threshold=self.file_threshold, mode=self.file_mode)

        # Force the cache to use the pre-hashed key for the filename
        def get_cache_filename(key):
            return os.path.join(self.cache_dir, key)

        self.cache._get_filename = get_cache_filename

    def stop(self) -> None:
        self.running = False

    def run(self) -> None:
        self.running = True

        # Try to prune remote desktop every couple minutes
        while self.running:
            self.cleanup_sessions()
            for i in range(60):
                if self.running:
                    time.sleep(2)
                else:
                    break

    def cleanup_sessions(self) -> None:
        # Get all sessions in cache dir
        sessions = []
        try:
            sessions = [f for f in os.listdir(self.cache_dir) if os.path.isfile(os.path.join(self.cache_dir, f))]
        except Exception as e:
            pass

        # Check each session
        ports = []
        for sid in sessions:
            # Get session
            try:
                data = self.cache.get(key=sid)
            except Exception as e:
                continue
            try:
                web_session = FileSystemSession(data, sid=sid)
            except Exception as e:
                continue

            try:
                session = DesktopSession()
                session.from_dict(web_session['desktop'])
            except Exception as e:
                continue

            # Session is expired
            if (session.last_access + self.session_lifetime) < datetime.datetime.utcnow():
                self.expire_session(sid)
            # Add the vnc port to the list
            else:
                ports.append(session.vnc_port + 1000)

        # Get all vnc processes
        vncProcs = [proc for proc in psutil.process_iter() if 'x11vnc' in proc.name()]

        # Kill any vnc processes not associated with a session
        for proc in vncProcs:
            # Try to parse the port from commandline args
            port = -1
            try:
                # In spawn-rkclient, the port is the fifth argument
                port = int(proc.cmdline()[4])
            except ValueError as e:
                continue

            # Parsed the port but it's not in our list
            if port not in ports:
                os.system("sudo /usr/bin/kill-vnc {}".format(port))
                proc.wait()

    def expire_session(self, sid) -> None:
        try:
           self.cache.delete(sid)
        except Exception as e:
            pass

# Run thread
thread = PruneRDThread()
thread.run()
