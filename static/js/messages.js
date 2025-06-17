document.addEventListener('DOMContentLoaded', function() {
    // Auto-cerrar mensajes después de 5 segundos
    const toasts = document.querySelectorAll('.custom-toast');
    
    toasts.forEach(function(toast, index) {
        // Agregar funcionalidad al botón de cerrar
        const closeBtn = toast.querySelector('.close-toast');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                closeToast(toast);
            });
        }
        
        // Auto-cerrar después de 5 segundos (excepto errores que duran más)
        const isError = toast.classList.contains('error');
        const delay = isError ? 8000 : 5000;
        
        setTimeout(function() {
            closeToast(toast);
        }, delay);
    });
    
    function closeToast(toast) {
        toast.classList.add('toast-exit');
        setTimeout(function() {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }
    
    // Función para crear nuevos toasts dinámicamente
    window.showToast = function(message, type = 'info') {
        const container = document.querySelector('.toast-container');
        if (!container) {
            // Crear contenedor si no existe
            const newContainer = document.createElement('div');
            newContainer.className = 'toast-container';
            newContainer.setAttribute('aria-live', 'polite');
            newContainer.setAttribute('aria-label', 'Notificaciones');
            document.body.appendChild(newContainer);
        }
        
        const toast = document.createElement('div');
        toast.className = `custom-toast ${type}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-message">${message}</span>
            </div>
            <button class="close-toast" type="button" aria-label="Cerrar notificación" title="Cerrar">
                ×
            </button>
        `;
        
        const finalContainer = document.querySelector('.toast-container');
        finalContainer.appendChild(toast);
        
        // Agregar event listener al botón de cerrar
        const closeBtn = toast.querySelector('.close-toast');
        closeBtn.addEventListener('click', function() {
            closeToast(toast);
        });
        
        // Auto-cerrar
        const isError = type === 'error';
        const delay = isError ? 8000 : 5000;
        
        setTimeout(function() {
            closeToast(toast);
        }, delay);
    };
});
