import os

class BaseConfig(object):
    # FLASK Configuration
    # SECRET KEY to be set as environment variable in production
    SECRET_KEY = 'SECRET_KEY'
    JWT_SECRET_KEY = 'JWT_SECRET_KEY'
    CSRF_SECRET_KEY = 'CSRF_SECRET_KEY'

    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    # The maximum number of items the session stores 
    # before it starts deleting some, default 500
    SESSION_FILE_THRESHOLD = 100  

    DEBUG = True
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SQLALCHEMY_DATABASE_URI='sqlite:///database.db'

    JWT_ACCESS_COOKIE_PATH = "/"
    JWT_REFRESH_COOKIE_PATH = "/api/v1/token"
    JWT_TOKEN_LOCATION = "cookies"
    JWT_CSRF_IN_COOKIES = False
    # Only allow JWT cookies to be sent over https. In production, this
    # should likely be True
    JWT_COOKIE_SECURE = False
    JWT_ACCESS_COOKIE_NAME  = 'jwt_access'
    JWT_REFRESH_COOKIE_NAME = 'jwt_refresh'
    JWT_COOKIE_CSRF_PROTECT = False

    # Game configuration
    WORD_LIST = ['3dhubs', 'marvin', 'print', 'filament', 'order', 'layer']
    ALLOWED_MISSES = 4

    # API configuration
    TOKEN_EXPIRATION = 3600
    API_BASE_URL     = 'http://localhost.localdomain:50011/api/v1/'
    API_GAMES_URL    = 'game'
    API_TOKENS_URL   = 'token'
    API_USERS_URL    = 'user'
    API_LOGIN_URL    = 'login'

class ProductionConfig(BaseConfig):
    DEBUG = False
    TOKEN_EXPIRATION = 600
    # SECRET KEY to be set as environment variable
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    SERVER_NAME='productionhost.changeme:5000'

    # Only allow JWT cookies to be sent over https. In production, this
    # should likely be True
    JWT_COOKIE_SECURE = True

class DevelopmentConfig(BaseConfig):
    ENV= 'development'
    DEBUG = True
    TESTING = True
    SERVER_NAME='localhost.localdomain:5000'
