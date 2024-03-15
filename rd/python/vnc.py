import os
import shutil
import socket
import datetime
import subprocess

from threading import Lock
from datetime import timedelta

from rkweb.rand import rand_token
from rkweb.config import WebConfig
from rkweb.session import AuthSession

def rand_id():
    return rand_token(32)

class VncSession(object):
    def __init__(self):
        self.width = 1024
        self.height = 768
        self.external_id = None
        self.internal_id = None
        self.vnc_port = -1
        self.pid = -1
        self.proc = None
        self.last_access = datetime.datetime.utcnow()

    def close(self) -> None:
        if self.proc:
            subprocess.call(["sudo", "/usr/bin/kill-vnc", str(self.vnc_port + 1000)])
            self.proc.wait()
            self.proc = None

        # Cleanup IPC files
        for tmpdir in ["rdviews", "rdevents", "rdfido"]:
            tmpdir = "/var/run/fx/tmp/" + tmpdir
            try:
                os.remove(f"{tmpdir}/{self.pid}.txt")
            except:
                pass
            try:
                os.remove(f"{tmpdir}/{self.pid}_in.txt")
            except:
                pass
            try:
                os.remove(f"{tmpdir}/{self.pid}_out.txt")
            except:
                pass
        self.pid = -1

class VncSessionList(object):
    def __init__(self):
        self.sessions = []
        self.mtx = Lock()

    async def new_session(self, width, height, view, local):
        # If somehow any Xvfb instances got orphaned
        # We are going to kill them to reclaim the ports
        subprocess.call(["sudo", "/usr/bin/kill-xvfb-orphans"])

        sess = VncSession()
        sess.width = width
        sess.height = height
        sess.external_id = rand_id()
        sess.internal_id = rand_id()

        self.mtx.acquire()
        try:
            # Reserve ports 6900/7900 for the local client
            if local:
                for session in self.sessions:
                    if session.vnc_port == 6900:
                        sess = session
                        break
                sess.vnc_port = 6900
            else:
                sess.vnc_port = await self.allocate_port()
            if sess.vnc_port <= 0:
                return None
            rdenv = {
                'DPY_WIDTH': str(width),
                'DPY_HEIGHT': str(height),
                'DPY_DEPTH': "24",
                'QT_X11_NO_MITSHM': '1',
                'QT_QPA_PLATFORM': 'xcb',
                'VNC_PASS': sess.external_id,
                'VNC_PORT': str(sess.vnc_port + 1000),
                'WEB_PORT': str(sess.vnc_port),
                'RKSERVER_HOST': '127.0.0.1',
                'RKJWT': AuthSession.auth_token(),
                'HOSTNAME': 'CryptoHub',
            }
            if view:
                rdenv['RK_VIEW'] = view
            if local:
                rdenv['RKCLIENT_ARGS'] = '-D'
            sess.proc = subprocess.Popen(
                executable="/usr/bin/sudo",
                args=["/usr/bin/sudo", "-E", "/usr/bin/python3.8", "/usr/bin/futurex_spawnrd.py"],
                stdin=subprocess.PIPE,
                env=rdenv,
            )
            sess.pid = sess.proc.pid
            sess.proc.stdin.close()
            self.sessions.append(sess)
        finally:
            self.mtx.release()

        return sess

    async def allocate_port(self) -> int:
        max_sessions = await WebConfig.get_max_sessions()
        for port in range(max_sessions):
            ret = port + 6901

            # Check if port is in use in our session cache
            for sess in self.sessions:
                if sess.vnc_port == ret:
                    ret = -1
                    break

            # Check if port can be bound against
            if ret > 0:
                s = None
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind(('127.0.0.1', ret))
                except:
                    ret = -1
                finally:
                    if s:
                        s.close()

            # Found port
            if ret > 0:
                return ret

        return -1

    def get_session(self, internal_id) -> VncSession:
        self.mtx.acquire()
        try:
            self.prune()
            for sess in self.sessions:
                if sess.internal_id == internal_id:
                    sess.last_access = datetime.datetime.utcnow()
                    return sess
        finally:
            self.mtx.release()

        return None

    def pop(self, internal_id) -> VncSession:
        self.mtx.acquire()
        try:
            for sess in self.sessions:
                if sess.internal_id == internal_id:
                    sess.close()
                    break
            self.prune()
        finally:
            self.mtx.release()

    def prune(self):
        keep = []
        cleanup = []
        # Find dead or expired sessions
        for sess in self.sessions:
            # Alive
            if sess.proc != None and sess.proc.pid > 0 and sess.proc.pid == sess.pid and sess.proc.poll() == None:
                # Front-end has not pinged us in 5 minutes
                if (sess.last_access + timedelta(minutes=5)) < datetime.datetime.utcnow():
                    cleanup.append(sess)
                # Active
                else:
                    keep.append(sess)
            # Dead
            else:
                cleanup.append(sess)

        # Update kept sessions
        self.sessions = keep

        # Reap
        for sess in cleanup:
            sess.close()

    def reset(self) -> None:
        # Close all open sessions
        while len(self.sessions) > 0:
            self.mtx.acquire()
            try:
                self.sessions[0].close()
            finally:
                self.sessions.pop(0)
                self.mtx.release()

        # Kill all VNC processes
        for proc in ["x11vnc", "Xvfb"]:
            try:
                subprocess.call(["killall", proc])
            except:
                pass

        # Get the rkweb/rkclient shared group id
        gid = -1
        uid = -1
        try:
            import grp
            gid = grp.getgrnam('rkwebclient')[2]
            import pwd
            uid = pwd.getpwnam('www-data')[2]
        except:
            pass

        # Cleanup the filesystem IPC directories
        for tmpdir in ["rdviews", "rdevents", "rdfido"]:
            tmpdir = "/var/run/fx/tmp/" + tmpdir
            try:
                shutil.rmtree(tmpdir)
            except:
                pass
            try:
                os.mkdir(tmpdir)
                os.chmod(tmpdir, 0o0770)
                os.chown(tmpdir, uid, gid)
            except:
                pass
