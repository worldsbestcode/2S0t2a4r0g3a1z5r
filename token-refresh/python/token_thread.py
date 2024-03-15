import os
import json
import time
import datetime
import asyncio

from cachelib.file import FileSystemCache
from flask_session.sessions import FileSystemSession

from rkweb.ipc import IpcUtils
from rkweb.session import AuthSession
from rkweb.session_config import get_session_config

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

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

def debug(msg):
    #f = open("/tmp/token_thread.txt", "a")
    #f.write(str(msg) + "\n")
    #f.close()
    ...

class TokenThread(object):
    """
    Keeps the Flask session JWTs fresh so that the user
    is not logged out when their JWT expires.
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

        # New async processing thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Try to refresh tokens every few seconds
        while self.running:
            next_refresh = self.refresh_tokens()

            # Sleep between 2 and 20 seconds
            # Depending on when the next JWT to refresh is
            if self.running:
                # How many seconds till the next refresh window
                now = datetime.datetime.utcnow()
                till_next_refresh = 9999
                if next_refresh and now > next_refresh:
                    till_next_refresh = 0
                elif next_refresh:
                    till_next_refresh = (next_refresh - now).seconds

                if till_next_refresh > 20:
                    till_next_refresh = 20
                elif till_next_refresh < 2:
                    till_next_refresh = 2

                time.sleep(till_next_refresh)

        # Done
        loop.stop()
        self.shutdown()

    def refresh_tokens(self):
        min_refresh = None

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
            try:
                web_session = FileSystemSession(data, sid=sid)
            except Exception as e:
                debug(e)
                continue

            try:
                session = AuthSession()
                session.from_dict(web_session['auth'])
            except Exception as e:
                debug(e)
                continue

            now = datetime.datetime.utcnow()
            refresh_starts = (session.token_expiration - TokenThread.refresh_window())

            debug("TOKEN: " + str(session.get_token()))
            debug("EXPIRES: " + str(session.token_expiration))
            debug("NOW    : " + str(now))

            # Session is expired
            if (session.last_access + self.session_lifetime) < now:
                self.expire_session(sid)
            # Token is expired
            elif (session.token_expiration + TokenThread.leeway()) < now:
                self.expire_session(sid)
            # Token is within renewal threshold
            elif refresh_starts < now:
                requests.append(self.refresh_token(sid, web_session, session))
            # Record soonest to come, but not yet here token refresh times
            elif not min_refresh or refresh_starts < min_refresh:
                min_refresh = refresh_starts

        # Process token updates
        debug(str(len(requests)) + " async to perform")
        if len(requests) > 0:
            try:
                asyncio.get_event_loop().run_until_complete(asyncio.wait(requests, return_when=asyncio.ALL_COMPLETED))
            except Exception as e:
                debug(e)

        return min_refresh

    def save_session(self, sid, web_session, session) -> None:
        try:
            web_session['auth'] = session.to_dict()
            debug("SAVE TOKEN: " + sid + "=" + web_session['auth']['token'])
            self.cache.set(key=sid, value=dict(web_session), timeout=self.session_lifetime.total_seconds())
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
            'source': 'Web',
            'refresh': True,
        }

        # Send synchronous to auth microservice
        try:
            response_json = await IpcUtils.send_json(port=1865, data=json.dumps(auth_data))
        except Exception as e:
            debug(e)
            return None
        rsp_data = json.loads(response_json)
        # Save new token
        if rsp_data["status"] == "success":
            session.token = rsp_data['auth']['token']
            session.token_expiration = datetime.datetime.strptime(rsp_data['auth']['tokenExpiration'], DATETIME_FORMAT)
            self.save_session(sid, web_session, session)
        # Token invalid
        elif rsp_data["error"].startswith("Failed to verify") or rsp_data["error"].startswith("JWT verification error"):
            self.expire_session(sid)

# Run thread
thread = TokenThread()
thread.run()
