"""
Modelo de usuario para la aplicación Eureka.
"""

from datetime import datetime
import uuid
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Index
from flask_login import UserMixin

from app import db, bcrypt

class User(UserMixin, db.Model):
    """
    Modelo de usuario que almacena la información de autenticación y preferencias.
    """
    __tablename__ = 'users'
    
    # Atributos principales
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    _password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Campo requerido por Flask-Security-Too desde la versión 4.0.0
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)
    
    # Campos de auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Preferencias
    theme_preference = db.Column(db.String(10), default='claro', nullable=False)
    
    # Soft delete
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Roles (requerido por Flask-Security)
    roles = db.relationship('Role', secondary='roles_users',
                          backref=db.backref('users', lazy='dynamic'))
    
    # Relaciones
    collections = db.relationship('Collection', back_populates='user', lazy='dynamic',
                                 cascade='all, delete-orphan')
    entries = db.relationship('Entry', back_populates='user', lazy='dynamic',
                             cascade='all, delete-orphan')
    tags = db.relationship('Tag', back_populates='user', lazy='dynamic',
                          cascade='all, delete-orphan')
    
    # Índices
    __table_args__ = (
        Index('idx_user_username_email', 'username', 'email'),
        Index('idx_user_active_verified', 'is_active', 'is_verified'),
    )
    
    def get_id(self):
        """
        Método requerido por Flask-Login.
        """
        return str(self.id)
    
    @property
    def is_authenticated(self):
        """
        Método requerido por Flask-Login.
        """
        return True
    
    @property
    def is_anonymous(self):
        """
        Método requerido por Flask-Login.
        """
        return False
    
    @hybrid_property
    def password(self):
        """
        Previene el acceso directo a la contraseña.
        """
        raise AttributeError('La contraseña no es un atributo legible')
    
    @password.setter
    def password(self, password):
        """
        Establece el hash de la contraseña.
        """
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def verify_password(self, password):
        """
        Verifica si la contraseña proporcionada coincide con el hash almacenado.
        """
        return bcrypt.check_password_hash(self._password_hash, password)
    
    def soft_delete(self):
        """
        Realiza un borrado lógico del usuario.
        """
        self.is_deleted = True
        self.is_active = False
        self.deleted_at = datetime.utcnow()
    
    def __repr__(self):
        """
        Representación en string del modelo.
        """
        return f'<User {self.username}>'

# Modelo de Role requerido por Flask-Security
class Role(db.Model):
    """
    Modelo de rol para la gestión de permisos.
    """
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Role {self.name}>'

# Tabla de asociación entre usuarios y roles
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'))
) 