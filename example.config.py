"""
Stuff needs to be filled out correctly. This is an example file. The app uses config.py in this directory.
"""

from tempfile import mkdtemp

class Config(object):
    DEBUG=1
    SECRET_KEY="MAKE IT SECREET"
    API_KEY="put your API key here"

    # Ensure templates are auto-reloaded
    TEMPLATES_AUTO_RELOAD = True

    # Configure session to use filesystem (instead of signed cookies)
    SESSION_FILE_DIR = mkdtemp()
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"


class ProductionConfig(Config):
    DEBUG = 0

class DevelopmentConfig(Config):
    pass
class TestingConfig(Config):
    pass


