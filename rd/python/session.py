from flask import session

import os
import datetime

from rkweb.flaskutils import abort

class DesktopSession():
    def __init__(self):
        self.pid = -1
        self.sess = None
        self.vnc_port = -1
        self.last_access = datetime.datetime.utcnow()

    @staticmethod
    def logout():
        try:
            session.pop('desktop')
        except:
            pass

    def save(self):
        try:
            self.last_access = datetime.datetime.utcnow()
            session['desktop'] = self.to_dict()
        except:
            pass

    def set_vnc_sess(self, pid, sess, vnc_port):
        self.pid = pid
        self.sess = sess
        self.vnc_port = vnc_port
        self.save()

    def get_file_dir(self):
        # All uploads and downloads will be placed here
        # rkclient is responsible for creating and destroying this directory
        directory = "/var/run/fx/tmp/webmnt/{}".format(self.pid)
        if not os.path.exists(directory):
            abort(503, "Desktop session does not have file directory mounted.")
        return directory

    @staticmethod
    def check():
        desktop_sess = DesktopSession.get()
        if desktop_sess == None:
            abort(503, "No remote desktop session active.")
        elif desktop_sess.sess == None:
            abort(503, "No remote desktop view active.")
        elif desktop_sess.pid <= 0:
            abort(503, "No remote desktop process active.")
        return desktop_sess

    @staticmethod
    def get():
        ret = DesktopSession()
        try:
            if 'desktop' in session:
                ret.from_dict(session['desktop'])
        except:
            pass
        # Update last access time
        ret.save()
        return ret

    def to_dict(self):
        return {
            "pid": self.pid,
            "sess": self.sess,
            "vnc_port": self.vnc_port,
            "last_access": self.last_access,
        }

    def from_dict(self, serial: dict):
        self.pid = serial['pid']
        self.sess = serial['sess']
        self.vnc_port = serial['vnc_port']
        self.last_access = serial['last_access']

