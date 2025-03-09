from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, ValidationError

class LoginForm(FlaskForm):
    """Formulario para inicio de sesión."""
    email = StringField('Correo electrónico', validators=[
        DataRequired(message="El correo electrónico es obligatorio."),
        Email(message="Introduce un correo electrónico válido.")
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message="La contraseña es obligatoria.")
    ])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar sesión')

class RegistrationForm(FlaskForm):
    """Formulario para registro de usuarios."""
    username = StringField('Nombre de usuario', validators=[
        DataRequired(message="El nombre de usuario es obligatorio."),
        Length(min=3, max=64, message="El nombre de usuario debe tener entre 3 y 64 caracteres."),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'El nombre de usuario debe comenzar con una letra y solo puede contener letras, números, puntos y guiones bajos.')
    ])
    email = StringField('Correo electrónico', validators=[
        DataRequired(message="El correo electrónico es obligatorio."),
        Email(message="Introduce un correo electrónico válido."),
        Length(max=120, message="El correo electrónico no puede tener más de 120 caracteres.")
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message="La contraseña es obligatoria."),
        Length(min=8, message="La contraseña debe tener al menos 8 caracteres."),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[@$!%*?&])[A-Za-z0-9@$!%*?&]',
               message="La contraseña debe contener al menos una letra minúscula, una mayúscula, un número y un carácter especial.")
    ])
    password_confirm = PasswordField('Confirmar contraseña', validators=[
        DataRequired(message="Debes confirmar la contraseña."),
        EqualTo('password', message="Las contraseñas no coinciden.")
    ])
    submit = SubmitField('Registrarse')

class RequestResetPasswordForm(FlaskForm):
    """Formulario para solicitar restablecimiento de contraseña."""
    email = StringField('Correo electrónico', validators=[
        DataRequired(message="El correo electrónico es obligatorio."),
        Email(message="Introduce un correo electrónico válido.")
    ])
    submit = SubmitField('Enviar instrucciones')

class ResetPasswordForm(FlaskForm):
    """Formulario para restablecer contraseña."""
    password = PasswordField('Nueva contraseña', validators=[
        DataRequired(message="La contraseña es obligatoria."),
        Length(min=8, message="La contraseña debe tener al menos 8 caracteres."),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[@$!%*?&])[A-Za-z0-9@$!%*?&]',
               message="La contraseña debe contener al menos una letra minúscula, una mayúscula, un número y un carácter especial.")
    ])
    password_confirm = PasswordField('Confirmar nueva contraseña', validators=[
        DataRequired(message="Debes confirmar la contraseña."),
        EqualTo('password', message="Las contraseñas no coinciden.")
    ])
    submit = SubmitField('Cambiar contraseña') 