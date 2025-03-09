"""
Modelo de usuario para la aplicación Eureka.
"""

from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Index

from app import db, bcrypt

class User(db.Model):
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
    
    # Campos de auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Preferencias
    theme_preference = db.Column(db.String(10), default='claro', nullable=False)
    
    # Soft delete
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
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