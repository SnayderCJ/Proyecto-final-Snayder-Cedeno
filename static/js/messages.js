document.addEventListener('DOMContentLoaded', function() {
    // Auto-cerrar mensajes después de 5 segundos
    const messages = document.querySelectorAll('.animate-slide-in-right');
    
    messages.forEach(function(message, index) {
        // Agregar funcionalidad al botón de cerrar
        const closeBtn = message.querySelector('button[onclick*="remove"]');
        if (closeBtn) {
            closeBtn.addEventListener('click', function(e) {
                e.preventDefault();
                closeMessage(message);
            });
        }
        
        // Auto-cerrar después de 5 segundos (excepto errores que duran más)
        const isError = message.querySelector('.text-red-500');
        const delay = isError ? 8000 : 5000;
        
        setTimeout(function() {
            closeMessage(message);
        }, delay);
    });
    
    function closeMessage(message) {
        message.style.animation = 'slideOutRight 0.3s ease-in forwards';
        setTimeout(function() {
            if (message.parentNode) {
                message.remove();
            }
        }, 300);
    }
    
    // Función para crear nuevos mensajes dinámicamente
    window.showMessage = function(text, type = 'info') {
        const container = document.querySelector('.fixed.top-4.right-4') || createMessageContainer();
        
        const messageElement = createMessageElement(text, type);
        container.appendChild(messageElement);
        
        // Auto-cerrar
        const isError = type === 'error';
        const delay = isError ? 8000 : 5000;
        
        setTimeout(function() {
            closeMessage(messageElement);
        }, delay);
        
        return messageElement;
    };
    
    function createMessageContainer() {
        const container = document.createElement('div');
        container.className = 'fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-md w-full pointer-events-none';
        document.body.appendChild(container);
        return container;
    }
    
    function createMessageElement(text, type) {
        const message = document.createElement('div');
        message.className = 'animate-slide-in-right pointer-events-auto bg-card border border-border rounded-lg shadow-lg overflow-hidden';
        
        let iconSvg, borderClass, iconColor;
        
        switch(type) {
            case 'success':
                borderClass = 'border-l-4 border-l-green-500';
                iconColor = 'text-green-500';
                iconSvg = `<svg class="w-5 h-5 text-green-500" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>`;
                break;
            case 'error':
                borderClass = 'border-l-4 border-l-red-500';
                iconColor = 'text-red-500';
                iconSvg = `<svg class="w-5 h-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                </svg>`;
                break;
            case 'warning':
                borderClass = 'border-l-4 border-l-yellow-500';
                iconColor = 'text-yellow-500';
                iconSvg = `<svg class="w-5 h-5 text-yellow-500" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                </svg>`;
                break;
            default:
                borderClass = 'border-l-4 border-l-blue-500';
                iconColor = 'text-blue-500';
                iconSvg = `<svg class="w-5 h-5 text-blue-500" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
                </svg>`;
        }
        
        message.innerHTML = `
            <div class="flex items-center p-4 ${borderClass}">
                <div class="flex-shrink-0 mr-3">
                    ${iconSvg}
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-foreground">${text}</p>
                </div>
                <div class="ml-4 flex-shrink-0 flex">
                    <button type="button" class="inline-flex text-muted-foreground hover:text-foreground focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-ring rounded-md" onclick="closeMessage(this.closest('.animate-slide-in-right'))">
                        <span class="sr-only">Cerrar</span>
                        <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                        </svg>
                    </button>
                </div>
            </div>
            <div class="relative h-0.5 bg-muted">
                <div class="absolute inset-0 bg-gradient-to-r ${type === 'success' ? 'from-green-500 to-green-600' : type === 'error' ? 'from-red-500 to-red-600' : type === 'warning' ? 'from-yellow-500 to-yellow-600' : 'from-blue-500 to-blue-600'} animate-shrink origin-left"></div>
            </div>
        `;
        
        return message;
    }
    
    // Agregar estilos CSS si no existen
    if (!document.querySelector('#message-styles')) {
        const style = document.createElement('style');
        style.id = 'message-styles';
        style.textContent = `
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }

            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }

            @keyframes shrink {
                from {
                    transform: scaleX(1);
                }
                to {
                    transform: scaleX(0);
                }
            }

            .animate-slide-in-right {
                animation: slideInRight 0.3s ease-out;
            }

            .animate-shrink {
                animation: shrink 5s linear forwards;
            }
        `;
        document.head.appendChild(style);
    }
});

// Hacer la función closeMessage global
window.closeMessage = function(message) {
    message.style.animation = 'slideOutRight 0.3s ease-in forwards';
    setTimeout(function() {
        if (message.parentNode) {
            message.remove();
        }
    }, 300);
};
