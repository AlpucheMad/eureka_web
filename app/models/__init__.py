"""
Módulo de modelos para la aplicación Eureka.

Este paquete contiene todos los modelos de datos utilizados por la aplicación,
implementados con SQLAlchemy ORM.
"""

from app.models.user import User
from app.models.collection import Collection
from app.models.entry import Entry
from app.models.tag import Tag, EntryTag

__all__ = ['User', 'Collection', 'Entry', 'Tag', 'EntryTag'] 