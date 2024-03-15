from flask import session

from rkweb.flaskutils import abort

PED_INJECT_KEY = 'pedinject'
SESSION_ID_KEY = 'session_id'

class InjectSession():
    port = 5045

    def __init__(self, service_id=None):
        self.session_id = None
        self.service_id = service_id

    def start(self, session_id):

        self.session_id = session_id
        self.save()

    @staticmethod
    def clear(service_id):
        try:
            session.pop(InjectSession.get_key(service_id))
        except:
            pass

    def save(self):
        try:
            key = self.get_key(self.service_id)
            session.permanent = True
            session[key] = self.to_dict()
        except:
            pass

    def get_key(self, service_id):
        return PED_INJECT_KEY + "/" + service_id

    @staticmethod
    def get(service_id):
        ret = InjectSession(service_id)
        try:
            key = ret.get_key(service_id)
            if key in session:
                ret.from_dict(session[key])
                ret.service_id = service_id
        except:
            pass
        return ret

    def to_dict(self):
        return {
            "session": self.session_id,
        }

    def from_dict(self, serial: dict):
        self.session_id = serial['session']

