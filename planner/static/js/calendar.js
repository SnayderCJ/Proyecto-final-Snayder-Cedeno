// Archivo: static/js/calendar.js
// JavaScript para mejorar la funcionalidad del calendario

document.addEventListener('DOMContentLoaded', function() {
    initializeCalendar();
});

function initializeCalendar() {
    // Auto-scroll al día actual y hora actual
    scrollToCurrentTime();

    // Inicializar tooltips mejorados
    initializeTooltips();

    // Configurar atajos de teclado
    setupKeyboardShortcuts();

    // Agregar efectos de hover mejorados
    setupHoverEffects();

    // Configurar quick actions
    setupQuickActions();
}

function scrollToCurrentTime() {
    const todayColumn = document.querySelector('.day-column.today');
    if (todayColumn) {
        const currentHour = new Date().getHours();
        // Obtener la altura real de un time-slot
        const timeSlotElement = document.querySelector('.time-slot');
        const timeSlotHeight = timeSlotElement ? timeSlotElement.offsetHeight : 50; // Fallback a 50px

        // Usamos timeSlotHeight por hora. El '-2' es para mostrar un par de horas antes de la actual.
        const scrollPosition = Math.max(0, (currentHour - 2) * timeSlotHeight);
        const wrapper = document.querySelector('.calendar-grid-wrapper');

        // Scroll suave
        if (wrapper) { // Asegurarse de que el wrapper existe antes de intentar scroll
            wrapper.scrollTo({
                top: scrollPosition,
                behavior: 'smooth'
            });
        }

        // Resaltar la hora actual
        highlightCurrentHour();
    }
}

function highlightCurrentHour() {
    const currentHour = new Date().getHours();
    const timeSlots = document.querySelectorAll('.time-slot');

    timeSlots.forEach((slot, index) => {
        // La hora del time-slot debería coincidir con el índice (0-23)
        // Asumiendo que el primer time-slot es para la hora 0
        const slotHour = parseInt(slot.dataset.hour || index); // Si tienes un data-attribute para la hora

        if (slotHour === currentHour) {
            slot.classList.add('current-hour');
        } else {
            slot.classList.remove('current-hour');
        }
    });
}

function initializeTooltips() {
    document.querySelectorAll('.event').forEach(function(event) {
        // Crear tooltip personalizado
        const tooltip = event.querySelector('.custom-tooltip');
        if (tooltip) {
            event.addEventListener('mouseenter', function(e) {
                showTooltip(this, tooltip);
            });

            event.addEventListener('mouseleave', function(e) {
                hideTooltip(tooltip);
            });

            // Posicionar tooltip correctamente
            event.addEventListener('mousemove', function(e) {
                positionTooltip(e, tooltip);
            });
        }
    });
}

function showTooltip(element, tooltip) {
    tooltip.style.opacity = '1';
    tooltip.style.visibility = 'visible';
    tooltip.style.transform = 'translateX(-50%) translateY(-10px)';
}

function hideTooltip(tooltip) {
    tooltip.style.opacity = '0';
    tooltip.style.visibility = 'hidden';
    tooltip.style.transform = 'translateX(-50%) translateY(0)';
}

