document.addEventListener('DOMContentLoaded', function() {
    const optimizeBtn = document.querySelector('.optimize-btn');
    
    if (optimizeBtn) {
        optimizeBtn.addEventListener('click', function() {
            // Cambiar texto del botón mientras procesa
            const originalText = this.textContent;
            this.textContent = 'Optimizando...';
            this.disabled = true;
            
            // Hacer petición AJAX al endpoint de optimización
            fetch('/planner/optimize-schedule/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.suggestions && data.suggestions.length > 0) {
                    showSuggestions(data.suggestions);
                } else {
                    alert('No se encontraron sugerencias de optimización. Necesitas más tareas para entrenar la IA (mínimo 5 tareas).');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Hubo un error al optimizar el horario. Asegúrate de tener tareas creadas.');
            })
            .finally(() => {
                // Restaurar botón
                this.textContent = originalText;
                this.disabled = false;
            });
        });
    }
});

function showSuggestions(suggestions) {
    // Crear modal para mostrar sugerencias con checkboxes y botón aplicar
    const modal = document.createElement('div');
    modal.className = 'suggestions-modal';
    modal.innerHTML = `
        <div class="suggestions-content">
            <div class="suggestions-header">
                <h3>✅ Cambios sugeridos:</h3>
                <button class="close-btn">&times;</button>
            </div>
            <div class="suggestions-body">
                <form id="suggestions-form">
                    ${suggestions.map((suggestion, index) => `
                        <div class="suggestion-item">
                            <input type="checkbox" id="suggestion-${index}" name="suggestion" value="${suggestion.event_id}" checked>
                            <label for="suggestion-${index}">${suggestion.reason}</label>
                        </div>
                    `).join('')}
                </form>
            </div>
            <div class="suggestions-footer">
                <button id="apply-selected-btn" class="apply-btn">Aplicar</button>
                <button class="cancel-btn">Cancelar</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Event listeners para cerrar modal
    modal.querySelector('.close-btn').addEventListener('click', () => {
        document.body.removeChild(modal);
    });

    modal.querySelector('.cancel-btn').addEventListener('click', () => {
        document.body.removeChild(modal);
    });

    // Event listener para aplicar cambios seleccionados
    modal.querySelector('#apply-selected-btn').addEventListener('click', (e) => {
        e.preventDefault();
        const checkedBoxes = modal.querySelectorAll('input[name="suggestion"]:checked');
        if (checkedBoxes.length === 0) {
            alert('Por favor selecciona al menos un cambio para aplicar.');
            return;
        }
        // Aplicar cambios uno por uno
        checkedBoxes.forEach(box => {
            const eventId = box.value;
            const suggestion = suggestions.find(s => s.event_id == eventId);
            if (suggestion) {
                applySuggestionWithTimes(eventId, suggestion.suggested_time, suggestion.suggested_end_time);
            }
        });
        alert('Cambios aplicados. La página se recargará para mostrar los cambios.');
        document.body.removeChild(modal);
        location.reload();
    });
}

// Nueva función para aplicar sugerencia con tiempos específicos
function applySuggestionWithTimes(eventId, newTime, newEndTime) {
    fetch(`/planner/event/${eventId}/update-ajax/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            start_time: newTime,
            end_time: newEndTime
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (!data.success) {
            console.error('Error en la respuesta:', data);
            alert('Error al actualizar la tarea: ' + (data.error || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al actualizar la tarea. Por favor, intenta de nuevo.');
    });
}


function applySuggestion(eventId) {
    const btn = document.querySelector(`[data-event-id="${eventId}"]`);
    const newTime = btn.getAttribute('data-new-time');
    const newEndTime = btn.getAttribute('data-new-end-time');

    console.log('Actualizando evento:', {
        eventId,
        newTime,
        newEndTime
    });

    fetch(`/planner/event/${eventId}/update-ajax/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            start_time: newTime,
            end_time: newEndTime
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            btn.textContent = 'Aplicado ✓';
            btn.disabled = true;
            
            // Recargar la página después de un breve delay
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            console.error('Error en la respuesta:', data);
            alert('Error al actualizar la tarea: ' + (data.error || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al actualizar la tarea. Por favor, intenta de nuevo.');
        btn.disabled = false;
    });
}

function formatDateTime(dateTimeString) {
    const date = new Date(dateTimeString);
    return date.toLocaleString('es-ES', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}