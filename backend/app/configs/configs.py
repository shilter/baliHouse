import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'

# cek apakah file ada
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    print(f"File .env tidak ditemukan di: {ENV_PATH}")

class DevConfig:
    __conf = {
        "secret_key": os.getenv('secret'),
        "upload_folder": "static/downloads",
        "file_path": None,
        "file":None,
        "page":os.getenv('page'),
        "per_page":os.getenv('per_page'),
        "MAIL_SERVER": "{mail_host}".format(mail_host=os.getenv('mail_host')),
        "MAIL_PORT": os.getenv('mail_port'),
        "MAIL_USERNAME": "{mail_user}".format(mail_user=os.getenv('mail_user')),
        "MAIL_PASSWORD": "{mail_pass}".format(mail_pass=os.getenv('mail_password')),
        "MAIL_USE_TLS": True,
        "MAIL_USE_SSL": False,
        "MAIL_DEBUG": 1,
        "MAIL_DEFAULT_SENDER":"Green Digital Platform <no-reply@treemedia.green>",
        "FLASK_ENV":os.getenv('FLASK_ENV')
    }
    __setters = [
        "secret_key",
        "upload_folder",
        "file",
        "file_path",
        "page",
        "per_page",
        "MAIL_SERVER",
        "MAIL_PORT",
        "MAIL_USE_TLS",
        "MAIL_USE_SSL",
        "MAIL_DEBUG",
        "MAIL_USERNAME",
        "MAIL_PASSWORD",
        "MAIL_DEFAULT_SENDER",
        "FLASK_ENV"
    ]

    def __init__(self):
        pass

    @staticmethod
    def config(name):
        return DevConfig.__conf[name]

    @staticmethod
    def set(name, value):
        if name in DevConfig.__setters:
            DevConfig.__conf[name] = value
        else:
            raise NameError("Name not accepted in set() method")

class ConfigProduction:
    __conf = {
        "secret_key": os.getenv('prod_secret'),
        "upload_folder": "static/downloads",
        "file_path": None,
        "file":None,
        "page": os.getenv('prod_page'),
        "per_page": os.getenv('prod_per_page'),
        "MAIL_SERVER": "{mail_host}".format(mail_host=os.getenv('prod_mail_host')),
        "MAIL_PORT": os.getenv('prod_mail_port'),
        "MAIL_USERNAME": "{mail_user}".format(mail_user=os.getenv('prod_mail_user')),
        "MAIL_PASSWORD": "{mail_pass}".format(mail_pass=os.getenv('prod_mail_password')),
        "MAIL_USE_TLS": True,
        "MAIL_USE_SSL": False,
        "MAIL_DEBUG": 0,
        "FLASK_ENV":os.getenv('FLASK_ENV'),
        "MAIL_DEFAULT_SENDER":"Green Digital Platform <no-reply@treemedia.green>",
    }
    __setters = [
        "secret_key",
        "upload_folder",
        "file",
        "file_path",
        "page",
        "per_page",
        "MAIL_SERVER",
        "MAIL_PORT",
        "MAIL_USE_TLS",
        "MAIL_USE_SSL",
        "MAIL_DEBUG",
        "MAIL_USERNAME",
        "MAIL_PASSWORD",
        "FLASK_ENV",
        "MAIL_DEFAULT_SENDER"
    ]

    def __init__(self):
        pass

    @staticmethod
    def config(name):
        return ConfigProduction.__conf[name]

    @staticmethod
    def set(name, value):
        if name in ConfigProduction.__setters:
            ConfigProduction.__conf[name] = value
        else:
            raise NameError("Name not accepted in set() method")


class ConfigStagging:
    __conf = {
        "secret_key": os.getenv('staging_secret'),
        "upload_folder": "static/downloads",
        "file_path": None,
        "file":None,
        "page":os.getenv('staging_page'),
        "per_page":os.getenv('staging_per_page'),
        "MAIL_SERVER": "{mail_host}".format(mail_host=os.getenv('staging_mail_host')),
        "MAIL_PORT": os.getenv('staging_mail_port'),
        "MAIL_USERNAME": "{mail_user}".format(mail_user=os.getenv('staging_mail_user')),
        "MAIL_PASSWORD": "{mail_pass}".format(mail_pass=os.getenv('staging_mail_password')),
        "MAIL_USE_TLS": True,
        "MAIL_USE_SSL": False,
        "MAIL_DEBUG": 0,
        "FLASK_ENV":os.getenv('FLASK_ENV'),
        "MAIL_DEFAULT_SENDER":"Green Digital Platform <no-reply@treemedia.green>"
    }
    __setters = [
        "secret_key",
        "upload_folder",
        "file",
        "file_path",
        "page",
        "per_page",
        "MAIL_SERVER",
        "MAIL_PORT",
        "MAIL_USE_TLS",
        "MAIL_USE_SSL",
        "MAIL_DEBUG",
        "MAIL_USERNAME",
        "MAIL_PASSWORD",
        "FLASK_ENV",
        "MAIL_DEFAULT_SENDER"
    ]

    def __init__(self):
        pass

    @staticmethod
    def config(name):
        return ConfigStagging.__conf[name]

    @staticmethod
    def set(name, value):
        if name in ConfigStagging.__setters:
            ConfigStagging.__conf[name] = value
        else:
            raise NameError("Name not accepted in set() method")