function positionTooltip(e, tooltip) {
    const rect = e.target.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();

    // Calcular la posición X del tooltip
    let tooltipX = e.clientX;

    // Ajustar si se sale por la derecha
    if (tooltipX + tooltipRect.width > window.innerWidth - 10) { // Margen de 10px
        tooltipX = window.innerWidth - tooltipRect.width - 10;
    }
    // Ajustar si se sale por la izquierda
    if (tooltipX < 10) { // Margen de 10px
        tooltipX = 10;
    }

    // Calcular la posición Y del tooltip
    let tooltipY = e.clientY - tooltipRect.height - 10; // 10px por encima del cursor

    // Ajustar si se sale por arriba
    if (tooltipY < 10) { // Margen de 10px
        tooltipY = e.clientY + 20; // 20px por debajo del cursor
    }

    tooltip.style.left = `${tooltipX}px`;
    tooltip.style.top = `${tooltipY}px`;
    tooltip.style.transform = 'none'; // Desactivar transform para control manual
}

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Solo procesar si no estamos en un input
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }

        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 'n':
                    e.preventDefault();
                    window.location.href = "/planner/event/create/";
                    break;
                case 'h':
                    e.preventDefault();
                    window.location.href = "/planner/horarios/";
                    break;
            }
        }

        // Navegación con flechas
        switch(e.key) {
            case 'ArrowLeft':
                if (e.shiftKey) {
                    e.preventDefault();
                    navigateWeek('prev');
                }
                break;
            case 'ArrowRight':
                if (e.shiftKey) {
                    e.preventDefault();
                    navigateWeek('next');
                }
                break;
            case 'Home':
                e.preventDefault();
                navigateWeek('current');
                break;
        }
    });
}

function navigateWeek(direction) {
    const currentUrl = new URL(window.location);
    currentUrl.searchParams.set('direction', direction);

    // La dirección 'current' generalmente no necesita una fecha explícita
    // porque el backend calculará la semana actual.
    // Para 'prev' y 'next', la fecha base es importante.
    if (direction !== 'current') {
        // Obtener la fecha actual de la URL o usar la fecha de hoy
        const urlDateParam = currentUrl.searchParams.get('date');
        let baseDate;

        if (urlDateParam) {
            baseDate = new Date(urlDateParam + 'T12:00:00'); // Añadir hora para evitar problemas de zona horaria
        } else {
            baseDate = new Date();
        }

        let newDate = new Date(baseDate);

        if (direction === 'prev') {
            newDate.setDate(baseDate.getDate() - 7);
        } else if (direction === 'next') {
            newDate.setDate(baseDate.getDate() + 7);
        }
        currentUrl.searchParams.set('date', newDate.toISOString().split('T')[0]);
    } else {
        // Eliminar el parámetro 'date' para que el backend recalcule "hoy"
        currentUrl.searchParams.delete('date');
    }

    // Agregar efecto de carga
    showLoading();
    window.location.href = currentUrl.toString();
}

function setupHoverEffects() {
    // Efecto de hover en días
    document.querySelectorAll('.day-column').forEach(column => {
        column.addEventListener('mouseenter', function() {
            this.classList.add('day-hover');
        });

        column.addEventListener('mouseleave', function() {
            this.classList.remove('day-hover');
        });
    });

    // Efecto de hover en eventos
    document.querySelectorAll('.event').forEach(event => {
        event.addEventListener('mouseenter', function() {
            this.style.zIndex = '30';

            // Agregar info adicional al hover
            const duration = calculateEventDuration(this);
            if (duration && !this.querySelector('.hover-duration')) {
                const durationSpan = document.createElement('span');
                durationSpan.className = 'hover-duration';
                durationSpan.textContent = duration;
                durationSpan.style.cssText = `
                    position: absolute;
                    bottom: 2px;
                    right: 4px;
                    font-size: 8px;
                    background: rgba(0,0,0,0.5);
                    padding: 1px 3px;
                    border-radius: 2px;
                    color: white;
                `;
                this.appendChild(durationSpan);
            }
        });

        event.addEventListener('mouseleave', function() {
            this.style.zIndex = '10';

            // Remover info adicional
            const durationSpan = this.querySelector('.hover-duration');
            if (durationSpan) {
                durationSpan.remove();
            }
        });
    });
}

function calculateEventDuration(eventElement) {
    const timeText = eventElement.querySelector('.event-time')?.textContent;
    if (!timeText) return null;

    const times = timeText.split(' - ');
    if (times.length !== 2) return null;

    const start = parseTime(times[0]);
    const end = parseTime(times[1]);

    if (!start || !end) return null;

    const diffMinutes = (end.hours - start.hours) * 60 + (end.minutes - start.minutes);

    if (diffMinutes >= 60) {
        const hours = Math.floor(diffMinutes / 60);
        const minutes = diffMinutes % 60;
        return `${hours}h${minutes > 0 ? ` ${minutes}m` : ''}`;
    } else {
        return `${diffMinutes}m`;
    }
}

