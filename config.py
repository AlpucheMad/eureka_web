import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configuración general
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY configurada. Esta variable es obligatoria.")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')
    if not SECURITY_PASSWORD_SALT:
        raise ValueError("No SECURITY_PASSWORD_SALT configurada. Esta variable es obligatoria.")
    
    # Database configuration
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    if not DB_USER or not DB_PASSWORD:
        raise ValueError("DB_USER y DB_PASSWORD son obligatorios para la conexión a la base de datos.")
    
    DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD)
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5433')
    
    # Mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
class DevelopmentConfig(Config):
    DEBUG = True
    DB_NAME = os.environ.get('DB_NAME', 'eureka_dev')
    SQLALCHEMY_DATABASE_URI = f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD_ENCODED}@{Config.DB_HOST}:{Config.DB_PORT}/{DB_NAME}"

class TestingConfig(Config):
    TESTING = True
    DB_NAME = os.environ.get('TEST_DB_NAME', 'eureka_test')
    SQLALCHEMY_DATABASE_URI = f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD_ENCODED}@{Config.DB_HOST}:{Config.DB_PORT}/{DB_NAME}"
    
    # Configuraciones para construcción de URLs en tests
    SERVER_NAME = 'localhost:5000'
    APPLICATION_ROOT = '/'
    PREFERRED_URL_SCHEME = 'http'

class ProductionConfig(Config):
    DB_NAME = os.environ.get('PROD_DB_NAME', 'eureka')
    SQLALCHEMY_DATABASE_URI = f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD_ENCODED}@{Config.DB_HOST}:{Config.DB_PORT}/{DB_NAME}"
    
    # Configuraciones específicas para producción
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}