document.addEventListener('DOMContentLoaded', function() {
    // Configuración
    const AUTO_DISMISS_DELAY = 5000; // 5 segundos

    // Inicializar los toasts existentes
    initializeToasts();

    function initializeToasts() {
        const toasts = document.querySelectorAll('.custom-toast');
        toasts.forEach(toast => {
            setupToast(toast);
        });
    }

    function setupToast(toast) {
        // Configurar el botón de cerrar
        const closeBtn = toast.querySelector('.close-toast');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => removeToast(toast));
        }

        // Auto-cerrar después del delay
        setTimeout(() => removeToast(toast), AUTO_DISMISS_DELAY);
    }

    function removeToast(toast) {
        if (!toast.classList.contains('toast-removing')) {
            toast.classList.add('toast-removing');
            toast.addEventListener('animationend', () => {
                toast.remove();
            });
        }
    }
});
