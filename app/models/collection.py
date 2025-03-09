"""
Modelo de colección para la aplicación Eureka.
"""

from datetime import datetime
from sqlalchemy import Index, ForeignKey

from app import db

class Collection(db.Model):
    """
    Modelo de colección que permite agrupar entradas relacionadas.
    """
    __tablename__ = 'collections'
    
    # Atributos principales
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    
    # Relaciones
    user_id = db.Column(db.Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', back_populates='collections')
    entries = db.relationship('Entry', back_populates='collection', lazy='dynamic')
    
    # Campos de auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Soft delete
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Índices
    __table_args__ = (
        # Índice compuesto para búsquedas por usuario y nombre
        Index('idx_collection_user_name', 'user_id', 'name'),
        # Índice para búsquedas por fecha de creación
        Index('idx_collection_created', 'created_at'),
    )
    
    def soft_delete(self):
        """
        Realiza un borrado lógico de la colección.
        """
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        
        # También marca como eliminadas todas las entradas asociadas
        for entry in self.entries:
            if not entry.is_deleted:
                entry.soft_delete()
    
    def __repr__(self):
        """
        Representación en string del modelo.
        """
        return f'<Collection {self.name} (User: {self.user_id})>' 