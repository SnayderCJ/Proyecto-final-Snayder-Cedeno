from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Event
from .forms import EventForm
from .ml_optimizer import TaskOptimizer
from django.http import JsonResponse
from django.views.decorators.http import require_GET
import json
import calendar

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
            base_date = timezone.now().date()
    else:
        base_date = timezone.now().date()

    # Convertir base_date a datetime aware
    local_tz = timezone.get_current_timezone()
    base_date = timezone.make_aware(datetime.combine(base_date, datetime.min.time()), local_tz)

    # Aplicar la dirección de navegación
    if direction == 'prev':
        base_date = base_date - timedelta(weeks=1)
    elif direction == 'next':
        base_date = base_date + timedelta(weeks=1)

    today = timezone.now().date()

    # Calcular el inicio y fin de la semana (lunes a domingo)
    start_of_week = base_date - timedelta(days=base_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Convertir a datetime aware para el filtro
    start_of_week_dt = timezone.make_aware(datetime.combine(start_of_week, datetime.min.time()), local_tz)
    end_of_week_dt = timezone.make_aware(datetime.combine(end_of_week, datetime.max.time()), local_tz)

    # Nombres de los días de la semana en español
    day_names_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    # Generar los días de la semana para el encabezado del calendario
    week_days_data = []
    for i in range(7):
        current_day = start_of_week + timedelta(days=i)
        is_today = (current_day.date() == today)
        week_days_data.append({
            'date': current_day.date(),
            'day_num': current_day.day,
            'day_name_short': day_names_es[current_day.weekday()][:3],
            'is_today': is_today,
        })

    # Filtrar eventos para la semana actual del usuario
    user_events = Event.objects.filter(
        user=request.user,
        start_time__gte=start_of_week_dt,
        start_time__lte=end_of_week_dt
    ).order_by('start_time')

    # Configuración del calendario
    CALENDAR_START_HOUR = 0
    CALENDAR_END_HOUR = 23

    # Agrupar eventos por día y hora, incluyendo todas las horas que abarca cada evento
    events_by_day = {i: {f"{h:02d}:00": [] for h in range(CALENDAR_START_HOUR, CALENDAR_END_HOUR + 1)} for i in range(7)}
    for event in user_events:
        start_time_local = event.start_time.astimezone(local_tz)
        end_time_local = event.end_time.astimezone(local_tz)
        weekday = start_time_local.weekday()
        css_class_type = f"event-{event.event_type}"
        
        # Calcular todas las franjas horarias que cubre el evento
        current_time = start_time_local.replace(minute=0, second=0, microsecond=0)
        end_time_ceiled = end_time_local.replace(minute=0, second=0, microsecond=0)
        if end_time_local > end_time_ceiled:
            end_time_ceiled += timedelta(hours=1)
        
        is_first_slot = True
        while current_time < end_time_ceiled and current_time.date() == start_time_local.date():
            hour_slot = current_time.strftime("%H:00")
            events_by_day[weekday][hour_slot].append({
                'id': event.pk,
                'title': event.title,
                'description': event.description,
                'start_time': start_time_local,
                'end_time': end_time_local,
                'event_type': event.event_type,
                'is_completed': event.is_completed,
                'priority': event.priority,
                'due_date': event.due_date,
                'css_class': css_class_type,
                'is_continuation': not is_first_slot,
            })
            current_time += timedelta(hours=1)
            is_first_slot = False

    context = {
        'today': today,
        'start_of_week': start_of_week.date(),
        'end_of_week': end_of_week.date(),
        'week_days_data': week_days_data,
        'events_by_day': events_by_day,
        'time_slots': [f"{h:02d}:00" for h in range(CALENDAR_START_HOUR, CALENDAR_END_HOUR + 1)],
        'current_month_name': start_of_week.strftime("%B"),
        'current_week_range': f"{start_of_week.day:02d}-{end_of_week.day:02d} {start_of_week.strftime('%B')} {start_of_week.year}",
    }
    return render(request, 'horarios.html', context)

@login_required
def optimize_schedule(request):
    """
    Vista para optimizar el horario del usuario usando IA.
    """
    try:
        if request.method == 'POST':
            user_events = Event.objects.filter(user=request.user).order_by('start_time')
            
            print(f"DEBUG: Usuario {request.user.username}")
            print(f"DEBUG: Total de eventos: {user_events.count()}")
            
            if not user_events.exists():
                return JsonResponse({
                    'suggestions': [],
                    'message': 'No hay tareas creadas.'
                })
            
            # Mostrar información de las tareas
            for event in user_events:
                print(f"DEBUG: Tarea: {event.title}, Completada: {event.is_completed}, Fecha: {event.start_time}")
                
            # Crear sugerencias considerando si la tarea está completada o no
            suggestions_data = []
            for i, event in enumerate(user_events):
                if event.is_completed:
                    # Para tareas completadas, sugerir mantener horario actual
                    new_start = event.start_time
                    new_end = event.end_time
                    reason = "Tarea completada, se mantiene el horario actual"
                    improvement_score = 0.0
                else:
                    # Para tareas no completadas, sugerir cambios alternados
                    if i % 2 == 0:
                        new_start = event.start_time + timedelta(hours=1)
                        reason = "Mover 1 hora más tarde puede mejorar la concentración"
                    else:
                        new_start = event.start_time - timedelta(hours=1)
                        reason = "Mover 1 hora más temprano puede ser más productivo"
                    new_end = new_start + (event.end_time - event.start_time)
                    improvement_score = 0.8 + (i * 0.1)
                
                suggestions_data.append({
                    'event_id': event.id,
                    'title': event.title,
                    'current_time': event.start_time.isoformat(),
                    'suggested_time': new_start.isoformat(),
                    'suggested_end_time': new_end.isoformat(),
                    'improvement_score': improvement_score,
                    'reason': reason,
                })

            print(f"DEBUG: Sugerencias generadas: {len(suggestions_data)}")
            return JsonResponse({'suggestions': suggestions_data})
        else:
            return JsonResponse({'error': 'Método no permitido'}, status=405)
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        return JsonResponse({
            'error': f'Error al optimizar el horario: {str(e)}'
        }, status=500)

@login_required
def event_update_ajax(request, pk):
    """
    Vista para actualizar un evento vía AJAX.
    """
    if request.method == 'POST':
        try:
            event = get_object_or_404(Event, pk=pk, user=request.user)
            body = request.body.decode('utf-8')
            data = json.loads(body)
            
            # Convertir fechas ISO a datetime
            start_time_str = data['start_time'].replace('Z', '+00:00')
            end_time_str = data['end_time'].replace('Z', '+00:00')
            
            event.start_time = datetime.fromisoformat(start_time_str)
            event.end_time = datetime.fromisoformat(end_time_str)
            event.save()
            
            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Datos JSON inválidos'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
@require_GET
def list_user_events(request):
    """
    Vista para listar las tareas del usuario con fechas actuales en JSON.
    """
    events = Event.objects.filter(user=request.user).order_by('start_time')
    events_data = []
    for event in events:
        events_data.append({
            'id': event.id,
            'title': event.title,
            'start_time': event.start_time.isoformat(),
            'end_time': event.end_time.isoformat(),
            'is_completed': event.is_completed,
        })
    return JsonResponse({'events': events_data})

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
            
            # Cambiar el estado
            event.is_completed = not event.is_completed
            event.save()
            
            print(f"Evento {event.pk} actualizado. Completado: {event.is_completed}")  # Debug
            
            return JsonResponse({
                'success': True,
                'is_completed': event.is_completed,
                'message': 'Completado' if event.is_completed else 'Pendiente'
            })
        except Exception as e:
            print(f"Error al actualizar evento: {str(e)}")  # Debug
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

# Tareas 

@login_required
def tareas_view(request):
    """
    Vista para mostrar las tareas organizadas por días de la semana y agrupadas por materia.
    """
    # Obtener la fecha actual
    today = timezone.localdate()
    
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
    
    # Función para extraer materia del título
    def extract_subject_from_title(title):
        # Normalizar el título
        title_lower = title.lower().strip()
        
        # Mapeo de palabras clave a materias (buscar en el título)
        subject_keywords = {
            'Matemáticas': ['matematicas', 'matemáticas', 'algebra', 'álgebra', 'calculo', 'cálculo', 'geometria', 'geometría', 'trigonometria', 'trigonometría'],
            'Filosofía': ['filosofia', 'filosofía', 'etica', 'ética', 'logica', 'lógica'],
            'Biología': ['biologia', 'biología', 'anatomia', 'anatomía', 'celula', 'célula', 'genetica', 'genética'],
            'Física': ['fisica', 'física', 'mecanica', 'mecánica', 'termodinamica', 'termodinámica', 'optica', 'óptica'],
            'Química': ['quimica', 'química', 'organica', 'orgánica', 'inorganica', 'inorgánica', 'laboratorio'],
            'Historia': ['historia', 'guerra', 'revolucion', 'revolución', 'antigua', 'medieval'],
            'Inglés': ['ingles', 'inglés', 'english'],
            'Francés': ['frances', 'francés', 'french'],
            'Arte': ['arte', 'pintura', 'musica', 'música', 'teatro', 'danza', 'literatura'],
            'Deportes': ['deportes', 'futbol', 'fútbol', 'basquet', 'natacion', 'natación', 'atletismo'],
            'Programación': ['programacion', 'programación', 'codigo', 'código', 'python', 'javascript', 'html', 'css']
        }
        
        # Buscar coincidencia exacta primero (si el título ES la materia)
        for subject, keywords in subject_keywords.items():
            if title_lower in [kw.lower() for kw in keywords] or title_lower == subject.lower():
                return subject
        
        # Buscar si el título CONTIENE alguna palabra clave
        for subject, keywords in subject_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                return subject
        
        # Si no encuentra nada específico, usar el título como está (capitalizado)
        return title.strip().title()
    
    # Agrupar eventos por día de la semana
    for event in user_events:
        day_of_week = event.start_time.weekday()
        subject = extract_subject_from_title(event.title)
        
        events_by_day[day_of_week].append({
            'id': event.pk,
            'title': event.title,
            'description': event.description or 'Sin descripción',
            'start_time': event.start_time,
            'end_time': event.end_time,
            'event_type': event.event_type,
            'is_completed': event.is_completed,
            'priority': event.priority,
            'due_date': event.due_date,
            'css_class': f"event-{event.event_type}",
            'subject': subject,  # El tema/materia extraído del título
        })

    # Crear datos para cada día de la semana
    week_days_data = []
    for i in range(7):
        current_day_date = start_of_week + timedelta(days=i)
        
        # Agrupar eventos por materia para este día
        day_events = events_by_day[i]
        subjects_dict = {}
        
        for event in day_events:
            subject = event['subject']
            if subject not in subjects_dict:
                subjects_dict[subject] = []
            subjects_dict[subject].append(event)
        
        week_days_data.append({
            'day_name': day_names_es[i],
            'day_name_short': day_names_es[i][:3],
            'day_num': current_day_date.day,
            'date': current_day_date,
            'is_today': current_day_date == today,
            'events': day_events,  # Todos los eventos del día
            'subjects': subjects_dict,  # Eventos agrupados por materia
            'event_count': len(day_events),
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