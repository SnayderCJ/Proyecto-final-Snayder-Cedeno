document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard JS cargado');
    
    // Event delegation para las tarjetas de tareas
    document.addEventListener('click', function(e) {
        const taskCard = e.target.closest('.task-card[data-task-id]');
        if (taskCard) {
            const taskId = taskCard.dataset.taskId;
            console.log('Haciendo toggle en tarea:', taskId);
            toggleTaskCompletion(taskId);
        }
    });

    // Función para cambiar el estado de completado de una tarea
    function toggleTaskCompletion(taskId) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        if (!csrfToken) {
            console.error('No se encontró el token CSRF');
            return;
        }
        
        fetch(`/planner/event/${taskId}/toggle-completion/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Respuesta del servidor:', data);
            if (data.success) {
                // Recargar la página para mostrar los cambios
                window.location.reload();
            } else {
                console.error('Error en la respuesta:', data.error);
            }
        })
        .catch(error => {
            console.error('Error en la petición:', error);
        });
    }

    // Funcionalidad de pestañas
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Remover clase active de todas las pestañas y contenidos
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Agregar clase active a la pestaña clickeada
            this.classList.add('active');
            
            // Mostrar el contenido correspondiente
            const targetContent = document.getElementById(targetTab + 'Tab');
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
});