function parseTime(timeString) {
    // Maneja formatos de 12 horas con AM/PM (si es el caso) o 24 horas
    let date = new Date(`2000/01/01 ${timeString}`); // Fecha ficticia para parsear la hora
    if (isNaN(date.getTime())) { // Si falla el parseo directo, intentar con 24h
        const match = timeString.match(/(\d{1,2}):(\d{2})/);
        if (!match) return null;
        return {
            hours: parseInt(match[1]),
            minutes: parseInt(match[2])
        };
    }
    return {
        hours: date.getHours(),
        minutes: date.getMinutes()
    };
}

function setupQuickActions() {
    // Quick action: Doble clic en un día vacío para crear evento
    document.querySelectorAll('.day-column').forEach(column => {
        let clickCount = 0;
        column.addEventListener('click', function(e) {
            // Solo si no se hizo clic en un evento
            if (e.target.closest('.event')) return;

            clickCount++;
            setTimeout(() => {
                if (clickCount === 2) {
                    createQuickEvent(this, e);
                }
                clickCount = 0;
            }, 300);
        });
    });

    // Quick action: Clic derecho para menú contextual
    document.querySelectorAll('.event').forEach(event => {
        event.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            showContextMenu(this, e);
        });
    });
}

function createQuickEvent(dayColumn, clickEvent) {
    const dayIndex = Array.from(dayColumn.parentNode.children).indexOf(dayColumn) - 1; // -1 por la columna de tiempo

    if (dayIndex < 0) return;

    const rect = dayColumn.getBoundingClientRect();

    // Obtener la altura real de un slot de tiempo.
    const timeSlotElement = document.querySelector('.time-slot');
    const timeSlotHeight = timeSlotElement ? timeSlotElement.offsetHeight : 50; // Fallback a 50px

    // Obtener la posición Y del primer time-slot dentro de la columna de día
    // Esto es crucial para un offset preciso.
    let yOffset = 0;
    const firstTimeSlotInColumn = dayColumn.querySelector('.time-slot');
    if (firstTimeSlotInColumn) {
        yOffset = firstTimeSlotInColumn.getBoundingClientRect().top - rect.top;
    } else {
        // Fallback si no se encuentran time-slots en la columna (ej. si la cuadrícula no está completamente renderizada).
        // Si el header del calendario tiene una altura diferente a 50px, ajusta esto.
        const calendarHeader = document.querySelector('.calendar-header');
        yOffset = calendarHeader ? calendarHeader.offsetHeight : 50;
    }


    // Calcula la posición Y del clic dentro del área de la cuadrícula de eventos, restando el offset del encabezado
    // Este cálculo es clave para la alineación vertical.
    const y = clickEvent.clientY - rect.top - yOffset;

    // Calcula la hora basada en la posición Y y la altura del slot de tiempo
    const hour = Math.max(0, Math.min(23, Math.floor(y / timeSlotHeight)));

    // Crear URL para nuevo evento con fecha y hora pre-llenadas
    const today = new Date();
    const weekStart = getWeekStart(today);
    const targetDate = new Date(weekStart);
    targetDate.setDate(targetDate.getDate() + dayIndex);

    const dateString = targetDate.toISOString().split('T')[0];
    const timeString = `${hour.toString().padStart(2, '0')}:00`;

    window.location.href = `/planner/event/create/?date=${dateString}&time=${timeString}`;
}

function getWeekStart(date) {
    const d = new Date(date);
    const day = d.getDay(); // 0 = Domingo, 1 = Lunes, etc.
    // Ajustar para que la semana empiece el Lunes
    // Si es domingo (0), queremos ir 6 días atrás para llegar al lunes anterior.
    // Si es lunes (1), queremos ir 0 días atrás.
    // Si es otro día (2-6), queremos ir (día - 1) días atrás.
    const diff = d.getDate() - day + (day === 0 ? -6 : 1); // Lunes como primer día de la semana (1)
    return new Date(d.setDate(diff));
}

