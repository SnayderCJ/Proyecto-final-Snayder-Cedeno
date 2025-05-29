# PLANIFICADOR_IA/planner/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, timedelta, time
import calendar # Para obtener nombres de días de la semana

# Importa los modelos y formularios necesarios
from .models import Event
from .forms import EventForm # 


# --- VISTA PRINCIPAL DEL CALENDARIO --

# --- VISTA PRINCIPAL DEL CALENDARIO ---
def calendar_view(request):
    """
    Vista del calendario que muestra los eventos del usuario en una vista semanal.
    """
    # Obtener la fecha actual (o la fecha de referencia si quieres navegar por semanas)
    today = datetime.now().date() # Solo la fecha, sin la hora

    # Calcular el inicio y fin de la semana actual
    # Asumiendo Lunes como el primer día de la semana (weekday() = 0 para Lunes)
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Nombres de los días de la semana en español (para el encabezado del calendario)
    day_names_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    # Generar los días de la semana para el encabezado del calendario
    week_days_data = []
    for i in range(7):
        current_day = start_of_week + timedelta(days=i)
        is_today = (current_day == today)
        week_days_data.append({
            'date': current_day,
            'day_num': current_day.day,
            'day_name_short': day_names_es[current_day.weekday()][:3], # Ej. "Lun"
            'is_today': is_today,
        })

    # Filtrar eventos para la semana actual del usuario
    user_events = Event.objects.filter(
        user=request.user,
        start_time__date__gte=start_of_week,
        # Considerar eventos que terminan en la semana o se extienden
        end_time__date__lte=end_of_week + timedelta(days=1) # +1 día para incluir eventos que terminan al final del domingo
    ).order_by('start_time')

    # --- CAMBIOS AQUÍ PARA LAS 24 HORAS ---
    CALENDAR_START_HOUR = 0  # Comienza a las 00:00 (medianoche)
    CALENDAR_END_HOUR = 23   # Termina a las 23:00 (la última franja es 23:00-00:00 del día siguiente)
    PIXELS_PER_HOUR = 60 # Altura de cada hora en píxeles (basado en tu CSS)

    events_for_template = []
    for event in user_events:
        start_hour_float = event.start_time.hour + event.start_time.minute / 60.0

        # El `top_px` ahora se calcula desde el inicio absoluto del calendario (00:00)
        # Asumiendo que `top: 0` de la columna de día (después del header) es el inicio de las 00:00.
        # Y que la cabecera del día tiene un offset de `PIXELS_PER_HOUR` (60px)
        # Esto significa que 00:00am se mostraría en top:60px, 01:00am en top:120px etc.
        top_px = (start_hour_float - CALENDAR_START_HOUR) * PIXELS_PER_HOUR + PIXELS_PER_HOUR 

        # Calcular la altura del evento
        duration_minutes = (event.end_time - event.start_time).total_seconds() / 60.0
        height_px = (duration_minutes / 60.0) * PIXELS_PER_HOUR

        # Clase CSS para el tipo de evento (para colores/estilos)
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
            'day_of_week': event.start_time.weekday(), # Lunes=0, Domingo=6
            'style': f"top: {top_px}px; height: {height_px}px;",
            'css_class': css_class_type,
        })
    
    # Agrupar eventos por día de la semana para facilitar la renderización en el template
    events_by_day = {i: [] for i in range(7)} 
    for event_data in events_for_template:
        events_by_day[event_data['day_of_week']].append(event_data)

    context = {
        'today': today,
        'start_of_week': start_of_week,
        'end_of_week': end_of_week,
        'week_days_data': week_days_data,
        'events_by_day': events_by_day, # Diccionario de eventos agrupados por día
        'time_slots': [f"{h:02d}:00" for h in range(CALENDAR_START_HOUR, CALENDAR_END_HOUR + 1)], # De 00:00 a 23:00
        'current_month_name': today.strftime("%B"), # Nombre del mes actual
        'current_week_range': f"{start_of_week.day:02d}-{end_of_week.day:02d} {start_of_week.strftime('%B')} {start_of_week.year}"
    }
    return render(request, 'horarios.html', context) 

# --- VISTA PARA CREAR UN NUEVO EVENTO ---
def event_create(request):
    """
    Vista para crear un nuevo evento.
    """
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            messages.success(request, 'Evento creado exitosamente.')
            return redirect('planner:horarios') # Redirige al calendario
        else:
            messages.error(request, 'Hubo un error al crear el evento. Por favor, revisa los datos.')
    else:
        # Pre-llenar fecha y hora actual para facilitar la creación
        initial_data = {
            'start_time': datetime.now().strftime('%Y-%m-%dT%H:%M'),
            'end_time': (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'),
        }
        form = EventForm(initial=initial_data)
    return render(request, 'event_form.html', {'form': form, 'form_type': 'Crear'})

# --- VISTA PARA EDITAR UN EVENTO EXISTENTE ---

def event_edit(request, pk):
    """
    Vista para editar un evento existente.
    """
    event = get_object_or_404(Event, pk=pk, user=request.user) # Asegura que solo el dueño edite
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento actualizado exitosamente.')
            return redirect('planner:horarios')
        else:
            messages.error(request, 'Hubo un error al actualizar el evento. Por favor, revisa los datos.')
    else:
        # Carga los datos existentes del evento en el formulario
        form = EventForm(instance=event)
    return render(request, 'event_form.html', {'form': form, 'form_type': 'Editar'})

# --- VISTA PARA ELIMINAR UN EVENTO ---
def event_delete(request, pk):
    """
    Vista para eliminar un evento.
    """
    event = get_object_or_404(Event, pk=pk, user=request.user)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Evento eliminado exitosamente.')
        return redirect('planner:horarios')
    return render(request, 'event_confirm_delete.html', {'event': event})

# --- VISTA PARA VER DETALLES DE UN EVENTO ---
def event_detail(request, pk):
    """
    Vista para ver los detalles de un evento.
    """
    event = get_object_or_404(Event, pk=pk, user=request.user)
    return render(request, 'event_detail.html', {'event': event})