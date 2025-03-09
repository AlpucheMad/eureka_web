from flask import request, current_app, g, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from functools import wraps
import re

# Inicializar limitador de tasa
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    strategy="fixed-window"
)

# Inicializar protección CSRF
csrf = CSRFProtect()

def configure_security_headers(app):
    """
    Configura cabeceras de seguridad HTTP para la aplicación.
    
    Args:
        app: Instancia de la aplicación Flask.
    """
    @app.after_request
    def add_security_headers(response):
        # Protección contra XSS
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Prevenir que el navegador detecte automáticamente MIME types
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Prevenir clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        
        # Política de seguridad de contenido
        response.headers['Content-Security-Policy'] = "default-src 'self'; " \
                                                    "script-src 'self' https://cdn.jsdelivr.net; " \
                                                    "style-src 'self' https://cdn.jsdelivr.net; " \
                                                    "img-src 'self' data:; " \
                                                    "font-src 'self';"
        
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Feature Policy para mayor seguridad
        response.headers['Permissions-Policy'] = "camera=(), microphone=(), geolocation=()"
        
        return response
    
    return app

def configure_secure_session(app):
    """
    Configura parámetros seguros para las cookies de sesión.
    
    Args:
        app: Instancia de la aplicación Flask.
    """
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutos
    
    return app

def sanitize_input(text):
    """
    Sanitiza la entrada de usuario para prevenir inyecciones.
    
    Args:
        text (str): Texto a sanitizar.
        
    Returns:
        str: Texto sanitizado.
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Eliminar caracteres potencialmente peligrosos
    sanitized = re.sub(r'[<>]', '', text)
    # Prevenir SQL injection con comentarios
    sanitized = re.sub(r'--', '', sanitized)
    # Prevenir script tags
    sanitized = re.sub(r'<script|</script', '', sanitized, flags=re.IGNORECASE)
    
    return sanitized

def block_suspicious_requests(app):
    """
    Configura la detección y bloqueo de peticiones sospechosas.
    
    Args:
        app: Instancia de la aplicación Flask.
    """
    @app.before_request
    def check_request():
        # Patrones sospechosos en la URL
        suspicious_patterns = [
            r'\.\./',              # Path traversal
            r'(?:/\*|\*/)',        # SQL injection
            r'(?i)(?:<script|alert\()', # XSS
            r'(?i)union\s+select'  # SQL injection
        ]
        
        url = request.url
        for pattern in suspicious_patterns:
            if re.search(pattern, url):
                abort(403)  # Prohibido
                
        # Validar cabeceras (prevenir falsificación)
        if request.method == 'POST':
            content_type = request.headers.get('Content-Type', '')
            # Asegurar que los POSTs tienen el tipo de contenido adecuado
            if not content_type.startswith(('application/x-www-form-urlencoded', 'multipart/form-data')):
                if not request.is_json and 'application/json' not in content_type:
                    abort(400)  # Bad request
    
    return app 