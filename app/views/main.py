from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from datetime import datetime
from app.services.entry_service import EntryService
from app.models.tag import Tag

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return redirect(url_for('main.app_shell'))

@main.route('/app')
@login_required
def app_shell():
    """Renderiza la shell de la aplicación SPA"""
    try:
        # Cargar datos necesarios para la vista principal
        entry_service = EntryService()
        entries = entry_service.get_entries_by_user(
            user_id=current_user.id,
            page=1,
            per_page=20
        )
        tags = Tag.query.filter_by(user_id=current_user.id).all()
        
        # Renderizar la plantilla de entradas directamente
        return render_template('entries/index.html', 
                               entries=entries, 
                               tags=tags,
                               now=datetime.now())
    except Exception as e:
        # Manejar cualquier excepción
        import traceback
        traceback.print_exc()  # Para depuración en consola
        flash(f'Error al cargar la aplicación: {str(e)}', 'error')
        return render_template('base_app.html')

@main.route('/terms')
def terms():
    return render_template('terms.html', now=datetime.now())

@main.route('/privacy')
def privacy():
    return render_template('privacy.html', now=datetime.now())