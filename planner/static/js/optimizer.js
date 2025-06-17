document.addEventListener('DOMContentLoaded', function() {
    // Inicializar el botón de optimización
    const optimizeBtn = document.querySelector('.optimize-btn');
    console.log('Estado inicial del botón:', optimizeBtn ? 'Encontrado' : 'No encontrado');

    if (optimizeBtn) {
        optimizeBtn.addEventListener('click', async function() {
            try {
                console.log('Botón de optimización clickeado');
                
                // Cambiar estado del botón
                this.textContent = 'Optimizando...';
                this.disabled = true;
                this.classList.add('loading');
                
                console.log('Iniciando petición de optimización...');
                
                // Hacer petición al servidor
                const response = await fetch('/planner/optimize/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({})
                });

                console.log('Respuesta recibida:', response.status);

                if (!response.ok) {
                    throw new Error(`Error HTTP: ${response.status}`);
                }

                const data = await response.json();
                console.log('Datos recibidos:', data);

                if (data.success) {
                    if (data.suggestions && data.suggestions.length > 0) {
                        showSuggestions(data.suggestions);
                    } else {
                        alert(data.message || 'No se encontraron optimizaciones posibles.');
                    }
                } else {
                    throw new Error(data.message || 'Error desconocido');
                }
            } catch (error) {
                console.error('Error en optimización:', error);
                alert('Hubo un error al optimizar el horario. Por favor, intenta de nuevo más tarde.');
            } finally {
                // Restaurar estado del botón
                if (this) {
                    this.textContent = '🤖 Optimizar Horario';
                    this.disabled = false;
                    this.classList.remove('loading');
                }
            }
        });

        console.log('Evento click registrado en el botón de optimización');
    }
});

function getConfidenceLevel(confidence) {
    if (confidence >= 0.8) return ['high', '🎯 Alta confianza'];
    if (confidence >= 0.6) return ['medium', '📊 Confianza media'];
    return ['low', '💭 Baja confianza'];
}

function showSuggestions(suggestions) {
    console.log('Mostrando sugerencias:', suggestions);
    
    const modal = document.createElement('div');
    modal.className = 'suggestions-modal';
    modal.innerHTML = `
        <div class="suggestions-content">
            <div class="suggestions-header">
                <h3>✨ Sugerencias de IA</h3>
                <button class="close-btn">&times;</button>
            </div>
            <div class="suggestions-body">
                <form id="suggestions-form">
                    ${suggestions.map((suggestion, index) => {
                        const [confidenceClass, confidenceText] = getConfidenceLevel(suggestion.confianza);
                        return `
                            <div class="suggestion-item">
                                <input type="checkbox" id="suggestion-${index}" name="suggestion" value="${suggestion.event_id}" checked>
                                <label for="suggestion-${index}">
                                    <strong>${suggestion.title}</strong>
                                    
                                    <div class="ai-confidence ai-confidence-${confidenceClass}">
                                        ${confidenceText} (${(suggestion.confianza * 100).toFixed(1)}%)
                                    </div>
                                    
                                    <div class="suggestion-details">
                                        <div class="detail-item">
                                            <i class="fas fa-clock"></i>
                                            Cambio: ${formatTime(suggestion.current_time)} → ${formatTime(suggestion.suggested_time)}
                                        </div>
                                        <div class="detail-item">
                                            <i class="fas fa-chart-line"></i>
                                            Mejora esperada: ${suggestion.improvement_score}%
                                        </div>
                                        <div class="detail-item">
                                            <i class="fas fa-lightbulb"></i>
                                            ${suggestion.reason}
                                        </div>
                                    </div>

                                    <div class="hours-chart">
                                        <div class="hours-chart-title">Análisis de horarios disponibles:</div>
                                        ${suggestion.todas_opciones.map(opcion => {
                                            const scorePercentage = (opcion.score * 100).toFixed(1);
                                            const isBest = opcion.hora === suggestion.mejor_hora;
                                            return `
                                                <div class="hour-bar ${isBest ? 'best-hour' : ''}">
                                                    <span class="hour-label">${opcion.hora_formateada}</span>
                                                    <div class="hour-score-bar">
                                                        <div class="hour-score-fill" style="width: ${scorePercentage}%"></div>
                                                    </div>
                                                    <span class="hour-score">${scorePercentage}%</span>
                                                </div>
                                            `;
                                        }).join('')}
                                    </div>
                                </label>
                            </div>
                        `;
                    }).join('')}
                </form>
            </div>
            <div class="suggestions-footer">
                <button id="apply-selected-btn" class="apply-btn">Aplicar Cambios</button>
                <button class="cancel-btn">Cancelar</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    console.log('Modal de sugerencias creado');

    // Manejar cierre del modal
    const closeModal = () => {
        document.body.removeChild(modal);
        console.log('Modal cerrado');
    };

    modal.querySelector('.close-btn').addEventListener('click', closeModal);
    modal.querySelector('.cancel-btn').addEventListener('click', closeModal);

    // Manejar aplicación de cambios
    modal.querySelector('#apply-selected-btn').addEventListener('click', async function(e) {
        e.preventDefault();
        const checkedBoxes = modal.querySelectorAll('input[name="suggestion"]:checked');
        
        if (checkedBoxes.length === 0) {
            alert('Por favor selecciona al menos un cambio para aplicar.');
            return;
        }

        try {
            console.log('Aplicando cambios seleccionados...');
            this.disabled = true;
            this.textContent = 'Aplicando...';

            for (const box of checkedBoxes) {
                const eventId = box.value;
                const suggestion = suggestions.find(s => s.event_id == eventId);
                
                if (suggestion) {
                    console.log(`Aplicando cambio para evento ${eventId}`);
                    await applySuggestionWithTimes(eventId, suggestion.suggested_time, suggestion.suggested_end_time);
                }
            }

            alert('Cambios aplicados exitosamente. La página se recargará para mostrar los cambios.');
            closeModal();
            location.reload();
        } catch (error) {
            console.error('Error al aplicar cambios:', error);
            alert('Hubo un error al aplicar los cambios. Por favor, intenta de nuevo.');
            this.disabled = false;
            this.textContent = 'Aplicar Cambios';
        }
    });
}

async function applySuggestionWithTimes(eventId, newTime, newEndTime) {
    console.log(`Actualizando evento ${eventId}:`, { newTime, newEndTime });
    
    const response = await fetch(`/planner/event/${eventId}/update-ajax/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            start_time: newTime,
            end_time: newEndTime
        })
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Respuesta de actualización:', data);
    
    if (!data.success) {
        throw new Error(data.error || 'Error desconocido');
    }

    return data;
}

function formatTime(isoString) {
    try {
        const date = new Date(isoString);
        return date.toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        console.error('Error al formatear tiempo:', error);
        return isoString;
    }
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
