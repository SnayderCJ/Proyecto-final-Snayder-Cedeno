document.addEventListener('DOMContentLoaded', function() {
    function updateDateTime() {
        fetch('/get_current_datetime/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Actualizar el saludo y la fecha
                    const greetingElement = document.querySelector('.greeting-text');
                    const dateElement = document.querySelector('.date-text');
                    
                    if (greetingElement) {
                        greetingElement.textContent = data.greeting;
                    }
                    if (dateElement) {
                        dateElement.textContent = data.current_date;
                    }
                }
            })
            .catch(error => console.error('Error actualizando fecha/hora:', error));
    }

    // Actualizar cada minuto
    setInterval(updateDateTime, 60000);
});
