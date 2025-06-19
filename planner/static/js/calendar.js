// Archivo: static/js/calendar.js
document.addEventListener('DOMContentLoaded', function() {
    initializeCalendar();
});

function initializeCalendar() {
    scrollToCurrentTime();
    initializeTooltips();
    setupKeyboardShortcuts();
    setupHoverEffects();
    setupQuickActions();
}

function scrollToCurrentTime() {
    const todayCell = document.querySelector('.day-cell.today');
    if (todayCell) {
        const currentHour = new Date().getHours();
        const timeSlotHeight = 50;
        const scrollPosition = Math.max(0, (currentHour - 2) * timeSlotHeight);
        const wrapper = document.querySelector('.calendar-table-wrapper');
        if (wrapper) {
            wrapper.scrollTo({
                top: scrollPosition,
                behavior: 'smooth'
            });
        }
        highlightCurrentHour();
    }
}

function highlightCurrentHour() {
    const currentHour = new Date().getHours();
    const timeSlots = document.querySelectorAll('.time-slot');
    timeSlots.forEach((slot, index) => {
        const slotHour = parseInt(slot.textContent.split(':')[0]);
        if (slotHour === currentHour) {
            slot.classList.add('current-hour');
        } else {
            slot.classList.remove('current-hour');
        }
    });
}

function initializeTooltips() {
    document.querySelectorAll('.event:not(.event-continuation)').forEach(function(event) {
        const tooltip = event.querySelector('.custom-tooltip');
        if (tooltip) {
            event.addEventListener('mouseenter', function(e) {
                showTooltip(this, tooltip);
            });
            event.addEventListener('mouseleave', function() {
                hideTooltip(tooltip);
            });
            event.addEventListener('mousemove', function(e) {
                positionTooltip(e, tooltip);
            });
        }
    });
}

function showTooltip(element, tooltip) {
    tooltip.style.opacity = '1';
    tooltip.style.visibility = 'visible';
}

function hideTooltip(tooltip) {
    tooltip.style.opacity = '0';
    tooltip.style.visibility = 'hidden';
}

function positionTooltip(e, tooltip) {
    const tooltipRect = tooltip.getBoundingClientRect();
    let tooltipX = e.clientX + 10;
    let tooltipY = e.clientY - tooltipRect.height - 10;

    if (tooltipX + tooltipRect.width > window.innerWidth - 10) {
        tooltipX = window.innerWidth - tooltipRect.width - 10;
    }
    if (tooltipX < 10) {
        tooltipX = 10;
    }
    if (tooltipY < 10) {
        tooltipY = e.clientY + 20;
    }

    tooltip.style.left = `${tooltipX}px`;
    tooltip.style.top = `${tooltipY}px`;
}

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
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
    if (direction !== 'current') {
        const urlDateParam = currentUrl.searchParams.get('date');
        let baseDate = urlDateParam ? new Date(urlDateParam + 'T12:00:00Z') : new Date();
        if (isNaN(baseDate.getTime())) baseDate = new Date();
        let newDate = new Date(baseDate);
        if (direction === 'prev') {
            newDate.setDate(baseDate.getDate() - 7);
        } else if (direction === 'next') {
            newDate.setDate(baseDate.getDate() + 7);
        }
        currentUrl.searchParams.set('date', newDate.toISOString().split('T')[0]);
    } else {
        currentUrl.searchParams.delete('date');
    }
    showLoading();
    window.location.href = currentUrl.toString();
}

