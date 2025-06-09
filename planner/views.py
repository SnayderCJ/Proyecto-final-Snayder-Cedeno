# PLANIFICADOR_IA/planner/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Event
from .forms import EventForm
from django.http import JsonResponse
import json

@login_required
def calendar_view(request):
    """
    Vista del calendario que muestra los eventos del usuario en una vista semanal.
    """
    # Obtener la fecha de referencia desde los parámetros GET
    date_param = request.GET.get('date')
    direction = request.GET.get('direction', 'current')
    
    # Determinar la fecha base
    if date_param:
        try:
            base_date = datetime.strptime(date_param, '%Y-%m-%d').date()
        except ValueError:
            base_date = datetime.now().date()
    else:
        base_date = datetime.now().date()
    
    # Aplicar la dirección de navegación
    if direction == 'prev':
        base_date = base_date - timedelta(weeks=1)
    elif direction == 'next':
        base_date = base_date + timedelta(weeks=1)
    # 'current' mantiene la fecha actual
    
    today = datetime.now().date()

    # Calcular el inicio y fin de la semana
    start_of_week = base_date - timedelta(days=base_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Nombres de los días de la semana en español
    day_names_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    # Generar los días de la semana para el encabezado del calendario
    week_days_data = []
    for i in range(7):
        current_day = start_of_week + timedelta(days=i)
        is_today = (current_day == today)
        week_days_data.append({
            'date': current_day,
            'day_num': current_day.day,
            'day_name_short': day_names_es[current_day.weekday()][:3],
            'is_today': is_today,
        })

    # Filtrar eventos para la semana actual del usuario
    user_events = Event.objects.filter(
        user=request.user,
        start_time__date__gte=start_of_week,
        end_time__date__lte=end_of_week + timedelta(days=1)
    ).order_by('start_time')

    # Configuración del calendario
    CALENDAR_START_HOUR = 0
    CALENDAR_END_HOUR = 23
    PIXELS_PER_HOUR = 50

    events_for_template = []
    for event in user_events:
        start_hour_float = event.start_time.hour + event.start_time.minute / 60.0
        top_px = (start_hour_float - CALENDAR_START_HOUR) * PIXELS_PER_HOUR

        # Calcular la altura del evento
        duration_minutes = (event.end_time - event.start_time).total_seconds() / 60.0
        height_px = (duration_minutes / 60.0) * PIXELS_PER_HOUR

        # Clase CSS para el tipo de evento
        css_class_type = f"event-{event.event_type}" 

        events_for_template.append({
            'id': event.pk,
            'title': event.title,
            'description': event.description,
            'start_time': event.start_time,
            'end_time': event.end_time,
            'event_type': event.event_type,
            'is_completed': event.is_completed,
            'priority': event.priority,
            'due_date': event.due_date,
            'day_of_week': event.start_time.weekday(),
            'style': f"top: {top_px}px; height: {height_px}px;",
            'css_class': css_class_type,
        })
    
    # Agrupar eventos por día de la semana
    events_by_day = {i: [] for i in range(7)} 
    for event_data in events_for_template:
        events_by_day[event_data['day_of_week']].append(event_data)

    context = {
        'today': today,
        'start_of_week': start_of_week,
        'end_of_week': end_of_week,
        'week_days_data': week_days_data,
        'events_by_day': events_by_day,
        'time_slots': [f"{h:02d}:00" for h in range(CALENDAR_START_HOUR, CALENDAR_END_HOUR + 1)],
        'current_month_name': start_of_week.strftime("%B"),
        'current_week_range': f"{start_of_week.day:02d}-{end_of_week.day:02d} {start_of_week.strftime('%B')} {start_of_week.year}",
    }
    return render(request, 'horarios.html', context)

# --- VISTA PARA CREAR UN NUEVO EVENTO ---
@login_required
def event_create(request):
    """
    Vista para crear un nuevo evento.
    """
    if request.method == 'POST':
        # Pasar el usuario al formulario para las validaciones
        form = EventForm(request.POST, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            messages.success(request, f'✅ Evento "{event.title}" creado exitosamente.')
            return redirect('planner:horarios')
        else:
            messages.error(request, '❌ Hubo errores en el formulario. Por favor revisa los datos.')
    else:
        # Pre-llenar fecha y hora actual
        initial_data = {
            'start_time': datetime.now().strftime('%Y-%m-%dT%H:%M'),
            'end_time': (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'),
        }
        # También pasar el usuario al formulario vacío
        form = EventForm(initial=initial_data, user=request.user)
    
    return render(request, 'pages/horarios/event_form.html', {'form': form, 'form_type': 'Crear'})

# --- VISTA PARA EDITAR UN EVENTO EXISTENTE ---
@login_required
def event_edit(request, pk):
    """
    Vista para editar un evento existente.
    """
    event = get_object_or_404(Event, pk=pk, user=request.user)
    if request.method == 'POST':
        # Pasar el usuario y la instancia al formulario
        form = EventForm(request.POST, instance=event, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Evento "{event.title}" actualizado exitosamente.')
            return redirect('planner:event_detail', pk=event.pk)
        else:
            messages.error(request, '❌ Hubo errores en el formulario. Por favor revisa los datos.')
    else:
        # También pasar el usuario al formulario de edición
        form = EventForm(instance=event, user=request.user)
    
    return render(request, 'pages/horarios/event_form.html', {
        'form': form, 
        'form_type': 'Editar', 
        'event': event
    })

# --- VISTA PARA ELIMINAR UN EVENTO ---
@login_required
def event_delete(request, pk):
    """
    Vista para eliminar un evento.
    """
    event = get_object_or_404(Event, pk=pk, user=request.user)
    event_title = event.title  # Guardar el título antes de eliminar
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, f'🗑️ Evento "{event_title}" eliminado exitosamente.')
        return redirect('planner:horarios')
    
    return render(request, 'pages/horarios/event_confirm_delete.html', {'event': event})

# --- VISTA PARA VER DETALLES DE UN EVENTO ---
@login_required
def event_detail(request, pk):
    """
    Vista para ver los detalles de un evento.
    """
    event = get_object_or_404(Event, pk=pk, user=request.user)
    return render(request, 'pages/horarios/event_detail.html', {'event': event})

@login_required
def toggle_event_completion(request, pk):
    """
    Vista AJAX para cambiar el estado de completado de un evento.
    """
    if request.method == 'POST':
        try:
            event = get_object_or_404(Event, pk=pk, user=request.user)
            event.is_completed = not event.is_completed
            event.save()
            
            return JsonResponse({
                'success': True,
                'is_completed': event.is_completed,
                'message': 'Completado' if event.is_completed else 'Pendiente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

# Tareas 

@login_required
def tareas_view(request):
    # Obtener la fecha actual
    today = datetime.now().date()
    
    # Calcular el inicio y fin de la semana (lunes a domingo)
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Filtrar eventos para la semana actual del usuario
    user_events = Event.objects.filter(
        user=request.user,
        start_time__date__gte=start_of_week,
        start_time__date__lte=end_of_week
    ).order_by('start_time')

    # Nombres de los días en español
    day_names_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    # Inicializar diccionario para eventos por día
    events_by_day = {i: [] for i in range(7)}
    
    # Agrupar eventos por día de la semana
    for event in user_events:
        day_of_week = event.start_time.weekday()
        events_by_day[day_of_week].append({
            'id': event.pk,
            'title': event.title,
            'description': event.description,
            'start_time': event.start_time,
            'end_time': event.end_time,
            'event_type': event.event_type,
            'is_completed': event.is_completed,
            'priority': event.priority,
            'due_date': event.due_date,
            'css_class': f"event-{event.event_type}",
        })

    # Crear datos para cada día de la semana
    week_days_data = []
    for i in range(7):
        current_day_date = start_of_week + timedelta(days=i)
        week_days_data.append({
            'day_name': day_names_es[i],
            'day_name_short': day_names_es[i][:3],  # Para versión corta (Lun, Mar, etc.)
            'day_num': current_day_date.day,
            'date': current_day_date,
            'is_today': current_day_date == today,
            'events': events_by_day[i],  # Eventos para este día
            'event_count': len(events_by_day[i]),  # Contador de eventos
        })

    # Estadísticas útiles
    total_events = sum(len(events) for events in events_by_day.values())
    completed_events = sum(1 for events in events_by_day.values() for event in events if event.get('is_completed', False))
    pending_events = total_events - completed_events

    context = {
        'week_days_data': week_days_data,
        'events_by_day': events_by_day,
        'seven_days_range': range(7),
        'start_of_week': start_of_week,
        'end_of_week': end_of_week,
        'today': today,
        'current_week_range': f"{start_of_week.day:02d}-{end_of_week.day:02d} {start_of_week.strftime('%B')} {start_of_week.year}",
        # Estadísticas
        'total_events': total_events,
        'completed_events': completed_events,
        'pending_events': pending_events,
    }
    
    return render(request, 'tareas.html', context)