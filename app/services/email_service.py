from flask import current_app, render_template, url_for
from flask_mail import Message
from threading import Thread
from app import mail

def _send_async_email(app, msg):
    """
    Envía un correo electrónico de forma asíncrona.
    
    Args:
        app: Instancia de la aplicación Flask.
        msg: Mensaje a enviar.
    """
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    """
    Configura y envía un correo electrónico.
    
    Args:
        to (str): Destinatario del correo.
        subject (str): Asunto del correo.
        template (str): Ruta a la plantilla para el cuerpo del correo.
        **kwargs: Variables para la plantilla.
    """
    app = current_app._get_current_object()
    msg = Message(
        subject=f"Eureka - {subject}",
        recipients=[to],
        html=render_template(template, **kwargs),
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    
    # Enviar el correo de forma asíncrona para no bloquear la aplicación
    if not app.testing:
        Thread(target=_send_async_email, args=(app, msg)).start()
    else:
        # En modo de prueba, enviar de forma síncrona
        mail.send(msg)

def send_confirmation_email(user):
    """
    Envía un correo de confirmación para verificar la cuenta.
    
    Args:
        user (User): Usuario al que se le enviará el correo.
    """
    from app.services.user_service import UserService
    user_service = UserService()
    
    token = user_service.generate_token(user.email, salt='email-confirm', expiration=86400)  # 24 horas
    
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    
    send_email(
        to=user.email,
        subject="Confirma tu cuenta",
        template="auth/email/confirmation.html",
        user=user,
        confirm_url=confirm_url
    )

def send_password_reset_email(user):
    """
    Envía un correo con instrucciones para restablecer la contraseña.
    
    Args:
        user (User): Usuario al que se le enviará el correo.
    """
    from app.services.user_service import UserService
    user_service = UserService()
    
    token = user_service.generate_token(user.email, salt='password-reset', expiration=3600)  # 1 hora
    
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    send_email(
        to=user.email,
        subject="Restablece tu contraseña",
        template="auth/email/reset_password.html",
        user=user,
        reset_url=reset_url
    ) 