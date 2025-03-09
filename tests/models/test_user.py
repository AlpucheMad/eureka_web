"""
Pruebas para el modelo User.
"""

import pytest
from datetime import datetime

from app.models import User

class TestUserModel:
    """Pruebas para el modelo User."""
    
    def test_create_user(self, db_session):
        """Prueba la creación de un usuario."""
        user = User(
            username='nuevo_usuario',
            email='nuevo@example.com',
            is_active=True,
            is_verified=False,
            theme_preference='oscuro',
            created_at=datetime.utcnow()
        )
        user.password = 'password_seguro'
        
        db_session.add(user)
        db_session.commit()
        
        saved_user = User.query.filter_by(username='nuevo_usuario').first()
        
        assert saved_user is not None
        assert saved_user.username == 'nuevo_usuario'
        assert saved_user.email == 'nuevo@example.com'
        assert saved_user.is_active is True
        assert saved_user.is_verified is False
        assert saved_user.theme_preference == 'oscuro'
    
    def test_password_hashing(self, test_user):
        """Prueba el hash y verificación de contraseñas."""
        # Verificar que la contraseña original funciona
        assert test_user.verify_password('test_password') is True
        
        # Verificar que una contraseña incorrecta no funciona
        assert test_user.verify_password('wrong_password') is False
        
        # Verificar que no podemos acceder directamente a la contraseña
        with pytest.raises(AttributeError):
            password = test_user.password
    
    def test_user_representation(self, test_user):
        """Prueba la representación en string del modelo."""
        assert str(test_user) == f'<User {test_user.username}>'
    
    def test_soft_delete(self, db_session, test_user):
        """Prueba el borrado lógico de un usuario."""
        # Verificar estado inicial
        assert test_user.is_deleted is False
        assert test_user.deleted_at is None
        
        # Realizar borrado lógico
        test_user.soft_delete()
        db_session.commit()
        
        # Verificar estado después del borrado
        updated_user = User.query.get(test_user.id)
        assert updated_user.is_deleted is True
        assert updated_user.is_active is False
        assert updated_user.deleted_at is not None
    
    def test_unique_constraints(self, db_session, test_user):
        """Prueba las restricciones de unicidad."""
        # Intentar crear un usuario con el mismo username
        duplicate_username = User(
            username='test_user',  # Duplicado
            email='different@example.com',
            is_active=True,
            is_verified=True,
            theme_preference='claro'
        )
        duplicate_username.password = 'another_password'
        
        db_session.add(duplicate_username)
        
        # Debe fallar por la restricción de unicidad
        with pytest.raises(Exception):
            db_session.commit()
        
        db_session.rollback()
        
        # Intentar crear un usuario con el mismo email
        duplicate_email = User(
            username='different_user',
            email='test@example.com',  # Duplicado
            is_active=True,
            is_verified=True,
            theme_preference='claro'
        )
        duplicate_email.password = 'another_password'
        
        db_session.add(duplicate_email)
        
        # Debe fallar por la restricción de unicidad
        with pytest.raises(Exception):
            db_session.commit()
        
        db_session.rollback() 