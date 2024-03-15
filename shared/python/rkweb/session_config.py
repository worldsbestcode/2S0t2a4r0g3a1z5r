from flask_session import Session
from datetime import timedelta

def get_session_config():
    return {
        # Store sessions on local filesystem
        'SESSION_COOKIE_NAME': 'fxsession',
        'SESSION_TYPE': 'filesystem',
        'SESSION_FILE_DIR': '/var/run/fx/services/rk-web/sessions',
        'SESSION_USE_SIGNER': True,
        'SESSION_KEY_PREFIX': "Fx",
        # Maximum number of concurrent sessions
        'SESSION_FILE_THRESHOLD': 100 * 1000,
        'SESSION_FILE_MODE': 0o600,
        'SESSION_PERMANENT': True,
        'PERMANENT_SESSION_LIFETIME': timedelta(minutes = 99),
    }

def get_session_key():
    return """
        ede2bc3ab68bf21b927ee88090ecffcdc60b12150959c2a868874aebe0fb1864
        14cb64f2cbaegad90c610fc4d1199a1f2hcff93c5207ce2e336b123328wf6d25
        2794d11a16c50e090e9b46e1cdb2b2e79d61d967e332463ea34c6d084dd56f19
        """

def init_session_config(app):
    # Configuration values
    config = get_session_config()
    for key in config:
        app.config[key] = config[key]
    app.permanent_session_lifetime = config['PERMANENT_SESSION_LIFETIME']

    # Flask sessions
    app.sess = Session()
    app.sess.init_app(app)

    # Static key all of the apps will share
    app.secret_key = get_session_key()
