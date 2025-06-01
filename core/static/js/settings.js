// static/js/settings.js
document.addEventListener('DOMContentLoaded', function() {
    const timezoneSelect = document.getElementById('timezone-select');
    const form = document.querySelector('form');
    let updateInterval;
    let isUpdating = false;

    // Obtener la URL base correcta
    const getDateTimeUrl = window.location.origin + '/get-datetime/';

    // Función para mostrar indicador de carga
    function showLoadingIndicator(element) {
        if (!element.querySelector('.loading-indicator')) {
            const loader = document.createElement('span');
            loader.className = 'loading-indicator';
            element.appendChild(loader);
        }
    }

    // Función para ocultar indicador de carga
    function hideLoadingIndicator(element) {
        const loader = element.querySelector('.loading-indicator');
        if (loader) {
            loader.remove();
        }
    }

    // Función para actualizar fecha y hora
    function updateDateTime(showAnimation = false) {
        if (isUpdating) return;
        isUpdating = true;

        console.log('Actualizando fecha y hora desde:', getDateTimeUrl);

        fetch(getDateTimeUrl)
            .then(response => {
                console.log('Respuesta recibida:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('Datos recibidos:', data);
                if (data.success) {
                    // Actualizar en navigation bar
                    const greetingElement = document.querySelector('.welcome-title');
                    if (greetingElement) {
                        const currentText = greetingElement.textContent;
                        const parts = currentText.split(', ');
                        if (parts.length > 1) {
                            const userName = parts[1];
                            greetingElement.textContent = `${data.greeting}, ${userName}`;
                        }
                        
                        if (showAnimation) {
                            greetingElement.classList.add('timezone-change-indicator');
                            setTimeout(() => {
                                greetingElement.classList.remove('timezone-change-indicator');
                            }, 1500);
                        }
                    }

                    const dateElement = document.querySelector('.welcome-date');
                    if (dateElement) {
                        dateElement.textContent = data.current_date;
                        
                        if (showAnimation) {
                            dateElement.classList.add('timezone-change-indicator');
                            setTimeout(() => {
                                dateElement.classList.remove('timezone-change-indicator');
                            }, 1500);
                        }
                    }

                    const previewDate = document.getElementById('preview-date');
                    if (previewDate) {
                        previewDate.textContent = data.current_date;
                        if (showAnimation) {
                            previewDate.parentElement.classList.add('timezone-updated');
                            setTimeout(() => {
                                previewDate.parentElement.classList.remove('timezone-updated');
                            }, 1000);
                        }
                    }
                } else {
                    console.error('Error en la respuesta:', data.error);
                }
            })
            .catch(error => {
                console.error('Error actualizando fecha y hora:', error);
            })
            .finally(() => {
                isUpdating = false;
            });
    }

    // Función para enviar cambios de zona horaria via AJAX
    function updateTimezone(timezone) {
        console.log('Actualizando zona horaria a:', timezone);
        
        const previewContainer = document.querySelector('.timezone-preview');
        if (previewContainer) {
            previewContainer.classList.add('timezone-updating');
            showLoadingIndicator(previewContainer);
        }

        const formData = new FormData();
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
        formData.append('language', document.querySelector('[name=language]').value);
        formData.append('timezone', timezone);

        fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            console.log('Zona horaria actualizada, status:', response.status);
            return response.text();
        })
        .then(data => {
            console.log('Respuesta del servidor:', data.substring(0, 100) + '...');
            // Actualizar inmediatamente después del cambio con animación
            setTimeout(() => {
                updateDateTime(true);
                
                if (previewContainer) {
                    previewContainer.classList.remove('timezone-updating');
                    hideLoadingIndicator(previewContainer);
                }
            }, 500);
        })
        .catch(error => {
            console.error('Error actualizando zona horaria:', error);
            if (previewContainer) {
                previewContainer.classList.remove('timezone-updating');
                hideLoadingIndicator(previewContainer);
            }
        });
    }

    // Event listener para cambio de zona horaria
    if (timezoneSelect) {
        timezoneSelect.addEventListener('change', function() {
            const selectedTimezone = this.value;
            console.log('Usuario seleccionó zona horaria:', selectedTimezone);
            updateTimezone(selectedTimezone);
        });
    }

    // Actualizar cada minuto
    updateInterval = setInterval(() => updateDateTime(false), 60000);

    // Limpiar interval cuando se cierre la página
    window.addEventListener('beforeunload', function() {
        if (updateInterval) {
            clearInterval(updateInterval);
        }
    });
});

// Función adicional para actualizar inmediatamente después de guardar configuración
function handleFormSubmit() {
    setTimeout(() => {
        const getDateTimeUrl = window.location.origin + '/get-datetime/';
        
        fetch(getDateTimeUrl)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Actualizar en navigation bar
                    const greetingElement = document.querySelector('.welcome-title');
                    if (greetingElement) {
                        const currentText = greetingElement.textContent;
                        const parts = currentText.split(', ');
                        if (parts.length > 1) {
                            const userName = parts[1];
                            greetingElement.textContent = `${data.greeting}, ${userName}`;
                        }
                    }

                    const dateElement = document.querySelector('.welcome-date');
                    if (dateElement) {
                        dateElement.textContent = data.current_date;
                    }
                }
            })
            .catch(error => {
                console.error('Error actualizando fecha y hora:', error);
            });
    }, 1000);
}