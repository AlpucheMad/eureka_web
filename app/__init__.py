from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail
from flask_login import LoginManager
import datetime  # Importamos el módulo datetime

from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
mail = Mail()
login_manager = LoginManager()

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
    
    # Configurar Login Manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    # Cargar el usuario desde el ID de sesión
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Añadir datetime al contexto de Jinja2
    @app.context_processor
    def inject_datetime():
        return dict(datetime=datetime)
    
    # Configurar cabeceras de seguridad HTTP
    app = configure_security_headers(app)
    
    # Configurar bloqueo de peticiones sospechosas
    app = block_suspicious_requests(app)
    
    # Register blueprints
    from app.views.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.views.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from app.views.entry import entry as entry_blueprint
    app.register_blueprint(entry_blueprint)
    
    return app 