function showContextMenu(event, clickEvent) {
    // Remover menú existente
    const existingMenu = document.querySelector('.context-menu');
    if (existingMenu) existingMenu.remove();

    // Crear menú contextual
    const menu = document.createElement('div');
    menu.className = 'context-menu';
    menu.style.cssText = `
        position: fixed;
        top: ${clickEvent.clientY}px;
        left: ${clickEvent.clientX}px;
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        z-index: 1000;
        min-width: 150px;
        padding: 8px 0;
    `;

    const eventId = event.getAttribute('data-event-id');

    // Opciones del menú
    const options = [
        {
            icon: 'fas fa-eye',
            text: 'Ver detalles',
            action: () => window.location.href = `/planner/event/${eventId}/`
        },
        {
            icon: 'fas fa-edit',
            text: 'Editar',
            action: () => window.location.href = `/planner/event/${eventId}/edit/`
        },
        {
            icon: 'fas fa-check',
            text: 'Marcar completado',
            action: () => toggleEventCompletion(eventId)
        },
        {
            icon: 'fas fa-trash',
            text: 'Eliminar',
            action: () => window.location.href = `/planner/event/${eventId}/delete/`,
            class: 'danger'
        }
    ];

    options.forEach(option => {
        const item = document.createElement('div');
        item.className = `context-menu-item ${option.class || ''}`;
        item.style.cssText = `
            padding: 12px 16px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 12px;
            color: #e2e8f0;
            font-size: 14px;
            transition: background-color 0.2s ease;
        `;

        if (option.class === 'danger') {
            item.style.color = '#ef4444';
        }

        item.innerHTML = `<i class="${option.icon}"></i> ${option.text}`;

        item.addEventListener('mouseenter', function() {
            this.style.backgroundColor = option.class === 'danger' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(124, 58, 237, 0.1)';
        });

        item.addEventListener('mouseleave', function() {
            this.style.backgroundColor = 'transparent';
        });

        item.addEventListener('click', function() {
            menu.remove();
            option.action();
        });

        menu.appendChild(item);
    });

    document.body.appendChild(menu);

    // Cerrar menú al hacer clic fuera
    setTimeout(() => {
        document.addEventListener('click', function closeMenu(e) {
            if (!menu.contains(e.target)) {
                menu.remove();
                document.removeEventListener('click', closeMenu);
            }
        });
    }, 100);
}

