document.addEventListener('DOMContentLoaded', function() {
    // Obtener la URL actual
    const currentPath = window.location.pathname;
    
    // Obtener todos los enlaces del sidebar
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    
    // Función para activar el enlace correcto
    function setActiveLink() {
        sidebarLinks.forEach(link => {
            // Obtener la URL del enlace
            const linkPath = link.getAttribute('href');
            
            // Si la URL actual coincide con la URL del enlace
            if (currentPath === linkPath) {
                link.classList.add('active');
                // Guardar el estado activo en localStorage
                localStorage.setItem('activeLink', linkPath);
            }
        });
    }
    
    // Restaurar el estado activo si estamos en modo de enfoque
    if (currentPath.includes('focused_time')) {
        const previousActive = localStorage.getItem('activeLink');
        if (previousActive) {
            sidebarLinks.forEach(link => {
                if (link.getAttribute('href') === previousActive) {
                    link.classList.add('active');
                }
            });
        }
    } else {
        setActiveLink();
    }
    
    // Agregar efectos de hover
    sidebarLinks.forEach(link => {
        // Efecto al pasar el mouse
        link.addEventListener('mouseenter', function() {
            if (!this.classList.contains('active')) {
                this.style.transform = 'translateX(5px)';
            }
        });
        
        // Restaurar posición al quitar el mouse
        link.addEventListener('mouseleave', function() {
            if (!this.classList.contains('active')) {
                this.style.transform = 'translateX(0)';
            }
        });
        
        // Efecto al hacer clic
        link.addEventListener('click', function() {
            // Añadir efecto de ripple
            const ripple = document.createElement('div');
            ripple.classList.add('ripple');
            this.appendChild(ripple);
            
            // Remover el efecto después de la animación
            setTimeout(() => {
                ripple.remove();
            }, 1000);
        });
    });
});
