"""
Modelo de entrada para la aplicación Eureka.
"""

from datetime import datetime
from sqlalchemy import Index, ForeignKey, Enum
import enum

from app import db

class EntryStatus(enum.Enum):
    """
    Enumeración para los posibles estados de una entrada.
    """
    BORRADOR = 'borrador'
    PUBLICADO = 'publicado'

class Entry(db.Model):
    """
    Modelo de entrada que representa una idea o nota del usuario.
    """
    __tablename__ = 'entries'
    
    # Atributos principales
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(
        Enum(EntryStatus),
        default=EntryStatus.BORRADOR,
        nullable=False
    )
    
    # Relaciones
    user_id = db.Column(db.Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', back_populates='entries')
    
    collection_id = db.Column(db.Integer, ForeignKey('collections.id', ondelete='SET NULL'), nullable=True)
    collection = db.relationship('Collection', back_populates='entries')
    
    # Relación muchos a muchos con Tag a través de EntryTag
    tags = db.relationship('Tag', secondary='entry_tags', back_populates='entries')
    
    # Campos de auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Soft delete
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Índices
    __table_args__ = (
        # Índice para búsquedas por usuario
        Index('idx_entry_user', 'user_id'),
        # Índice para búsquedas por colección
        Index('idx_entry_collection', 'collection_id'),
        # Índice para búsquedas por estado
        Index('idx_entry_status', 'status'),
        # Índice para búsquedas por fecha de creación
        Index('idx_entry_created', 'created_at'),
        # Índice para búsqueda de texto en título
        Index('idx_entry_title', 'title'),
    )
    
    def soft_delete(self):
        """
        Realiza un borrado lógico de la entrada.
        """
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def publish(self):
        """
        Cambia el estado de la entrada a publicado.
        """
        self.status = EntryStatus.PUBLICADO
        self.updated_at = datetime.utcnow()
    
    def draft(self):
        """
        Cambia el estado de la entrada a borrador.
        """
        self.status = EntryStatus.BORRADOR
        self.updated_at = datetime.utcnow()
    
    def add_tag(self, tag):
        """
        Añade una etiqueta a la entrada si no existe ya.
        """
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag):
        """
        Elimina una etiqueta de la entrada.
        """
        if tag in self.tags:
            self.tags.remove(tag)
    
    def __repr__(self):
        """
        Representación en string del modelo.
        """
        return f'<Entry {self.title} (Status: {self.status.value})>' 