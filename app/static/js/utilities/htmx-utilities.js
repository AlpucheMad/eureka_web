/**
 * Eureka - Utilidades HTMX
 * Funciones y extensiones para mejorar la experiencia con HTMX
 */

document.addEventListener('DOMContentLoaded', function() {
    // Configuración global de HTMX
    configureHtmx();

    // Inicializar manejadores para indicadores de carga
    setupLoadingIndicators();

    // Inicializar manejo de mensajes flash con fade-out
    setupFlashMessages();

    // Validación de formularios mejorada
    setupFormValidation();
});

/**
 * Configura parámetros globales de HTMX
 */
function configureHtmx() {
    // Asegurarse de que las solicitudes incluyan el token CSRF
    document.addEventListener('htmx:configRequest', function(evt) {
        let csrfToken = document.querySelector('meta[name="csrf-token"]');
        if (csrfToken) {
            evt.detail.headers['X-CSRF-Token'] = csrfToken.content;
        }
    });

    // Manejar respuestas JSON para mostrar toast
    document.addEventListener('htmx:afterRequest', function(evt) {
        if (evt.detail.xhr.status === 200) {
            try {
                const response = JSON.parse(evt.detail.xhr.response);
                if (response.message) {
                    showToast(response.message, response.success ? 'success' : 'error');
                }
            } catch (e) {
                // No es una respuesta JSON, ignorar
            }
        }
    });
}

/**
 * Configura indicadores de carga para elementos HTMX
 */
function setupLoadingIndicators() {
    // Añadir estado de carga a botones
    document.addEventListener('htmx:beforeRequest', function(evt) {
        const button = evt.target.tagName === 'BUTTON' ? 
                      evt.target : 
                      evt.target.querySelector('button');
        
        if (button && !button.querySelector('.spinner')) {
            const originalContent = button.innerHTML;
            button.dataset.originalContent = originalContent;
            
            // Crear spinner y añadirlo
            const spinner = document.createElement('span');
            spinner.className = 'spinner';
            spinner.style.marginRight = '0.5rem';
            
            button.innerHTML = '';
            button.appendChild(spinner);
            button.appendChild(document.createTextNode(' Cargando...'));
        }
    });

    // Restaurar estado original después de la solicitud
    document.addEventListener('htmx:afterRequest', function(evt) {
        const button = evt.target.tagName === 'BUTTON' ? 
                      evt.target : 
                      evt.target.querySelector('button');
        
        if (button && button.dataset.originalContent) {
            button.innerHTML = button.dataset.originalContent;
            delete button.dataset.originalContent;
        }
    });
}

/**
 * Configura mensajes flash con animación de desvanecimiento
 */
function setupFlashMessages() {
    const flashMessages = document.querySelectorAll('.alert, .flash-message');
    
    flashMessages.forEach(function(message) {
        // Auto-ocultar después de 5 segundos
        setTimeout(function() {
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.5s ease';
            
            // Eliminar después de la transición
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 5000);
        
        // Añadir botón para cerrar manualmente
        if (!message.querySelector('.close-btn')) {
            const closeBtn = document.createElement('button');
            closeBtn.className = 'close-btn';
            closeBtn.innerHTML = '&times;';
            closeBtn.style.background = 'none';
            closeBtn.style.border = 'none';
            closeBtn.style.float = 'right';
            closeBtn.style.fontSize = '1.25rem';
            closeBtn.style.fontWeight = 'bold';
            closeBtn.style.cursor = 'pointer';
            
            closeBtn.addEventListener('click', function() {
                message.style.opacity = '0';
                setTimeout(function() {
                    message.remove();
                }, 500);
            });
            
            message.insertBefore(closeBtn, message.firstChild);
        }
    });
}

/**
 * Configura validación de formularios
 */
function setupFormValidation() {
    document.addEventListener('htmx:validation:validate', function(evt) {
        const form = evt.detail.elt;
        const isValid = form.checkValidity();
        
        if (!isValid) {
            evt.preventDefault();
            
            // Resaltar campos inválidos
            const invalidFields = form.querySelectorAll(':invalid');
            invalidFields.forEach(function(field) {
                field.classList.add('is-invalid');
                
                // Mostrar mensaje de error si no existe
                const errorSpan = field.nextElementSibling;
                if (!errorSpan || !errorSpan.classList.contains('error-message')) {
                    const span = document.createElement('span');
                    span.className = 'error-message';
                    span.textContent = field.validationMessage;
                    field.parentNode.insertBefore(span, field.nextSibling);
                }
            });
        }
    });
}

/**
 * Muestra un toast con mensaje y tipo
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo de mensaje: 'success', 'error', 'warning', 'info'
 */
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast') || createToastElement();
    const toastMessage = toast.querySelector('.toast-message');
    const toastIcon = toast.querySelector('.toast-icon');
    
    // Configurar mensaje
    toastMessage.textContent = message;
    
    // Configurar clase según tipo
    toast.className = 'toast';
    toast.classList.add(`toast-${type}`);
    
    // Configurar icono según tipo
    let iconHTML = '';
    switch (type) {
        case 'success':
            iconHTML = '<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>';
            break;
        case 'error':
            iconHTML = '<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>';
            break;
        case 'warning':
            iconHTML = '<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>';
            break;
        default:
            iconHTML = '<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>';
    }
    
    toastIcon.innerHTML = iconHTML;
    
    // Mostrar el toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    // Ocultar después de 3 segundos
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

/**
 * Crea el elemento toast si no existe
 * @returns {HTMLElement} Elemento toast
 */
function createToastElement() {
    const toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'toast';
    toast.setAttribute('role', 'alert');
    
    const container = document.createElement('div');
    container.className = 'toast-container';
    
    const icon = document.createElement('div');
    icon.className = 'toast-icon';
    
    const message = document.createElement('div');
    message.className = 'toast-message';
    
    container.appendChild(icon);
    container.appendChild(message);
    toast.appendChild(container);
    
    document.body.appendChild(toast);
    return toast;
} 