"""
Configuración y fixtures para las pruebas de la aplicación Eureka.
"""

import os
import pytest
from datetime import datetime

from app import create_app, db
from app.models import User, Collection, Entry, Tag, EntryTag
from app.models.entry import EntryStatus

@pytest.fixture(scope='session')
def app():
    """Crea una instancia de la aplicación para las pruebas."""
    # Configurar la aplicación para pruebas
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app('testing')
    
    # Establecer el contexto de la aplicación
    with app.app_context():
        # Crear todas las tablas en la base de datos de prueba
        db.create_all()
        
        yield app
        
        # Limpiar después de las pruebas
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """Crea un cliente de prueba para la aplicación."""
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def db_session(app):
    """Proporciona una sesión de base de datos para las pruebas."""
    # Iniciar una transacción
    connection = db.engine.connect()
    transaction = connection.begin()
    
    # Crear una sesión usando la conexión
    session = db.create_scoped_session(
        options=dict(bind=connection, binds={})
    )
    
    # Reemplazar la sesión global con nuestra sesión de prueba
    db.session = session
    
    yield session
    
    # Rollback de la transacción y limpieza
    transaction.rollback()
    connection.close()
    session.remove()

@pytest.fixture
def test_user(db_session):
    """Crea un usuario de prueba."""
    user = User(
        username='test_user',
        email='test@example.com',
        is_active=True,
        is_verified=True,
        theme_preference='claro',
        created_at=datetime.utcnow()
    )
    user.password = 'test_password'
    db_session.add(user)
    db_session.commit()
    
    return user

@pytest.fixture
def test_collection(db_session, test_user):
    """Crea una colección de prueba."""
    collection = Collection(
        name='Test Collection',
        description='A test collection',
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(collection)
    db_session.commit()
    
    return collection

@pytest.fixture
def test_entry(db_session, test_user, test_collection):
    """Crea una entrada de prueba."""
    entry = Entry(
        title='Test Entry',
        content='This is a test entry content',
        status=EntryStatus.BORRADOR,
        user_id=test_user.id,
        collection_id=test_collection.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(entry)
    db_session.commit()
    
    return entry

@pytest.fixture
def test_tag(db_session, test_user):
    """Crea una etiqueta de prueba."""
    tag = Tag(
        name='test_tag',
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(tag)
    db_session.commit()
    
    return tag 