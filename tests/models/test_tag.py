"""
Pruebas para los modelos Tag y EntryTag.
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models import Tag, Entry, EntryTag

class TestTagModel:
    """Pruebas para el modelo Tag."""
    
    def test_create_tag(self, db_session, test_user):
        """Prueba la creación de una etiqueta."""
        tag = Tag(
            name='nueva_etiqueta',
            user_id=test_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db_session.add(tag)
        db_session.commit()
        
        saved_tag = Tag.query.filter_by(name='nueva_etiqueta').first()
        
        assert saved_tag is not None
        assert saved_tag.name == 'nueva_etiqueta'
        assert saved_tag.user_id == test_user.id
    
    def test_tag_user_relationship(self, test_tag, test_user):
        """Prueba la relación entre Tag y User."""
        assert test_tag.user is not None
        assert test_tag.user.id == test_user.id
        assert test_tag in test_user.tags
    
    def test_tag_unique_constraint(self, db_session, test_user, test_tag):
        """Prueba la restricción de unicidad de etiquetas por usuario."""
        # Intentar crear una etiqueta con el mismo nombre para el mismo usuario
        duplicate_tag = Tag(
            name='test_tag',  # Mismo nombre que test_tag
            user_id=test_user.id,  # Mismo usuario
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db_session.add(duplicate_tag)
        
        # Debe fallar por la restricción de unicidad
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Crear una etiqueta con el mismo nombre pero para otro usuario
        another_user = db_session.query(test_user.__class__).filter(
            test_user.__class__.id != test_user.id
        ).first()
        
        if not another_user:
            # Crear otro usuario si no existe
            another_user = test_user.__class__(
                username='another_user',
                email='another@example.com',
                is_active=True,
                is_verified=True,
                theme_preference='claro',
                created_at=datetime.utcnow()
            )
            another_user.password = 'test_password'
            db_session.add(another_user)
            db_session.commit()
        
        # Ahora crear la etiqueta con el mismo nombre pero para otro usuario
        same_name_different_user = Tag(
            name='test_tag',  # Mismo nombre que test_tag
            user_id=another_user.id,  # Diferente usuario
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db_session.add(same_name_different_user)
        db_session.commit()
        
        # Verificar que se creó correctamente
        saved_tag = Tag.query.filter_by(name='test_tag', user_id=another_user.id).first()
        assert saved_tag is not None
        assert saved_tag.name == 'test_tag'
        assert saved_tag.user_id == another_user.id
    
    def test_tag_representation(self, test_tag):
        """Prueba la representación en string del modelo."""
        assert str(test_tag) == f'<Tag {test_tag.name} (User: {test_tag.user_id})>'

class TestEntryTagModel:
    """Pruebas para el modelo EntryTag (tabla de relación)."""
    
    def test_entry_tag_relationship(self, db_session, test_entry, test_tag):
        """Prueba la creación de una relación entre Entry y Tag."""
        # Añadir la etiqueta a la entrada
        test_entry.add_tag(test_tag)
        db_session.commit()
        
        # Verificar que la relación existe en la tabla de relación
        entry_tag = db_session.query(EntryTag).filter_by(
            entry_id=test_entry.id,
            tag_id=test_tag.id
        ).first()
        
        assert entry_tag is not None
        assert entry_tag.entry_id == test_entry.id
        assert entry_tag.tag_id == test_tag.id
        
        # Verificar que la relación es bidireccional
        assert test_tag in test_entry.tags
        assert test_entry in test_tag.entries
    
    def test_entry_tag_unique_constraint(self, db_session, test_entry, test_tag):
        """Prueba la restricción de unicidad en la tabla de relación."""
        # Añadir la etiqueta a la entrada
        test_entry.add_tag(test_tag)
        db_session.commit()
        
        # Intentar añadir la misma etiqueta otra vez
        # El método add_tag debería evitar duplicados
        test_entry.add_tag(test_tag)
        db_session.commit()
        
        # Verificar que solo hay una relación
        entry_tags = db_session.query(EntryTag).filter_by(
            entry_id=test_entry.id,
            tag_id=test_tag.id
        ).all()
        
        assert len(entry_tags) == 1
    
    def test_entry_tag_representation(self, db_session, test_entry, test_tag):
        """Prueba la representación en string del modelo EntryTag."""
        # Añadir la etiqueta a la entrada
        test_entry.add_tag(test_tag)
        db_session.commit()
        
        # Obtener la relación
        entry_tag = db_session.query(EntryTag).filter_by(
            entry_id=test_entry.id,
            tag_id=test_tag.id
        ).first()
        
        assert str(entry_tag) == f'<EntryTag Entry: {test_entry.id}, Tag: {test_tag.id}>' 