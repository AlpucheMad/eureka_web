"""
Pruebas para el modelo Entry.
"""

import pytest
from datetime import datetime
import os

from app import db
from app.models import Entry, User, Collection, Tag
from app.models.entry import EntryStatus

class TestEntryModel:
    """Pruebas para el modelo Entry."""
    
    def test_create_entry(self, db_session, test_user, test_collection):
        """Prueba la creación de una entrada."""
        # Configurar modo prueba
        os.environ['FLASK_ENV'] = 'testing'
        
        # Crear una entrada
        entry = Entry(
            title='Test Entry Creation',
            content='This is a test entry content for creation test',
            status=EntryStatus.BORRADOR.value if os.environ.get('FLASK_ENV') == 'testing' else EntryStatus.BORRADOR,
            user_id=test_user.id,
            collection_id=test_collection.id
        )
        
        # Guardar en la base de datos
        db_session.add(entry)
        db_session.commit()
        
        # Recuperar de la base de datos
        saved_entry = Entry.query.filter_by(title='Test Entry Creation').first()
        
        # Verificar que se haya guardado correctamente
        assert saved_entry is not None
        assert saved_entry.title == 'Test Entry Creation'
        assert saved_entry.content == 'This is a test entry content for creation test'
        if os.environ.get('FLASK_ENV') == 'testing':
            assert saved_entry.status == EntryStatus.BORRADOR.value
        else:
            assert saved_entry.status == EntryStatus.BORRADOR
        assert saved_entry.user_id == test_user.id
        assert saved_entry.collection_id == test_collection.id
    
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
    
    def test_entry_relationships(self, db_session, test_user, test_collection, test_tag):
        """Prueba las relaciones de una entrada con usuario, colección y etiquetas."""
        # Configurar modo prueba
        os.environ['FLASK_ENV'] = 'testing'
        
        # Crear una entrada con relaciones
        entry = Entry(
            title='Test Entry Relationships',
            content='This is a test entry content for relationships test',
            status=EntryStatus.BORRADOR.value if os.environ.get('FLASK_ENV') == 'testing' else EntryStatus.BORRADOR,
            user_id=test_user.id,
            collection_id=test_collection.id
        )
        
        # Añadir una etiqueta
        entry.add_tag(test_tag)
        
        # Guardar en la base de datos
        db_session.add(entry)
        db_session.commit()
        
        # Recuperar de la base de datos
        saved_entry = Entry.query.filter_by(title='Test Entry Relationships').first()
        
        # Verificar relaciones
        assert saved_entry.user.id == test_user.id
        assert saved_entry.collection.id == test_collection.id
        assert len(saved_entry.tags) == 1
        assert saved_entry.tags[0].id == test_tag.id
    
    def test_entry_status_changes(self, db_session, test_user, test_collection):
        """Prueba los cambios de estado de una entrada."""
        # Configurar modo prueba
        os.environ['FLASK_ENV'] = 'testing'
        
        # Crear una entrada
        entry = Entry(
            title='Test Entry Status Changes',
            content='This is a test entry content for status changes test',
            user_id=test_user.id,
            collection_id=test_collection.id
        )
        
        # Guardar en la base de datos
        db_session.add(entry)
        db_session.commit()
        
        # Verificar estado inicial
        test_entry = Entry.query.filter_by(title='Test Entry Status Changes').first()
        if os.environ.get('FLASK_ENV') == 'testing':
            assert test_entry.status == EntryStatus.BORRADOR.value
        else:
            assert test_entry.status == EntryStatus.BORRADOR
        
        # Cambiar a publicado
        test_entry.publish()
        db_session.commit()
        
        # Verificar cambio a publicado
        updated_entry = Entry.query.filter_by(title='Test Entry Status Changes').first()
        if os.environ.get('FLASK_ENV') == 'testing':
            assert updated_entry.status == EntryStatus.PUBLICADO.value
        else:
            assert updated_entry.status == EntryStatus.PUBLICADO
        
        # Cambiar de nuevo a borrador
        updated_entry.draft()
        db_session.commit()
        
        # Verificar cambio a borrador
        final_entry = Entry.query.filter_by(title='Test Entry Status Changes').first()
        if os.environ.get('FLASK_ENV') == 'testing':
            assert final_entry.status == EntryStatus.BORRADOR.value
        else:
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