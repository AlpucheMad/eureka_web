from datetime import datetime
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from app import db
from app.models.user import User

class UserService:
    """
    Servicio para gestionar operaciones relacionadas con usuarios.
    """
    
    def create_user(self, username, email, password, is_verified=False, is_active=True, accept_terms=False):
        """
        Crea un nuevo usuario en la base de datos.
        
        Args:
            username (str): Nombre de usuario único.
            email (str): Correo electrónico único.
            password (str): Contraseña en texto plano (será hasheada).
            is_verified (bool): Indica si el correo ha sido verificado.
            is_active (bool): Indica si la cuenta está activa.
            accept_terms (bool): Indica si el usuario ha aceptado los términos y condiciones.
            
        Returns:
            User: Instancia del usuario creado.
        """
        user = User(
            username=username,
            email=email.lower(),
            is_verified=is_verified,
            is_active=is_active
        )
        user.password = password  # Se hashea mediante el setter del modelo
        
        if accept_terms:
            user.accept_terms()
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    def get_user_by_id(self, user_id):
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id (int): ID del usuario.
            
        Returns:
            User: Usuario encontrado o None.
        """
        return User.query.filter_by(id=user_id, is_deleted=False).first()
    
    def get_user_by_email(self, email):
        """
        Obtiene un usuario por su correo electrónico.
        
        Args:
            email (str): Correo electrónico del usuario.
            
        Returns:
            User: Usuario encontrado o None.
        """
        return User.query.filter_by(email=email.lower(), is_deleted=False).first()
    
    def get_user_by_username(self, username):
        """
        Obtiene un usuario por su nombre de usuario.
        
        Args:
            username (str): Nombre de usuario.
            
        Returns:
            User: Usuario encontrado o None.
        """
        return User.query.filter_by(username=username, is_deleted=False).first()
    
    def update_password(self, user, new_password):
        """
        Actualiza la contraseña de un usuario.
        
        Args:
            user (User): Usuario cuya contraseña se actualizará.
            new_password (str): Nueva contraseña en texto plano.
            
        Returns:
            User: Usuario actualizado.
        """
        user.password = new_password  # Se hashea mediante el setter del modelo
        db.session.commit()
        return user
    
    def verify_user(self, user):
        """
        Marca un usuario como verificado.
        
        Args:
            user (User): Usuario a verificar.
            
        Returns:
            User: Usuario actualizado.
        """
        user.is_verified = True
        db.session.commit()
        return user
    
    def update_last_login(self, user):
        """
        Actualiza la fecha del último inicio de sesión.
        
        Args:
            user (User): Usuario que ha iniciado sesión.
            
        Returns:
            User: Usuario actualizado.
        """
        user.last_login = datetime.utcnow()
        db.session.commit()
        return user
    
    def generate_token(self, data, salt='default', expiration=86400):
        """
        Genera un token firmado con información proporcionada.
        
        Args:
            data (str): Información a codificar en el token.
            salt (str): Sal adicional para el proceso de firma.
            expiration (int): Tiempo de expiración en segundos.
            
        Returns:
            str: Token generado.
        """
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps(data, salt=salt)
    
    def verify_token(self, token, salt='default', expiration=86400):
        """
        Verifica un token firmado y recupera la información original.
        
        Args:
            token (str): Token a verificar.
            salt (str): Sal utilizada en la generación del token.
            expiration (int): Tiempo máximo de validez en segundos.
            
        Returns:
            str: Información decodificada del token.
            
        Raises:
            Exception: Si el token es inválido o ha expirado.
        """
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.loads(token, salt=salt, max_age=expiration) 