class ProductionConfig(ConfigProduction):
    DEBUG = os.getenv('prod_debug')
    TESTING = os.getenv('prod_testing')
    SECRET_KEY = os.urandom(16).hex()
    JWT_SECRET_KEY = os.getenv('prod_secret')
    JWT_ALGORITHM = os.getenv('prod_algorithm')
    MAIL_DEBUG = ConfigProduction.config('MAIL_DEBUG')
    MAIL_SERVER = ConfigProduction.config('MAIL_SERVER')
    MAIL_PORT = ConfigProduction.config('MAIL_PORT')
    MAIL_USERNAME = ConfigProduction.config('MAIL_USERNAME')
    MAIL_PASSWORD  = ConfigProduction.config('MAIL_PASSWORD')
    MAIL_USE_TLS = ConfigProduction.config('MAIL_USE_TLS')
    MAIL_USE_SSL = ConfigProduction.config('MAIL_USE_SSL')
    MAIL_DEFAULT_SENDER = ConfigProduction.config('MAIL_DEFAULT_SENDER')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('prod_tracking')
    SQLALCHEMY_DATABASE_URI = '{connection}://{user}:{pw}@{host}:{port}/{db}'.format(
        connection='{cfg}'.format(cfg=os.getenv('prod_connection')),
        user='{username}'.format(username=os.getenv('prod_user')),
        pw='{password}'.format(password=os.getenv('prod_password')),
        host='{host}'.format(host=os.getenv('prod_dsn')),
        port='{port}'.format(port=os.getenv('prod_port')),
        db='{database}'.format(database=os.getenv('prod_database'))
    )

class StaggingConfig(ConfigStagging):
    DEBUG = os.getenv('staging_debug')
    TESTING = os.getenv('staging_testing')
    SECRET_KEY = os.urandom(16).hex()
    JWT_SECRET_KEY = os.getenv('staging_secret')
    JWT_ALGORITHM = os.getenv('staging_algorithm')
    MAIL_DEBUG = ConfigStagging.config('MAIL_DEBUG')
    MAIL_SERVER = ConfigStagging.config('MAIL_SERVER')
    MAIL_PORT = ConfigStagging.config('MAIL_PORT')
    MAIL_USERNAME = ConfigStagging.config('MAIL_USERNAME')
    MAIL_PASSWORD  = ConfigStagging.config('MAIL_PASSWORD')
    MAIL_USE_TLS = ConfigStagging.config('MAIL_USE_TLS')
    MAIL_USE_SSL = ConfigStagging.config('MAIL_USE_SSL')
    MAIL_DEFAULT_SENDER = ConfigStagging.config('MAIL_DEFAULT_SENDER')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('staging_tracking')
    SQLALCHEMY_DATABASE_URI = '{connection}://{user}:{pw}@{host}:{port}/{db}'.format(
        connection='{cfg}'.format(cfg=os.getenv('staging_connection')),
        user='{username}'.format(username=os.getenv('staging_username')),
        pw='{password}'.format(password=os.getenv('staging_password')),
        host='{host}'.format(host=os.getenv('staging_dsn')),
        port='{port}'.format(port=os.getenv('staging_port')),
        db='{database}'.format(database=os.getenv('staging_database'))
    )

class DevelopmentConfig(DevConfig):
    DEVELOPMENT = os.getenv('development')
    DEBUG = os.getenv('debug')
    SECRET_KEY = os.urandom(16).hex()
    JWT_SECRET_KEY = os.getenv('secret')
    JWT_ALGORITHM = os.getenv('algorithm')
    MAIL_DEBUG = DevConfig.config('MAIL_DEBUG')
    MAIL_SERVER = DevConfig.config('MAIL_SERVER')
    MAIL_PORT = DevConfig.config('MAIL_PORT')
    MAIL_USERNAME = DevConfig.config('MAIL_USERNAME')
    MAIL_PASSWORD  = DevConfig.config('MAIL_PASSWORD')
    MAIL_USE_TLS = DevConfig.config('MAIL_USE_TLS')
    MAIL_USE_SSL = DevConfig.config('MAIL_USE_SSL')
    MAIL_DEFAULT_SENDER = DevConfig.config('MAIL_DEFAULT_SENDER')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('tracking')
    SQLALCHEMY_DATABASE_URI = '{connection}://{user}:{pw}@{host}:{port}/{db}'.format(
        connection='{cfg}'.format(cfg=os.getenv('connection')),
        user='{username}'.format(username=os.getenv('username')),
        pw='{password}'.format(password=os.getenv('password')),
        host='{host}'.format(host=os.getenv('dsn')),
        port='{port}'.format(port=os.getenv('port')),
        db='{database}'.format(database=os.getenv('database'))
    )

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'stagging':StaggingConfig
}