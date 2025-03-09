from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, abort, make_response
from flask_login import login_required, current_user
from datetime import datetime
import bleach
import markdown

from app.services.entry_service import EntryService
from app.models.entry import EntryStatus
from app.models.tag import Tag

# Inicializar el blueprint
entry = Blueprint('entry', __name__, url_prefix='/entries')
entry_service = EntryService()

# Configuración para sanitización de HTML con Bleach
ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 
    'strong', 'ul', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'hr',
    'table', 'thead', 'tbody', 'tr', 'th', 'td', 'img'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    '*': ['class']
}

# Verificar si es una solicitud HTMX
def is_htmx_request():
    return request.headers.get('HX-Request') == 'true'

# =====================================
# Rutas completas (para navegación directa)
# =====================================

@entry.route('/', methods=['GET'])
@login_required
def list_entries():
    """
    Muestra la lista de entradas (vista completa).
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    tag_id = request.args.get('tag_id', None, type=int)
    
    entries = entry_service.get_entries_by_user(
        user_id=current_user.id,
        page=page,
        per_page=per_page,
        tag_id=tag_id
    )
    
    # Obtener todas las etiquetas para el sidebar
    tags = Tag.query.filter_by(user_id=current_user.id).all()
    
    return render_template(
        'entries/list.html',
        entries=entries,
        tags=tags,
        title="Mis Entradas",
        now=datetime.now()
    )

@entry.route('/new', methods=['GET'])
@login_required
def new_entry():
    """
    Muestra el formulario para crear una nueva entrada (vista completa).
    """
    return render_template(
        'entries/edit.html',
        entry=None,
        title="Nueva Entrada",
        now=datetime.now()
    )

@entry.route('/<int:entry_id>', methods=['GET'])
@login_required
def view_entry(entry_id):
    """
    Muestra una entrada específica (vista completa).
    """
    entry = entry_service.get_entry_by_id(entry_id)
    
    if not entry or entry.user_id != current_user.id:
        abort(404)
    
    # Convertir Markdown a HTML para la vista
    html_content = markdown.markdown(
        entry.content,
        extensions=['extra', 'codehilite', 'nl2br']
    )
    
    return render_template(
        'entries/view.html',
        entry=entry,
        html_content=html_content,
        title=entry.title,
        now=datetime.now()
    )

@entry.route('/<int:entry_id>/edit', methods=['GET'])
@login_required
def edit_entry(entry_id):
    """
    Muestra el formulario para editar una entrada (vista completa).
    """
    entry = entry_service.get_entry_by_id(entry_id)
    
    if not entry or entry.user_id != current_user.id:
        abort(404)
    
    # Preparar tags como string para el formulario
    tags = ','.join([tag.name for tag in entry.tags])
    
    return render_template(
        'entries/edit.html',
        entry=entry,
        tags=tags,
        title=f"Editar: {entry.title}",
        now=datetime.now()
    )

@entry.route('/trash', methods=['GET'])
@login_required
def trash():
    """
    Muestra las entradas en la papelera (vista completa).
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    entries = entry_service.get_entries_in_trash(
        user_id=current_user.id,
        page=page,
        per_page=per_page
    )
    
    return render_template(
        'entries/trash.html',
        entries=entries,
        title="Papelera",
        now=datetime.now()
    )

# =====================================
# Rutas para vistas parciales (HTMX)
# =====================================

@entry.route('/partial', methods=['GET'])
@login_required
def list_entries_partial():
    """
    Muestra la lista de entradas (vista parcial para HTMX).
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    tag_id = request.args.get('tag_id', None, type=int)
    
    entries = entry_service.get_entries_by_user(
        user_id=current_user.id,
        page=page,
        per_page=per_page,
        tag_id=tag_id
    )
    
    return render_template(
        'entries/partials/list_entries.html',
        entries=entries
    )

@entry.route('/new/partial', methods=['GET'])
@login_required
def new_entry_partial():
    """
    Muestra el formulario para crear una nueva entrada (vista parcial para HTMX).
    """
    return render_template(
        'entries/partials/edit_form.html',
        entry=None
    )

@entry.route('/<int:entry_id>/partial', methods=['GET'])
@login_required
def view_entry_partial(entry_id):
    """
    Muestra una entrada específica (vista parcial para HTMX).
    """
    entry = entry_service.get_entry_by_id(entry_id)
    
    if not entry or entry.user_id != current_user.id:
        return '<div class="p-4 bg-red-100 text-red-700 rounded">Entrada no encontrada</div>', 404
    
    # Convertir Markdown a HTML para la vista
    html_content = markdown.markdown(
        entry.content,
        extensions=['extra', 'codehilite', 'nl2br']
    )
    
    return render_template(
        'entries/partials/view_entry.html',
        entry=entry,
        html_content=html_content
    )

@entry.route('/<int:entry_id>/edit/partial', methods=['GET'])
@login_required
def edit_entry_partial(entry_id):
    """
    Muestra el formulario para editar una entrada (vista parcial para HTMX).
    """
    entry = entry_service.get_entry_by_id(entry_id)
    
    if not entry or entry.user_id != current_user.id:
        return '<div class="p-4 bg-red-100 text-red-700 rounded">Entrada no encontrada</div>', 404
    
    # Preparar tags como string para el formulario
    tags = ','.join([tag.name for tag in entry.tags])
    
    return render_template(
        'entries/partials/edit_form.html',
        entry=entry,
        tags=tags
    )

@entry.route('/trash/partial', methods=['GET'])
@login_required
def trash_partial():
    """
    Muestra las entradas en la papelera (vista parcial para HTMX).
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    entries = entry_service.get_entries_in_trash(
        user_id=current_user.id,
        page=page,
        per_page=per_page
    )
    
    return render_template(
        'entries/partials/trash_list.html',
        entries=entries
    )

