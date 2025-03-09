from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail
from flask_security import Security, SQLAlchemyUserDatastore
import datetime  # Importamos el módulo datetime

from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
mail = Mail()
security = Security()

# Import utils after initializing extensions
from app.utils.security import limiter, csrf, configure_security_headers, configure_secure_session, block_suspicious_requests

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configuración de seguridad para cookies de sesión
    app = configure_secure_session(app)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)
    CORS(app)
    
    # Añadir datetime al contexto de Jinja2
    @app.context_processor
    def inject_datetime():
        return dict(datetime=datetime)
    
    # Configurar cabeceras de seguridad HTTP
    app = configure_security_headers(app)
    
    # Configurar bloqueo de peticiones sospechosas
    app = block_suspicious_requests(app)
    
    # Configurar Flask-Security
    from app.models.user import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)  # Usar el modelo Role
    security.init_app(app, user_datastore)
    
    # Configurar comportamiento de Flask-Security
    app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
    app.config['SECURITY_PASSWORD_SALT'] = app.config['SECURITY_PASSWORD_SALT']
    app.config['SECURITY_REGISTERABLE'] = True
    app.config['SECURITY_CONFIRMABLE'] = True
    app.config['SECURITY_RECOVERABLE'] = True
    app.config['SECURITY_CHANGEABLE'] = True
    app.config['SECURITY_TRACKABLE'] = True
    app.config['SECURITY_SEND_REGISTER_EMAIL'] = True
    app.config['SECURITY_EMAIL_SUBJECT_REGISTER'] = 'Bienvenido a Eureka'
    app.config['SECURITY_EMAIL_SUBJECT_PASSWORD_RESET'] = 'Restablece tu contraseña en Eureka'
    app.config['SECURITY_EMAIL_SUBJECT_PASSWORD_NOTICE'] = 'Tu contraseña ha sido cambiada'
    app.config['SECURITY_EMAIL_SUBJECT_CONFIRM'] = 'Confirma tu correo en Eureka'
    app.config['SECURITY_MSG_UNAUTHORIZED'] = ('No tienes permisos para acceder a esta página.', 'error')
    app.config['SECURITY_MSG_CONFIRMATION_REQUIRED'] = ('Por favor, confirma tu correo electrónico antes de continuar.', 'warning')
    app.config['SECURITY_MSG_USER_DOES_NOT_EXIST'] = ('Correo electrónico o contraseña incorrectos.', 'error')
    app.config['SECURITY_MSG_PASSWORD_NOT_SET'] = ('No se ha establecido una contraseña para esta cuenta.', 'error')
    app.config['SECURITY_MSG_PASSWORD_INVALID_LENGTH'] = ('La contraseña debe tener al menos %(length)s caracteres.', 'error')
    app.config['SECURITY_MSG_PASSWORD_MISMATCH'] = ('Las contraseñas no coinciden.', 'error')
    app.config['SECURITY_MSG_DISABLED_ACCOUNT'] = ('Esta cuenta está desactivada.', 'error')
    app.config['SECURITY_MSG_LOGIN'] = ('Inicia sesión para acceder a esta página.', 'info')
    
    # Register blueprints
    from app.views.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.views.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    return app 