from tempfile import mkdtemp

class Config(object):
    DEBUG=0
	# intercepting redirects can be set to true for debugging in browser at runtime
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SECRET_KEY="thiskeyissecret&/&y&767U&&7867"
    API_KEY="pk_5853f92a8593405cb1380c7034653ae8"

    # Ensure templates are auto-reloaded
    TEMPLATES_AUTO_RELOAD = True

    # Configure session to use filesystem (instead of signed cookies)
    SESSION_FILE_DIR = mkdtemp()
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"


class ProductionConfig(Config):
    DEBUG = 0

class DevelopmentConfig(Config):
	SQLALCHEMY_DATABASE_URI = "sqlite:////home/ubuntu/pset8/finance/finance.db"
	SQLALCHEMY_TRACK_MODIFICATIONS = False
class TestingConfig(Config):
    pass


