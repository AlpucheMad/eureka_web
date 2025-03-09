"""
Pruebas para el modelo Entry.
"""

import pytest
from datetime import datetime

from app.models import Entry, Tag
from app.models.entry import EntryStatus

class TestEntryModel:
    """Pruebas para el modelo Entry."""
    
    def test_create_entry(self, db_session, test_user, test_collection):
        """Prueba la creación de una entrada."""
        entry = Entry(
            title='Nueva Entrada',
            content='Contenido de la nueva entrada',
            status=EntryStatus.BORRADOR,
            user_id=test_user.id,
            collection_id=test_collection.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db_session.add(entry)
        db_session.commit()
        
        saved_entry = Entry.query.filter_by(title='Nueva Entrada').first()
        
        assert saved_entry is not None
        assert saved_entry.title == 'Nueva Entrada'
        assert saved_entry.content == 'Contenido de la nueva entrada'
        assert saved_entry.status == EntryStatus.BORRADOR
        assert saved_entry.user_id == test_user.id
        assert saved_entry.collection_id == test_collection.id
        assert saved_entry.is_deleted is False
    
    def test_entry_without_collection(self, db_session, test_user):
        """Prueba la creación de una entrada sin colección."""
        entry = Entry(
            title='Entrada Sin Colección',
            content='Contenido de la entrada sin colección',
            status=EntryStatus.BORRADOR,
            user_id=test_user.id,
            collection_id=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db_session.add(entry)
        db_session.commit()
        
        saved_entry = Entry.query.filter_by(title='Entrada Sin Colección').first()
        
        assert saved_entry is not None
        assert saved_entry.collection_id is None
        assert saved_entry.collection is None
    
    def test_entry_relationships(self, test_entry, test_user, test_collection):
        """Prueba las relaciones de Entry con User y Collection."""
        assert test_entry.user is not None
        assert test_entry.user.id == test_user.id
        assert test_entry in test_user.entries
        
        assert test_entry.collection is not None
        assert test_entry.collection.id == test_collection.id
        assert test_entry in test_collection.entries
    
    def test_entry_status_methods(self, db_session, test_entry):
        """Prueba los métodos para cambiar el estado de una entrada."""
        # Verificar estado inicial
        assert test_entry.status == EntryStatus.BORRADOR
        
        # Cambiar a publicado
        test_entry.publish()
        db_session.commit()
        
        updated_entry = Entry.query.get(test_entry.id)
        assert updated_entry.status == EntryStatus.PUBLICADO
        
        # Cambiar a borrador
        updated_entry.draft()
        db_session.commit()
        
        final_entry = Entry.query.get(test_entry.id)
        assert final_entry.status == EntryStatus.BORRADOR
    
    def test_soft_delete(self, db_session, test_entry):
        """Prueba el borrado lógico de una entrada."""
        # Verificar estado inicial
        assert test_entry.is_deleted is False
        assert test_entry.deleted_at is None
        
        # Realizar borrado lógico
        test_entry.soft_delete()
        db_session.commit()
        
        # Verificar estado después del borrado
        updated_entry = Entry.query.get(test_entry.id)
        assert updated_entry.is_deleted is True
        assert updated_entry.deleted_at is not None
    
    def test_entry_tag_relationship(self, db_session, test_entry, test_tag):
        """Prueba la relación muchos a muchos entre Entry y Tag."""
        # Verificar estado inicial
        assert len(test_entry.tags) == 0
        assert len(test_tag.entries) == 0
        
        # Añadir etiqueta a la entrada
        test_entry.add_tag(test_tag)
        db_session.commit()
        
        # Verificar relación
        updated_entry = Entry.query.get(test_entry.id)
        updated_tag = Tag.query.get(test_tag.id)
        
        assert test_tag in updated_entry.tags
        assert test_entry in updated_tag.entries
        assert len(updated_entry.tags) == 1
        assert len(updated_tag.entries) == 1
        
        # Eliminar etiqueta de la entrada
        updated_entry.remove_tag(test_tag)
        db_session.commit()
        
        # Verificar que la relación se eliminó
        final_entry = Entry.query.get(test_entry.id)
        final_tag = Tag.query.get(test_tag.id)
        
        assert test_tag not in final_entry.tags
        assert test_entry not in final_tag.entries
        assert len(final_entry.tags) == 0
        assert len(final_tag.entries) == 0
    
    def test_entry_representation(self, test_entry):
        """Prueba la representación en string del modelo."""
        assert str(test_entry) == f'<Entry {test_entry.title} (Status: {test_entry.status.value})>' 