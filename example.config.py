"""
Stuff needs to be filled out correctly. This is an example file. The app uses config.py in this directory.
"""
from tempfile import mkdtemp

class Config(object):
    DEBUG=1
	# intercepting redirects can be set to true for debugging in browser at runtime
    DEBUG_TB_INTERCEPT_REDIRECTS = True
    SECRET_KEY="MAKE A SUPER SECRET KEY"
    API_KEY="GET YOUR API KEY FROM IEX CLOUD"

    # Ensure templates are auto-reloaded
    TEMPLATES_AUTO_RELOAD = True

    # Configure session to use filesystem (instead of signed cookies)
    SESSION_FILE_DIR = mkdtemp()
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"


class ProductionConfig(Config):
    DEBUG = 0

class DevelopmentConfig(Config):
	DB_PATH = "a direct path to the db file for using with sqlite3 until sqlalchemy is fully implemented"
	SQLALCHEMY_DATABASE_URI = "sqlite:////absolute path"
	SQLALCHEMY_TRACK_MODIFICATIONS = False
class TestingConfig(Config):
    pass


