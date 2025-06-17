document.addEventListener('DOMContentLoaded', function() {
    // Función para marcar el enlace activo en el sidebar
    function setActiveNavigation() {
        const currentPath = window.location.pathname;
        const sidebarLinks = document.querySelectorAll('#sidebar a[href]');
        
        sidebarLinks.forEach(link => {
            const linkPath = link.getAttribute('href');
            
            // Remover clases activas de todos los enlaces
            link.classList.remove('text-sidebar-active', 'font-semibold');
            link.classList.add('text-sidebar-muted');
            
            // Verificar si el enlace coincide con la página actual
            if (linkPath === currentPath || 
                (currentPath.includes('/horarios') && linkPath.includes('horarios')) ||
                (currentPath.includes('/tareas') && linkPath.includes('tareas')) ||
                (currentPath === '/' && linkPath.includes('home'))) {
                
                // Agregar clases activas al enlace actual
                link.classList.remove('text-sidebar-muted');
                link.classList.add('text-sidebar-active', 'font-semibold');
            }
        });
    }
    
    // Ejecutar al cargar la página
    setActiveNavigation();
    
    // También ejecutar cuando se navega (para SPAs)
    window.addEventListener('popstate', setActiveNavigation);
});
