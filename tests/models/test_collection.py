"""
Pruebas para el modelo Collection.
"""

import pytest
from datetime import datetime

from app.models import Collection, Entry

class TestCollectionModel:
    """Pruebas para el modelo Collection."""
    
    def test_create_collection(self, db_session, test_user):
        """Prueba la creación de una colección."""
        collection = Collection(
            name='Nueva Colección',
            description='Descripción de la nueva colección',
            user_id=test_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db_session.add(collection)
        db_session.commit()
        
        saved_collection = Collection.query.filter_by(name='Nueva Colección').first()
        
        assert saved_collection is not None
        assert saved_collection.name == 'Nueva Colección'
        assert saved_collection.description == 'Descripción de la nueva colección'
        assert saved_collection.user_id == test_user.id
        assert saved_collection.is_deleted is False
    
    def test_collection_user_relationship(self, test_collection, test_user):
        """Prueba la relación entre Collection y User."""
        assert test_collection.user is not None
        assert test_collection.user.id == test_user.id
        assert test_collection in test_user.collections
    
    def test_collection_representation(self, test_collection):
        """Prueba la representación en string del modelo."""
        assert str(test_collection) == f'<Collection {test_collection.name} (User: {test_collection.user_id})>'
    
    def test_soft_delete(self, db_session, test_collection, test_entry):
        """Prueba el borrado lógico de una colección y sus entradas asociadas."""
        # Verificar estado inicial
        assert test_collection.is_deleted is False
        assert test_collection.deleted_at is None
        assert test_entry.is_deleted is False
        assert test_entry.deleted_at is None
        
        # Realizar borrado lógico
        test_collection.soft_delete()
        db_session.commit()
        
        # Verificar estado después del borrado
        updated_collection = Collection.query.get(test_collection.id)
        updated_entry = Entry.query.get(test_entry.id)
        
        assert updated_collection.is_deleted is True
        assert updated_collection.deleted_at is not None
        
        # Verificar que la entrada asociada también se marcó como eliminada
        assert updated_entry.is_deleted is True
        assert updated_entry.deleted_at is not None
    
    def test_collection_entries_relationship(self, db_session, test_collection, test_user):
        """Prueba la relación entre Collection y Entry."""
        # Crear varias entradas para la colección
        for i in range(3):
            entry = Entry(
                title=f'Entry {i}',
                content=f'Content for entry {i}',
                user_id=test_user.id,
                collection_id=test_collection.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db_session.add(entry)
        
        db_session.commit()
        
        # Verificar que las entradas están asociadas a la colección
        assert test_collection.entries.count() == 4  # 3 nuevas + 1 de fixture
        
        # Verificar que podemos acceder a las entradas
        entries = list(test_collection.entries)
        assert len(entries) == 4
        
        # Verificar que cada entrada tiene la colección correcta
        for entry in entries:
            assert entry.collection_id == test_collection.id
            assert entry.collection is test_collection 