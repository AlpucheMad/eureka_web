"""
Modelos de etiqueta y relación entre etiquetas y entradas para la aplicación Eureka.
"""

from datetime import datetime
from sqlalchemy import Index, ForeignKey, UniqueConstraint

from app import db

class Tag(db.Model):
    """
    Modelo de etiqueta que permite categorizar entradas.
    """
    __tablename__ = 'tags'
    
    # Atributos principales
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    
    # Relaciones
    user_id = db.Column(db.Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', back_populates='tags')
    
    # Relación muchos a muchos con Entry a través de EntryTag
    entries = db.relationship('Entry', secondary='entry_tags', back_populates='tags')
    
    # Campos de auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Índices y restricciones
    __table_args__ = (
        # Asegura que no haya etiquetas duplicadas para un mismo usuario
        UniqueConstraint('name', 'user_id', name='uq_tag_name_user'),
        # Índice para búsquedas por nombre
        Index('idx_tag_name', 'name'),
        # Índice para búsquedas por usuario
        Index('idx_tag_user', 'user_id'),
    )
    
    def __repr__(self):
        """
        Representación en string del modelo.
        """
        return f'<Tag {self.name} (User: {self.user_id})>'


class EntryTag(db.Model):
    """
    Tabla de relación muchos a muchos entre Entry y Tag.
    """
    __tablename__ = 'entry_tags'
    
    # Claves primarias y foráneas
    entry_id = db.Column(db.Integer, ForeignKey('entries.id', ondelete='CASCADE'), primary_key=True)
    tag_id = db.Column(db.Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
    
    # Campos de auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Índices
    __table_args__ = (
        # Índice para búsquedas por entrada
        Index('idx_entrytag_entry', 'entry_id'),
        # Índice para búsquedas por etiqueta
        Index('idx_entrytag_tag', 'tag_id'),
    )
    
    def __repr__(self):
        """
        Representación en string del modelo.
        """
        return f'<EntryTag Entry: {self.entry_id}, Tag: {self.tag_id}>' 