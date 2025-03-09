/**
 * Eureka - JavaScript principal
 * Funcionalidades de la aplicación
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar iconos
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    // Manejo del tema oscuro/claro
    setupTheme();
    
    // Inicializar sidebar móvil
    setupSidebar();
    
    // Configurar animaciones HTMX
    setupHtmxAnimations();
    
    // Crear overlay para sidebar móvil si no existe
    createSidebarOverlay();
});

/**
 * Configuración del tema claro/oscuro
 */
function setupTheme() {
    // Detectar preferencia del sistema
    const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const savedTheme = localStorage.getItem('theme');
    
    // Aplicar tema según preferencia guardada o sistema
    if (savedTheme) {
        document.body.className = `theme-${savedTheme}`;
    } else if (prefersDarkMode) {
        document.body.className = 'theme-dark';
        localStorage.setItem('theme', 'dark');
    } else {
        document.body.className = 'theme-light';
        localStorage.setItem('theme', 'light');
    }
    
    // Buscar botón de cambio de tema en el menú de usuario (se implementará luego)
    document.addEventListener('click', function(e) {
        if (e.target.closest('#theme-toggle')) {
            toggleTheme();
        }
    });
}

/**
 * Alternar entre tema claro y oscuro
 */
function toggleTheme() {
    const isDark = document.body.classList.contains('theme-dark');
    
    if (isDark) {
        document.body.className = 'theme-light';
        localStorage.setItem('theme', 'light');
    } else {
        document.body.className = 'theme-dark';
        localStorage.setItem('theme', 'dark');
    }
    
    // Recargar iconos para aplicar los cambios de color
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
}

/**
 * Crear overlay para sidebar móvil
 */
function createSidebarOverlay() {
    // Verificar si ya existe
    if (!document.querySelector('.sidebar-overlay')) {
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        document.body.appendChild(overlay);
        
        // Cerrar sidebar al hacer clic en overlay
        overlay.addEventListener('click', function() {
            const sidebar = document.getElementById('sidebar');
            if (sidebar) {
                sidebar.classList.remove('show');
            }
        });
    }
}

/**
 * Configuración del sidebar
 */
function setupSidebar() {
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const appContent = document.querySelector('.app-content');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                // Comportamiento móvil: mostrar/ocultar
                sidebar.classList.toggle('show');
            } else {
                // Comportamiento desktop: colapsar/expandir
                sidebar.classList.toggle('sidebar-collapsed');
                
                // Ajustar el contenido principal
                if (appContent) {
                    appContent.style.marginLeft = sidebar.classList.contains('sidebar-collapsed') 
                        ? 'var(--sidebar-collapsed-width)' 
                        : 'var(--sidebar-width)';
                }
                
                // Guardar preferencia de estado del sidebar
                const isCollapsed = sidebar.classList.contains('sidebar-collapsed');
                localStorage.setItem('sidebar-collapsed', isCollapsed ? 'true' : 'false');
            }
        });
        
        // Aplicar estado guardado del sidebar (solo en desktop)
        if (window.innerWidth > 768) {
            const sidebarCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
            if (sidebarCollapsed) {
                sidebar.classList.add('sidebar-collapsed');
                if (appContent) {
                    appContent.style.marginLeft = 'var(--sidebar-collapsed-width)';
                }
            }
        }
    }
    
    // Cerrar sidebar al hacer clic en enlace (sólo móvil)
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768 && e.target.closest('.sidebar-nav-link') && sidebar) {
            sidebar.classList.remove('show');
        }
    });
    
    // Ajustar sidebar en cambio de tamaño de ventana
    window.addEventListener('resize', function() {
        if (sidebar) {
            if (window.innerWidth <= 768) {
                // En móvil, quitar collapsed y ajustar margen
                sidebar.classList.remove('sidebar-collapsed');
                if (appContent) {
                    appContent.style.marginLeft = '0';
                }
            } else {
                // En desktop, restaurar estado guardado
                const sidebarCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
                if (sidebarCollapsed) {
                    sidebar.classList.add('sidebar-collapsed');
                    if (appContent) {
                        appContent.style.marginLeft = 'var(--sidebar-collapsed-width)';
                    }
                } else {
                    if (appContent) {
                        appContent.style.marginLeft = 'var(--sidebar-width)';
                    }
                }
                
                // Quitar clase show si estaba visible en móvil
                sidebar.classList.remove('show');
            }
        }
    });
}

/**
 * Configurar animaciones para interacciones HTMX
 */
function setupHtmxAnimations() {
    // Reemplazar iconos después de cada carga HTMX
    document.addEventListener('htmx:afterSwap', function() {
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    });
    
    // Mostrar notificaciones toast
    document.addEventListener('htmx:responseError', function(evt) {
        showToast('Ocurrió un error. Por favor intenta nuevamente.', 'error');
    });
    
    // Manejar transiciones de página
    document.body.addEventListener('htmx:beforeSwap', function(evt) {
        const target = evt.detail.target;
        if (target.id === 'main-content') {
            target.classList.add('htmx-swapping');
        }
    });
    
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        const target = evt.detail.target;
        if (target.id === 'main-content') {
            setTimeout(() => {
                target.classList.remove('htmx-swapping');
            }, 50);
        }
    });
}

/**
 * Mostrar un mensaje toast
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo de mensaje: 'success', 'error', 'info', 'warning'
 */
function showToast(message, type = 'info') {
    // Crear elemento toast si no existe
    let toast = document.getElementById('toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        toast.className = 'toast';
        document.body.appendChild(toast);
    }
    
    // Establecer mensaje y clase según tipo
    let iconHtml = '';
    switch (type) {
        case 'success':
            iconHtml = '<i data-feather="check-circle"></i>';
            break;
        case 'error':
            iconHtml = '<i data-feather="alert-circle"></i>';
            break;
        case 'warning':
            iconHtml = '<i data-feather="alert-triangle"></i>';
            break;
        default:
            iconHtml = '<i data-feather="info"></i>';
    }
    
    toast.innerHTML = `
        <div class="toast-content">
            <div class="toast-icon">${iconHtml}</div>
            <div class="toast-message">${message}</div>
        </div>
    `;
    
    // Mostrar toast
    setTimeout(() => {
        toast.classList.add('show');
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }, 100);
    
    // Ocultar después de 3 segundos
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
} 