document.addEventListener("DOMContentLoaded", function () {
    const toasts = document.querySelectorAll(".custom-toast");

    toasts.forEach(toast => {
        let isManuallyClose = false;
        let autoCloseTimer;
        
        // Función para cerrar el toast
        const closeToast = () => {
            if (toast && toast.parentNode) {
                toast.style.opacity = "0";
                toast.style.transition = "opacity 0.5s ease";
                setTimeout(() => {
                    if (toast.parentNode) {
                        toast.remove();
                    }
                }, 500);
            }
        };

        // Auto-cerrar después de 5 segundos
        autoCloseTimer = setTimeout(() => {
            if (!isManuallyClose) {
                closeToast();
            }
        }, 5000);

        // Manejar el botón de cerrar manualmente
        const closeButton = toast.querySelector('.close-toast');
        if (closeButton) {
            closeButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                isManuallyClose = true;
                clearTimeout(autoCloseTimer);
                closeToast();
            });
        }

        // Pausar auto-close al hacer hover
        toast.addEventListener('mouseenter', () => {
            clearTimeout(autoCloseTimer);
        });

        // Reanudar al quitar el hover (solo si no se cerró manualmente)
        toast.addEventListener('mouseleave', () => {
            if (!isManuallyClose) {
                autoCloseTimer = setTimeout(() => {
                    if (!isManuallyClose) {
                        closeToast();
                    }
                }, 2000);
            }
        });
    });
});