# =====================================
# Rutas para acciones (POST, PUT, DELETE)
# =====================================

@entry.route('/', methods=['POST'])
@login_required
def create_entry():
    """
    Procesa la creación de una nueva entrada.
    """
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    collection_id = request.form.get('collection_id')
    tags = request.form.get('tags', '').split(',')
    
    # Convertir collection_id a None si está vacío
    if not collection_id:
        collection_id = None
    else:
        collection_id = int(collection_id)
    
    # Validación básica
    if not title:
        flash('El título es obligatorio.', 'error')
        if is_htmx_request():
            return render_template(
                'entries/partials/edit_form.html',
                entry={'title': title, 'content': content},
                error='El título es obligatorio.'
            )
        return render_template(
            'entries/edit.html',
            entry={'title': title, 'content': content},
            title="Nueva Entrada",
            now=datetime.now()
        )
    
    # Sanitizar contenido HTML para evitar XSS
    content = bleach.clean(content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    
    # Crear entrada
    entry = entry_service.create_entry(
        title=title,
        content=content,
        user_id=current_user.id,
        collection_id=collection_id,
        tags=[tag.strip() for tag in tags if tag.strip()]
    )
    
    # Redireccionar si es una solicitud normal, o devolver JSON/HTML si es HTMX
    if is_htmx_request():
        if request.headers.get('HX-Trigger') == 'save-form':
            return jsonify({
                'success': True,
                'entry_id': entry.id,
                'message': 'Entrada creada correctamente.'
            })
        # Redireccionar a la vista de la entrada mediante HTMX
        response = render_template('entries/partials/redirect.html')
        response = make_response(response)
        response.headers['HX-Redirect'] = url_for('entry.view_entry_partial', entry_id=entry.id)
        return response
    
    flash('Entrada creada correctamente.', 'success')
    return redirect(url_for('entry.view_entry', entry_id=entry.id))

@entry.route('/<int:entry_id>', methods=['POST', 'PUT'])
@login_required
def update_entry(entry_id):
    """
    Procesa la actualización de una entrada.
    """
    entry = entry_service.get_entry_by_id(entry_id)
    
    if not entry or entry.user_id != current_user.id:
        abort(404)
    
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    collection_id = request.form.get('collection_id')
    tags = request.form.get('tags', '').split(',')
    
    # Convertir collection_id a None si está vacío
    if not collection_id:
        collection_id = None
    else:
        collection_id = int(collection_id)
    
    # Validación básica
    if not title:
        flash('El título es obligatorio.', 'error')
        if is_htmx_request():
            return render_template(
                'entries/partials/edit_form.html',
                entry={'id': entry_id, 'title': title, 'content': content},
                error='El título es obligatorio.'
            )
        return render_template(
            'entries/edit.html',
            entry={'id': entry_id, 'title': title, 'content': content},
            title="Editar Entrada",
            now=datetime.now()
        )
    
    # Sanitizar contenido HTML para evitar XSS
    content = bleach.clean(content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    
    # Actualizar entrada
    updated_entry = entry_service.update_entry(
        entry_id=entry_id,
        title=title,
        content=content,
        collection_id=collection_id,
        tags=[tag.strip() for tag in tags if tag.strip()]
    )
    
    # Responder según el tipo de solicitud
    if is_htmx_request():
        if request.headers.get('HX-Trigger') == 'save-form':
            return jsonify({
                'success': True,
                'message': 'Entrada actualizada correctamente.',
                'entry_id': updated_entry.id
            })
        # Redireccionar a la vista de la entrada mediante HTMX
        response = render_template('entries/partials/redirect.html')
        response = make_response(response)
        response.headers['HX-Redirect'] = url_for('entry.view_entry_partial', entry_id=entry_id)
        return response
    
    flash('Entrada actualizada correctamente.', 'success')
    return redirect(url_for('entry.view_entry', entry_id=entry_id))

@entry.route('/<int:entry_id>/autosave', methods=['POST'])
@login_required
def autosave_entry(entry_id):
    """
    Guarda automáticamente una entrada en edición.
    Solo para solicitudes HTMX/AJAX.
    """
    if not is_htmx_request():
        abort(400)  # Bad Request si no es una solicitud HTMX
    
    entry = entry_service.get_entry_by_id(entry_id) if entry_id != 0 else None
    
    # Para nuevas entradas (id=0), crear una nueva
    if entry_id == 0:
        title = request.form.get('title', 'Sin título').strip()
        content = request.form.get('content', '').strip()
        
        # Sanitizar contenido
        content = bleach.clean(content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
        
        # Crear nueva entrada
        entry = entry_service.create_entry(
            title=title,
            content=content,
            user_id=current_user.id
        )
        
        return jsonify({
            'success': True,
            'message': 'Entrada creada y guardada automáticamente.',
            'entry_id': entry.id,
            'is_new': True
        })
    
    # Para entradas existentes, verificar permisos
    if not entry or entry.user_id != current_user.id:
        return jsonify({
            'success': False,
            'message': 'No tienes permiso para editar esta entrada.'
        }), 403
    
    # Obtener datos del formulario
    title = request.form.get('title')
    content = request.form.get('content')
    
    # Actualizar sólo si se proporcionan datos
    if title or content:
        # Sanitizar contenido si existe
        if content:
            content = bleach.clean(content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
        
        # Actualizar entrada
        entry_service.update_entry(
            entry_id=entry_id,
            title=title if title else None,
            content=content if content else None
        )
    
    return jsonify({
        'success': True,
        'message': 'Entrada guardada automáticamente.',
        'last_saved': datetime.now().strftime('%H:%M:%S')
    })

@entry.route('/<int:entry_id>/delete', methods=['POST', 'DELETE'])
@login_required
def delete_entry(entry_id):
    """
    Elimina (borrado lógico) una entrada.
    """
    entry = entry_service.get_entry_by_id(entry_id)
    
    if not entry or entry.user_id != current_user.id:
        abort(404)
    
    entry_service.delete_entry(entry_id)
    
    if is_htmx_request():
        return jsonify({
            'success': True,
            'message': 'Entrada movida a la papelera.'
        })
    
    flash('Entrada movida a la papelera.', 'success')
    return redirect(url_for('entry.list_entries'))

@entry.route('/<int:entry_id>/restore', methods=['POST'])
@login_required
def restore_entry(entry_id):
    """
    Restaura una entrada de la papelera.
    """
    # Verificar que la entrada exista y pertenezca al usuario
    entry = entry_service.get_entry_by_id(entry_id, include_deleted=True)
    
    if not entry or entry.user_id != current_user.id:
        abort(404)
    
    entry_service.restore_entry(entry_id)
    
    if is_htmx_request():
        if 'HX-Target' in request.headers:
            # Si hay un objetivo específico, actualizar solo ese elemento
            return f'<div id="entry-{entry_id}" hx-swap-oob="delete"></div>'
        return jsonify({
            'success': True,
            'message': 'Entrada restaurada correctamente.'
        })
    
    flash('Entrada restaurada correctamente.', 'success')
    return redirect(url_for('entry.trash'))

@entry.route('/quick-create', methods=['POST'])
@login_required
def quick_create():
    """
    Crea rápidamente una entrada con contenido mínimo desde el formulario rápido.
    """
    content = request.form.get('content', '').strip()
    
    if not content:
        if is_htmx_request():
            return jsonify({'error': 'El contenido no puede estar vacío'}), 400
        flash('El contenido no puede estar vacío', 'error')
        return redirect(url_for('entry.list_entries'))
    
    # Sanitizar el contenido
    sanitized_content = bleach.clean(content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    
    # Crear la entrada
    entry = entry_service.create_entry(
        user_id=current_user.id,
        title=content[:50] if len(content) > 50 else content,  # Usar primeros 50 caracteres como título
        content=sanitized_content,
        status=EntryStatus.PUBLISHED
    )
    
    if is_htmx_request():
        # Devolver la vista parcial de la nueva entrada para insertarla en la lista
        return render_template(
            'entries/partials/list_entries.html',
            entries=[entry]
        )
    
    flash('Entrada creada correctamente', 'success')
    return redirect(url_for('entry.view_entry', entry_id=entry.id)) 