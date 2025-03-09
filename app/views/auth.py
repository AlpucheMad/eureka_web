from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_security import login_required, current_user
from flask_security.utils import login_user, logout_user, verify_password, hash_password
from flask_security.decorators import anonymous_user_required
from datetime import datetime

from app.forms.auth_forms import LoginForm, RegistrationForm, RequestResetPasswordForm, ResetPasswordForm
from app.services.user_service import UserService
from app.services.email_service import send_password_reset_email, send_confirmation_email
from app.utils.security import limiter

auth = Blueprint('auth', __name__, url_prefix='/auth')
user_service = UserService()

@auth.route('/login', methods=['GET', 'POST'])
@anonymous_user_required
@limiter.limit("5 per 5 minutes")
def login():
    """Ruta para iniciar sesión."""
    form = LoginForm()
    
    if form.validate_on_submit():
        user = user_service.get_user_by_email(form.email.data)
        
        if user and user.verify_password(form.password.data):
            if not user.is_verified:
                flash('Por favor, verifica tu correo electrónico antes de iniciar sesión.', 'warning')
                return render_template('auth/login.html', form=form, now=datetime.now())
                
            if not user.is_active:
                flash('Tu cuenta está desactivada. Contacta con el administrador.', 'error')
                return render_template('auth/login.html', form=form, now=datetime.now())
                
            login_user(user, remember=form.remember_me.data)
            user_service.update_last_login(user)
            
            next_page = request.args.get('next')
            flash('Has iniciado sesión correctamente.', 'success')
            return redirect(next_page or url_for('main.index'))
            
        else:
            flash('Email o contraseña incorrectos.', 'error')
            
    return render_template('auth/login.html', form=form, now=datetime.now())

@auth.route('/logout')
@login_required
def logout():
    """Ruta para cerrar sesión."""
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
@anonymous_user_required
def register():
    """Ruta para registro de nuevos usuarios."""
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Verificar si ya existe el correo o nombre de usuario
        if user_service.get_user_by_email(form.email.data):
            flash('Este correo electrónico ya está registrado.', 'error')
            return render_template('auth/register.html', form=form, now=datetime.now())
            
        if user_service.get_user_by_username(form.username.data):
            flash('Este nombre de usuario ya está en uso.', 'error')
            return render_template('auth/register.html', form=form, now=datetime.now())
        
        # Crear nuevo usuario
        user = user_service.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            is_verified=False,
            accept_terms=form.accept_terms.data
        )
        
        # Enviar correo de confirmación
        send_confirmation_email(user)
        
        flash('Te has registrado correctamente. Por favor, revisa tu correo para verificar tu cuenta.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', form=form, now=datetime.now())

@auth.route('/confirm/<token>')
def confirm_email(token):
    """Ruta para confirmar correo electrónico."""
    try:
        email = user_service.verify_token(token, salt='email-confirm')
        user = user_service.get_user_by_email(email)
        
        if not user:
            flash('El enlace de confirmación no es válido o ha expirado.', 'error')
            return redirect(url_for('auth.login'))
            
        if user.is_verified:
            flash('Tu cuenta ya ha sido verificada. Por favor, inicia sesión.', 'info')
            return redirect(url_for('auth.login'))
            
        user_service.verify_user(user)
        flash('Tu cuenta ha sido verificada. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
        
    except Exception:
        flash('El enlace de confirmación no es válido o ha expirado.', 'error')
        return redirect(url_for('auth.login'))

@auth.route('/reset-password', methods=['GET', 'POST'])
@anonymous_user_required
def request_reset_password():
    """Ruta para solicitar restablecimiento de contraseña."""
    form = RequestResetPasswordForm()
    
    if form.validate_on_submit():
        user = user_service.get_user_by_email(form.email.data)
        
        if user:
            send_password_reset_email(user)
            
        # Siempre mostrar el mismo mensaje para evitar enumerar usuarios
        flash('Si tu correo está registrado, recibirás un enlace para restablecer tu contraseña.', 'info')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/request_reset_password.html', form=form, now=datetime.now())

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
@anonymous_user_required
def reset_password(token):
    """Ruta para restablecer contraseña."""
    try:
        email = user_service.verify_token(token, salt='password-reset', expiration=3600)
        user = user_service.get_user_by_email(email)
        
        if not user:
            flash('El enlace de restablecimiento no es válido o ha expirado.', 'error')
            return redirect(url_for('auth.login'))
            
    except Exception:
        flash('El enlace de restablecimiento no es válido o ha expirado.', 'error')
        return redirect(url_for('auth.login'))
        
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        user_service.update_password(user, form.password.data)
        flash('Tu contraseña ha sido actualizada. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password.html', form=form, now=datetime.now(), token=token)

@auth.route('/resend-confirmation')
@anonymous_user_required
def resend_confirmation():
    """Ruta para reenviar correo de confirmación."""
    email = request.args.get('email')
    
    if not email:
        flash('Debes proporcionar un correo electrónico.', 'error')
        return redirect(url_for('auth.login'))
        
    user = user_service.get_user_by_email(email)
    
    if not user:
        # No revelar si el usuario existe o no
        flash('Si tu correo está registrado, recibirás un nuevo enlace de confirmación.', 'info')
        return redirect(url_for('auth.login'))
        
    if user.is_verified:
        flash('Tu cuenta ya ha sido verificada. Por favor, inicia sesión.', 'info')
        return redirect(url_for('auth.login'))
        
    send_confirmation_email(user)
    flash('Se ha enviado un nuevo enlace de confirmación a tu correo electrónico.', 'success')
    return redirect(url_for('auth.login')) 