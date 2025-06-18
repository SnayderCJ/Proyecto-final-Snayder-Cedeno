document.addEventListener('DOMContentLoaded', function() {
    const greetingElement = document.querySelector('.greeting-text');
    const dateElement = document.querySelector('.date-text');

    function updateDateTime() {
        fetch('/get-datetime/')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    if (greetingElement) {
                        greetingElement.textContent = data.greeting;
                    }
                    if (dateElement) {
                        dateElement.textContent = data.current_date;
                        // Efecto sutil de actualización
                        dateElement.classList.add('opacity-50');
                        setTimeout(() => dateElement.classList.remove('opacity-50'), 200);
                    }
                } else if (data.error) {
                    console.warn('Error del servidor:', data.error);
                }
            })
            .catch(error => {
                console.error('Error actualizando fecha/hora:', error);
                // Reintentamos en 30 segundos si hay un error
                setTimeout(updateDateTime, 30000);
            });
    }

    // Ejecutar inmediatamente al cargar
    updateDateTime();

    // Actualizar cada minuto
    setInterval(updateDateTime, 60000);

    // Actualizar cuando la pestaña vuelve a estar activa
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible') {
            updateDateTime();
        }
    });
});
