document.addEventListener('DOMContentLoaded', function () {
  const optimizeBtn = document.querySelector('#optimize-btn');
  console.log('Estado inicial del botón:', optimizeBtn ? 'Encontrado' : 'No encontrado');

  if (optimizeBtn) {
    optimizeBtn.addEventListener('click', async function () {
      try {
        console.log('Botón de optimización clickeado');
        // Ensure the loading spinner is correctly applied to the button itself
        const buttonTextSpan = this.querySelector('span:not(.loading-spinner)');
        if (buttonTextSpan) {
            buttonTextSpan.textContent = 'Optimizando...';
        }
        this.disabled = true;
        this.classList.add('loading'); // Use 'loading' class as defined in CSS for spinner

        console.log('Iniciando petición de optimización...');
        const response = await fetch('/planner/optimize/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
          },
          body: JSON.stringify({}),
        });

        console.log('Respuesta recibida:', response.status);
        if (!response.ok) {
          throw new Error(`Error HTTP: ${response.status}`);
        }

        const data = await response.json();
        console.log('Datos recibidos:', data);

        if (data.success) {
          if (data.suggestions && data.suggestions.length > 0) {
            await showSuggestions(data.suggestions);
          } else {
            if (data.insufficient_tasks) {
              const currentTasks = data.current_tasks || 0;
              const remainingTasks = 4 - currentTasks;
              alert(`Se necesitan al menos 4 tareas para generar sugerencias óptimas.\nActualmente tienes ${currentTasks} tarea(s).\nAgrega ${remainingTasks} tarea(s) más para poder optimizar tu horario.`);
            } else {
              alert(data.message || 'No se encontraron optimizaciones posibles.');
            }
          }
        } else {
          throw new Error(data.message || 'Error desconocido');
        }
      } catch (error) {
        console.error('Error en optimización:', error);
        alert('Hubo un error al optimizar el horario. Por favor, intenta de nuevo más tarde.');
      } finally {
        if (this) {
            const buttonTextSpan = this.querySelector('span:not(.loading-spinner)');
            if (buttonTextSpan) {
                buttonTextSpan.textContent = '🤖 Optimizar Horario';
            }
            this.disabled = false;
            this.classList.remove('loading'); 
        }
      }
    });

    console.log('Evento click registrado en el botón de optimización');
  }
});

async function showSuggestions(suggestions) {
  console.log('Mostrando sugerencias:', suggestions);

  try {
    const response = await fetch('/planner/suggestions_template/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: JSON.stringify({ suggestions: suggestions }),
    });

    if (!response.ok) {
      throw new Error('No se pudo cargar la plantilla del modal: ' + response.status);
    }

    const modalHtml = await response.text();
    
    // Buscar el contenedor del modal o usar el body como fallback
    const modalContainer = document.getElementById('modal-container') || document.body;
    
    // Limpiar cualquier modal existente
    const existingModal = document.getElementById('suggestions-modal');
    if (existingModal) {
      existingModal.remove();
    }
    
    // Crear el modal
    modalContainer.innerHTML = modalHtml;
    
    console.log('Modal de sugerencias creado');

    // Buscar el modal recién creado
    const modal = document.getElementById('suggestions-modal');
    if (!modal) {
      throw new Error('No se pudo encontrar el modal después de crearlo');
    }

    // Mostrar el modal
    modal.style.display = 'flex';

    const closeModal = () => {
      if (modal && modal.parentNode) {
        modal.style.display = 'none';
        modal.remove();
        console.log('Modal cerrado');
      }
    };

    // Agregar event listeners
    const closeBtn = modal.querySelector('.close-btn');
    const cancelBtn = modal.querySelector('.cancel-btn');
    const applyBtn = modal.querySelector('#apply-selected-btn');

    if (closeBtn) {
      closeBtn.addEventListener('click', closeModal);
    }

    if (cancelBtn) {
      cancelBtn.addEventListener('click', closeModal);
    }

    // Cerrar modal al hacer clic en el fondo
    modal.addEventListener('click', function(e) {
      if (e.target === modal) {
        closeModal();
      }
    });

    if (applyBtn) {
      applyBtn.addEventListener('click', async function (e) {
        e.preventDefault();
        const checkedBoxes = modal.querySelectorAll('input[name="suggestion"]:checked');

        if (checkedBoxes.length === 0) {
          alert('Por favor selecciona al menos un cambio para aplicar.');
          return;
        }

        try {
          console.log('Aplicando cambios seleccionados...');
          this.textContent = 'Aplicando...';
          this.disabled = true;

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
          this.textContent = 'Aplicar Cambios';
          this.disabled = false;
        }
      });
    }

  } catch (error) {
    console.error('Error al mostrar sugerencias:', error);
    alert('Error al cargar el modal de sugerencias: ' + error.message);
  }
}

function getConfidenceLevel(confidence) {
  if (confidence >= 0.8) return ['text-green-500', '🎯 Alta confianza'];
  if (confidence >= 0.6) return ['text-yellow-500', '📊 Confianza media'];
  return ['text-red-500', '💭 Baja confianza'];
}

async function applySuggestionWithTimes(eventId, newTime, newEndTime) {
  console.log(`Actualizando evento ${eventId}:`, { newTime, newEndTime });

  const response = await fetch(`/planner/event/${eventId}/update-ajax/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify({
      start_time: newTime,
      end_time: newEndTime,
    }),
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
      minute: '2-digit',
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