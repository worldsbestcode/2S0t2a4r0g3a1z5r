import os
import json
import time
import datetime
import threading
import asyncio

from cachelib.file import FileSystemCache
from flask_session.sessions import FileSystemSession

from ipc import IpcUtils
from session import UserSession

def debug(msg):
    #f = open("/tmp/token_thread.txt", "a")
    #f.write(str(msg) + "\n")
    #f.close()
    ...

class TokenThread(threading.Thread):
    def __init__(self, config):
        super().__init__()

        self.running = False

        # Grab configuration
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

        # New async processing thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Try to refresh tokens every couple seconds
        while self.running:
            self.refresh_tokens()
            if self.running:
                time.sleep(2)

        # Done
        loop.stop()
        self.shutdown()

    def refresh_tokens(self) -> None:
        # Get all sessions in cache dir
        sessions = []
        try:
            sessions = [f for f in os.listdir(self.cache_dir) if os.path.isfile(os.path.join(self.cache_dir, f))]
        except Exception as e:
            debug(e)
        debug(sessions)

        # Check each session
        requests = []
        for sid in sessions:
            # Get session
            debug("SID: " + sid)
            try:
                data = self.cache.get(key=sid)
            except Exception as e:
                debug(e)
                continue
            debug("getted")
            debug("DATA: " + str(data))
            try:
                web_session = FileSystemSession(data, sid=sid)
            except Exception as e:
                debug(e)
                continue

            try:
                session = UserSession()
                session.from_dict(web_session['guardian'])
            except Exception as e:
                debug(e)
                continue

            # Session is expired
            if (session.last_access + self.session_lifetime) < datetime.datetime.utcnow():
                self.expire_session(sid)
            # Token is expired
            elif (session.token_expiration + TokenThread.leeway()) < datetime.datetime.utcnow():
                self.expire_session(sid)
            # Token is within renewal threshold
            elif (session.token_expiration - TokenThread.refresh_window()) < datetime.datetime.utcnow():
                requests.append(self.refresh_token(sid, web_session, session))

        # Process token updates
        debug(str(len(requests)) + " async to perform")
        if len(requests) > 0:
            try:
                debug("Async IOs waiting")
                asyncio.get_event_loop().run_until_complete(asyncio.wait(requests, return_when=asyncio.ALL_COMPLETED))
                debug("Async IOs complete")
            except Exception as e:
                debug(e)

    def save_session(self, sid, web_session, session) -> None:
        try:
            web_session['guardian'] = session.to_dict()
            self.cache.set(sid, dict(web_session), self.session_lifetime.total_seconds())
        except Exception as e:
            debug(e)

    def expire_session(self, sid) -> None:
        try:
           self.cache.delete(sid)
        except Exception as e:
            debug(e)

    @staticmethod
    def refresh_window():
        return datetime.timedelta(seconds = 28)

    @staticmethod
    def leeway():
        return datetime.timedelta(seconds = 28)

    async def refresh_token(self, sid, web_session, session):
        auth_data = {
            'command': 'login-token',
            'token': session.get_token(),
            #'port': 'Web', # TODO: Enable web login connection type for UserGroups
        }

        # Send synchronous to auth microservice
        try:
            response_json = await IpcUtils.send_json(port=1865, data=json.dumps(auth_data))
        except Exception as e:
            debug(e)
            return None
        rsp_data = json.loads(response_json)
        debug(rsp_data)
        # Save new token
        if rsp_data["status"] == "success":
            session.token = rsp_data['auth']['token']
            session.token_expiration =  datetime.datetime.strptime(rsp_data['auth']['tokenExpiration'], '%Y-%m-%d %H:%M:%S')
            self.save_session(sid, web_session, session)
        # Token invalid
        # TODO: Verify error for soft tokens
        elif rsp_data["error"].startwith("Failed to verify"):
            self.expire_session(sid)

