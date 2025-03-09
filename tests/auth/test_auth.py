import pytest
from flask import url_for
from app import create_app, db
from app.models.user import User
from app.services.user_service import UserService
import re

def get_csrf_token(response):
    """Extrae el token CSRF de la respuesta HTML."""
    csrf_token = re.search(b'name="csrf_token" type="hidden" value="(.+?)"', response.data)
    if csrf_token:
        return csrf_token.group(1).decode('utf-8')
    return None

@pytest.fixture
def app():
    """Crea una instancia de la aplicación para pruebas."""
    app = create_app('testing')
    
    # Crear un contexto de aplicación
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        
        # Crear un usuario de prueba
        user_service = UserService()
        test_user = user_service.create_user(
            username='testuser',
            email='test@example.com',
            password='Test1234!',
            is_verified=True
        )
        
        yield app
        
        # Limpiar después de las pruebas
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente para realizar peticiones HTTP."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Runner para ejecutar comandos CLI."""
    return app.test_cli_runner()

def test_login_page(client):
    """Prueba que la página de login se carga correctamente."""
    response = client.get(url_for('auth.login'))
    assert response.status_code == 200
    assert b'Iniciar sesi' in response.data  # 'Iniciar sesión' en UTF-8

def test_register_page(client):
    """Prueba que la página de registro se carga correctamente."""
    response = client.get(url_for('auth.register'))
    assert response.status_code == 200
    assert b'Crear cuenta' in response.data

def test_reset_password_page(client):
    """Prueba que la página de solicitud de restablecimiento de contraseña se carga correctamente."""
    response = client.get(url_for('auth.request_reset_password'))
    assert response.status_code == 200
    assert b'Restablecer contrase' in response.data  # 'Restablecer contraseña' en UTF-8

def test_login_success(client):
    """Prueba un inicio de sesión exitoso."""
    # Primero obtener el token CSRF
    response = client.get(url_for('auth.login'))
    csrf_token = get_csrf_token(response)
    
    response = client.post(
        url_for('auth.login'),
        data={
            'email': 'test@example.com',
            'password': 'Test1234!',
            'remember_me': False,
            'csrf_token': csrf_token
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Has iniciado sesi' in response.data  # 'Has iniciado sesión correctamente' en UTF-8

def test_login_wrong_password(client):
    """Prueba un inicio de sesión con contraseña incorrecta."""
    # Primero obtener el token CSRF
    response = client.get(url_for('auth.login'))
    csrf_token = get_csrf_token(response)
    
    response = client.post(
        url_for('auth.login'),
        data={
            'email': 'test@example.com',
            'password': 'WrongPassword123!',
            'remember_me': False,
            'csrf_token': csrf_token
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Email o contrase' in response.data  # 'Email o contraseña incorrectos' en UTF-8

def test_login_nonexistent_user(client):
    """Prueba un inicio de sesión con un usuario que no existe."""
    # Primero obtener el token CSRF
    response = client.get(url_for('auth.login'))
    csrf_token = get_csrf_token(response)
    
    response = client.post(
        url_for('auth.login'),
        data={
            'email': 'nonexistent@example.com',
            'password': 'Test1234!',
            'remember_me': False,
            'csrf_token': csrf_token
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Email o contrase' in response.data  # 'Email o contraseña incorrectos' en UTF-8

def test_register_success(client):
    """Prueba un registro exitoso."""
    # Primero obtener el token CSRF
    response = client.get(url_for('auth.register'))
    csrf_token = get_csrf_token(response)
    
    response = client.post(
        url_for('auth.register'),
        data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewUser1234!',
            'password_confirm': 'NewUser1234!',
            'csrf_token': csrf_token
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Te has registrado correctamente' in response.data

def test_register_existing_email(client):
    """Prueba un registro con un correo electrónico ya existente."""
    # Primero obtener el token CSRF
    response = client.get(url_for('auth.register'))
    csrf_token = get_csrf_token(response)
    
    response = client.post(
        url_for('auth.register'),
        data={
            'username': 'anotheruser',
            'email': 'test@example.com',  # Email ya existente
            'password': 'AnotherUser1234!',
            'password_confirm': 'AnotherUser1234!',
            'csrf_token': csrf_token
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Este correo electr' in response.data  # 'Este correo electrónico ya está registrado' en UTF-8

def test_register_existing_username(client):
    """Prueba un registro con un nombre de usuario ya existente."""
    # Primero obtener el token CSRF
    response = client.get(url_for('auth.register'))
    csrf_token = get_csrf_token(response)
    
    response = client.post(
        url_for('auth.register'),
        data={
            'username': 'testuser',  # Username ya existente
            'email': 'another@example.com',
            'password': 'AnotherUser1234!',
            'password_confirm': 'AnotherUser1234!',
            'csrf_token': csrf_token
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Este nombre de usuario ya est' in response.data  # 'Este nombre de usuario ya está en uso' en UTF-8

def test_logout(client):
    """Prueba el cierre de sesión."""
    # Primero obtener el token CSRF
    response = client.get(url_for('auth.login'))
    csrf_token = get_csrf_token(response)
    
    # Iniciar sesión
    client.post(
        url_for('auth.login'),
        data={
            'email': 'test@example.com',
            'password': 'Test1234!',
            'remember_me': False,
            'csrf_token': csrf_token
        }
    )
    
    # Luego cerrar sesión
    response = client.get(url_for('auth.logout'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Has cerrado sesi' in response.data  # 'Has cerrado sesión correctamente' en UTF-8

def test_request_reset_password(client):
    """Prueba la solicitud de restablecimiento de contraseña."""
    # Primero obtener el token CSRF
    response = client.get(url_for('auth.request_reset_password'))
    csrf_token = get_csrf_token(response)
    
    response = client.post(
        url_for('auth.request_reset_password'),
        data={
            'email': 'test@example.com',
            'csrf_token': csrf_token
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Si tu correo est' in response.data  # 'Si tu correo está registrado, recibirás un enlace...' en UTF-8 