function setupHoverEffects() {
    document.querySelectorAll('.day-cell').forEach(cell => {
        cell.addEventListener('mouseenter', function() {
            this.classList.add('day-hover');
        });
        cell.addEventListener('mouseleave', function() {
            this.classList.remove('day-hover');
        });
    });
    document.querySelectorAll('.event:not(.event-continuation)').forEach(event => {
        event.addEventListener('mouseenter', function() {
            this.style.zIndex = '30';
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
            const durationSpan = this.querySelector('.hover-duration');
            if (durationSpan) durationSpan.remove();
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
    const match = timeString.match(/(\d{1,2}):(\d{2})/);
    if (!match) return null;
    return {
        hours: parseInt(match[1]),
        minutes: parseInt(match[2])
    };
}

function setupQuickActions() {
    document.querySelectorAll('.day-cell').forEach(cell => {
        let clickCount = 0;
        cell.addEventListener('click', function(e) {
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
    document.querySelectorAll('.event:not(.event-continuation)').forEach(event => {
        event.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            showContextMenu(this, e);
        });
    });
}

function createQuickEvent(dayCell, clickEvent) {
    const dayIndex = parseInt(dayCell.getAttribute('data-day-index'));
    if (isNaN(dayIndex)) return;
    const row = dayCell.closest('tr');
    const timeSlot = row.querySelector('.time-slot').textContent.split(':')[0];
    const hour = parseInt(timeSlot);
    const urlParams = new URLSearchParams(window.location.search);
    let baseDate = urlParams.get('date') ? new Date(urlParams.get('date') + 'T12:00:00Z') : new Date();
    if (isNaN(baseDate.getTime())) baseDate = new Date();
    const weekStart = getWeekStart(baseDate);
    const targetDate = new Date(weekStart);
    targetDate.setDate(targetDate.getDate() + dayIndex);
    const dateString = targetDate.toISOString().split('T')[0];
    const timeString = `${hour.toString().padStart(2, '0')}:00`;
    window.location.href = `/planner/event/create/?date=${dateString}&time=${timeString}`;
}

function getWeekStart(date) {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1);
    return new Date(d.setDate(diff));
}

function showContextMenu(event, clickEvent) {
    const existingMenu = document.querySelector('.context-menu');
    if (existingMenu) existingMenu.remove();
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
    const isCompleted = event.classList.contains('completed');
    const options = [
        { icon: 'fas fa-eye', text: 'Ver detalles', action: () => window.location.href = `/planner/event/${eventId}/` },
        { icon: 'fas fa-edit', text: 'Editar', action: () => window.location.href = `/planner/event/${eventId}/edit/` },
        { icon: 'fas fa-check', text: isCompleted ? 'Marcar pendiente' : 'Marcar completado', action: () => toggleEventCompletion(eventId) },
        { icon: 'fas fa-trash', text: 'Eliminar', action: () => window.location.href = `/planner/event/${eventId}/delete/`, class: 'danger' }
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
        if (option.class === 'danger') item.style.color = '#ef4444';
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
            document.querySelectorAll(`[data-event-id="${eventId}"]`).forEach(eventElement => {
                // Actualizar clases y estilos
                if (data.is_completed) {
                    eventElement.classList.add('opacity-60', 'line-through', 'bg-opacity-30');
                    // Agregar el ícono de check si no existe
                    if (!eventElement.querySelector('.fa-check-circle')) {
                        const titleDiv = eventElement.querySelector('.font-medium');
                        const checkIcon = document.createElement('i');
                        checkIcon.className = 'fas fa-check-circle text-green-500 text-sm';
                        titleDiv.insertBefore(checkIcon, titleDiv.firstChild);
                    }
                } else {
                    eventElement.classList.remove('opacity-60', 'line-through', 'bg-opacity-30');
                    // Remover el ícono de check si existe
                    const checkIcon = eventElement.querySelector('.fa-check-circle');
                    if (checkIcon) {
                        checkIcon.remove();
                    }
                }
            });
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
    setTimeout(() => overlay.style.opacity = '1', 10);
}

function hideLoading() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.style.opacity = '0';
        setTimeout(() => overlay.remove(), 300);
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
            ">×</button>
        </div>
    `;
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
        notification.style.opacity = '1';
    }, 100);
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

function addCalendarStyles() {
    if (document.querySelector('#calendar-dynamic-styles')) return;
    const style = document.createElement('style');
    style.id = 'calendar-dynamic-styles';
    style.textContent = `
        .time-slot.current-hour {
            background-color: rgba(124, 58, 237, 0.2) !important;
            border-left: 3px solid #7c3aed;
            color: #7c3aed;
            font-weight: 600;
        }
        .day-cell.day-hover {
            background: rgba(124, 58, 237, 0.05);
        }
        .event:not(.event-continuation) {
            transition: all 0.2s ease-in-out;
            will-change: transform, filter, z-index;
        }
        .event:not(.event-continuation):hover {
            filter: brightness(1.1) saturate(1.1) drop-shadow(0 0 8px rgba(124, 58, 237, 0.4));
            transform: translateY(-2px);
        }
        .context-menu {
            animation: contextMenuAppear 0.2s ease-out;
        }
        @keyframes contextMenuAppear {
            from { opacity: 0; transform: scale(0.9) translateY(-10px); }
            to { opacity: 1; transform: scale(1) translateY(0); }
        }
        .notification {
            animation: notificationSlide 0.3s ease-out;
        }
        @keyframes notificationSlide {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
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

addCalendarStyles();

window.calendarUtils = {
    toggleEventCompletion,
    navigateWeek,
    showNotification,
    showLoading,
    hideLoading,
    optimizeSchedule
};