function toggleEventCompletion(eventId) {
    showLoading('Actualizando evento...');

    fetch(`/planner/event/${eventId}/toggle-completion/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            // Actualizar visualmente el evento
            const eventElement = document.querySelector(`[data-event-id="${eventId}"]`);
            if (eventElement) {
                if (data.is_completed) {
                    eventElement.classList.add('completed');
                } else {
                    eventElement.classList.remove('completed');
                }
            }

            // Mostrar notificación
            showNotification(data.message, 'success');
        } else {
            showNotification('Error al actualizar el evento', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showNotification('Error al actualizar el evento', 'error');
    });
}

function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

function showLoading(message = 'Cargando...') {
    const existing = document.querySelector('.loading-overlay');
    if (existing) existing.remove();

    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        backdrop-filter: blur(4px);
        transition: opacity 0.3s ease;
        opacity: 0;
    `;

    overlay.innerHTML = `
        <div style="
            background: #1e293b;
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            color: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        ">
            <div style="
                width: 40px;
                height: 40px;
                border: 3px solid #334155;
                border-top: 3px solid #7c3aed;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 1rem;
            "></div>
            <p style="margin: 0; font-size: 14px;">${message}</p>
        </div>
    `;

    // Agregar animación CSS
    if (!document.querySelector('#loading-styles')) {
        const style = document.createElement('style');
        style.id = 'loading-styles';
        style.textContent = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }

    document.body.appendChild(overlay);
    setTimeout(() => overlay.style.opacity = '1', 10); // Fade in
}

function hideLoading() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.style.opacity = '0';
        setTimeout(() => overlay.remove(), 300); // Fade out then remove
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;

    const colors = {
        success: { bg: '#10b981', border: '#059669' },
        error: { bg: '#ef4444', border: '#dc2626' },
        info: { bg: '#3b82f6', border: '#2563eb' },
        warning: { bg: '#f59e0b', border: '#d97706' }
    };

    const color = colors[type] || colors.info;

    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${color.bg};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        border-left: 4px solid ${color.border};
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10001;
        max-width: 300px;
        font-size: 14px;
        transform: translateX(100%);
        transition: transform 0.3s ease, opacity 0.3s ease;
        opacity: 0;
    `;

    const iconClass = type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle';

    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 8px;">
            <i class="fas fa-${iconClass}"></i>
            <span>${message}</span>
            <button onclick="this.closest('.notification').remove()" style="
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                padding: 0;
                margin-left: auto;
                font-size: 16px;
            ">&times;</button>
        </div>
    `;

    document.body.appendChild(notification);

    // Animación de entrada
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
        notification.style.opacity = '1';
    }, 100);

    // Auto-remove después de 5 segundos
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.transform = 'translateX(100%)';
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

function optimizeSchedule() {
    showNotification('🚀 ¡Función de optimización con IA próximamente en el Módulo 3!', 'info');
}

// Funciones de utilidad (no se modificaron, son auxiliares)
function formatTime(date) {
    return date.toTimeString().slice(0, 5);
}

function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Agregar estilos CSS adicionales (ya no es necesario si ya se carga en un CSS aparte)
function addCalendarStyles() {
    if (document.querySelector('#calendar-dynamic-styles')) return;

    const style = document.createElement('style');
    style.id = 'calendar-dynamic-styles';
    style.textContent = `
        /* Estilo para la hora actual */
        .time-slot.current-hour {
            background-color: rgba(124, 58, 237, 0.2) !important;
            border-left: 3px solid #7c3aed;
            color: #7c3aed;
            font-weight: 600;
        }

        /* Efecto hover en columnas de día */
        .day-column.day-hover::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(124, 58, 237, 0.05);
            pointer-events: none;
            z-index: 1;
        }

        /* Mejoras en eventos */
        .event {
            transition: all 0.2s ease-in-out; /* Animación más suave */
            will-change: transform, filter, z-index;
        }

        .event:hover {
            filter: brightness(1.1) saturate(1.1) drop-shadow(0 0 8px rgba(124, 58, 237, 0.4)); /* Sombra para resaltado */
            transform: translateY(-2px); /* Pequeño levantamiento */
        }

        /* Context menu */
        .context-menu {
            animation: contextMenuAppear 0.2s ease-out;
        }

        @keyframes contextMenuAppear {
            from {
                opacity: 0;
                transform: scale(0.9) translateY(-10px);
            }
            to {
                opacity: 1;
                transform: scale(1) translateY(0);
            }
        }

        /* Notificaciones */
        .notification {
            animation: notificationSlide 0.3s ease-out;
        }

        @keyframes notificationSlide {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        /* Responsive mejoras */
        @media (max-width: 768px) {
            .context-menu {
                left: 50% !important;
                transform: translateX(-50%);
                max-width: calc(100vw - 40px);
            }

            .notification {
                right: 10px;
                left: 10px;
                max-width: none;
            }
        }
    `;

    document.head.appendChild(style);
}

// Inicializar estilos cuando se carga el script
addCalendarStyles();

// Exportar funciones para uso global
window.calendarUtils = {
    toggleEventCompletion,
    navigateWeek,
    showNotification,
    showLoading,
    hideLoading,
    optimizeSchedule
};