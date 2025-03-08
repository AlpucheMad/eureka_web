import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'eureka-dev-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'eureka-salt'
    
    # Mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@eureka-app.com')
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        f"postgresql://{os.environ.get('DB_USER', 'eureka_user')}:{os.environ.get('DB_PASSWORD', 'Eur3ka_S3cure_P@ss')}@{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', '5433')}/{os.environ.get('DB_NAME', 'eureka_dev')}"

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        f"postgresql://{os.environ.get('DB_USER', 'eureka_user')}:{os.environ.get('DB_PASSWORD', 'Eur3ka_S3cure_P@ss')}@{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', '5433')}/eureka_test"

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"postgresql://{os.environ.get('DB_USER', 'eureka_user')}:{os.environ.get('DB_PASSWORD', 'Eur3ka_S3cure_P@ss')}@{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', '5433')}/eureka"

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}