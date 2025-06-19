from time import localtime
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, time, timedelta
from django.utils import timezone
from planner.ai_optimizer import SmartScheduleOptimizer
from django.views.decorators.http import require_POST
from .models import Event
from .forms import EventForm
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
import json
import pytz
from core.models import UserSettings
from .models import BloqueEstudio
from .ia_generador import generar_bloques_enfocados_semana

@login_required
def calendar_view(request):
    # Obtener la zona horaria del usuario
    try:
        user_settings = UserSettings.objects.get(user=request.user)
        user_tz = pytz.timezone(user_settings.timezone)
    except (UserSettings.DoesNotExist, pytz.exceptions.UnknownTimeZoneError):
        user_tz = pytz.timezone('America/Guayaquil')

    # Obtener la fecha de referencia desde los parámetros GET
    date_param = request.GET.get('date')
    direction = request.GET.get('direction', 'current')
    
    # Determinar la fecha base en la zona horaria del usuario
    if date_param:
        try:
            base_date = datetime.strptime(date_param, '%Y-%m-%d')
            base_date = user_tz.localize(base_date)
        except ValueError:
            base_date = timezone.now().astimezone(user_tz)
    else:
        base_date = timezone.now().astimezone(user_tz)

    # Asegurarnos de que base_date sea una fecha
    base_date = base_date.date()

    # Aplicar la dirección de navegación
    if direction == 'prev':
        base_date = base_date - timedelta(weeks=1)
    elif direction == 'next':
        base_date = base_date + timedelta(weeks=1)

    today = timezone.now().date()

    # Calcular el inicio y fin de la semana (lunes a domingo)
    start_of_week = base_date - timedelta(days=base_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Convertir a datetime aware en la zona horaria del usuario
    start_of_week_dt = user_tz.localize(datetime.combine(start_of_week, datetime.min.time()))
    end_of_week_dt = user_tz.localize(datetime.combine(end_of_week, datetime.max.time()))

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
        start_time__gte=start_of_week_dt,
        start_time__lte=end_of_week_dt
    ).order_by('start_time')

    # Convertir los eventos a la zona horaria del usuario
    for event in user_events:
        event.start_time = event.start_time.astimezone(user_tz)
        event.end_time = event.end_time.astimezone(user_tz)
        if event.due_date:
            # La fecha de vencimiento ya es un objeto date, no necesita conversión de zona horaria
            pass

    # Configuración del calendario
    CALENDAR_START_HOUR = 0
    CALENDAR_END_HOUR = 23

    # Agrupar eventos por día y hora, incluyendo todas las horas que abarca cada evento
    events_by_day = {i: {f"{h:02d}:00": [] for h in range(CALENDAR_START_HOUR, CALENDAR_END_HOUR + 1)} for i in range(7)}
    for event in user_events:
        # Los eventos ya están convertidos a la zona horaria del usuario
        start_time_local = event.start_time
        end_time_local = event.end_time
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

    # Nombres de los meses en español
    months_es = {
        'January': 'enero',
        'February': 'febrero',
        'March': 'marzo',
        'April': 'abril',
        'May': 'mayo',
        'June': 'junio',
        'July': 'julio',
        'August': 'agosto',
        'September': 'septiembre',
        'October': 'octubre',
        'November': 'noviembre',
        'December': 'diciembre'
    }
    
    # Obtener el nombre del mes en español
    month_name_en = start_of_week.strftime("%B")
    month_name_es = months_es.get(month_name_en, month_name_en)
    
    context = {
        'today': today,
        'start_of_week': start_of_week,
        'end_of_week': end_of_week,
        'week_days_data': week_days_data,
        'events_by_day': events_by_day,
        'time_slots': [f"{h:02d}:00" for h in range(CALENDAR_START_HOUR, CALENDAR_END_HOUR + 1)],
        'current_month_name': month_name_es,
        'current_week_range': f"{start_of_week.day:02d}-{end_of_week.day:02d} de {month_name_es} de {start_of_week.year}",
    }
    return render(request, 'horarios.html', context)

@csrf_exempt
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

# --- VISTA PARA OPTIMIZACIÓN CON IA ---
@csrf_exempt
@login_required
def optimize_schedule(request):
    """
    Vista para optimizar el horario del usuario usando IA.
    """
    if request.method == 'POST':
        try:
            # Inicializar el optimizador de IA
            optimizer = SmartScheduleOptimizer()
            
            if not optimizer.is_loaded:
                return JsonResponse({
                    'success': False,
                    'message': 'El modelo de IA no está disponible. Verifica que los archivos del modelo estén en la carpeta trained_models.'
                })
            
            # Obtener eventos del usuario para la próxima semana
            today = timezone.localdate()
            start_date = today
            end_date = today + timedelta(days=7)
            
            user_events = Event.objects.filter(
                user=request.user,
                start_time__date__gte=start_date,
                start_time__date__lte=end_date,
                is_completed=False  # Solo eventos pendientes
            )
            
            if not user_events.exists():
                return JsonResponse({
                    'success': True,
                    'suggestions': [],
                    'message': 'No hay eventos pendientes para optimizar en los próximos 7 días.'
                })
            
            # Verificar que hay al menos 4 tareas para generar sugerencias óptimas
            if user_events.count() < 4:
                return JsonResponse({
                    'success': True,
                    'suggestions': [],
                    'message': 'Se necesitan al menos 4 tareas programadas para generar sugerencias de optimización precisas.',
                    'insufficient_tasks': True,
                    'current_tasks': user_events.count()
                })
            
            # Obtener sugerencias de optimización
            suggestions = []
            for event in user_events:
                # Excluir el evento actual al verificar conflictos
                other_events = user_events.exclude(pk=event.pk)
                
                # Convertir evento Django a formato del modelo
                event_data = {
                    'event_type': optimizer._map_django_event_type(event.event_type),
                    'priority': optimizer._map_django_priority(event.priority),
                    'duration': optimizer._calculate_duration(event.start_time, event.end_time),
                    'weekday': event.start_time.weekday(),
                    'due_date': event.due_date,
                    'start_date': start_date
                }
                
                # Obtener predicción pasando los otros eventos para verificar conflictos
                prediction = optimizer.predict_best_schedule(event_data, other_events)
                
                # Crear horario sugerido
                current_date = event.start_time.date()
                suggested_datetime = datetime.combine(
                    current_date, 
                    datetime.min.time().replace(hour=prediction['mejor_hora'])
                )
                suggested_end_datetime = suggested_datetime + timedelta(hours=event_data['duration'])
                
                # Solo sugerir si es diferente al horario actual y está disponible
                if suggested_datetime.hour != event.start_time.hour and prediction.get('disponible', True):
                    suggestions.append({
                        'event_id': event.id,
                        'title': event.title,
                        'current_time': event.start_time.isoformat(),
                        'suggested_time': suggested_datetime.isoformat(),
                        'suggested_end_time': suggested_end_datetime.isoformat(),
                        'improvement_score': round((prediction['score'] - 0.5) * 100, 1),
                        'confianza': prediction['confianza'],
                        'mejor_hora': prediction['mejor_hora'],
                        'todas_opciones': prediction['todas_opciones'],
                        'reason': optimizer._generate_reason(event_data, prediction)
                    })
            
            if not suggestions:
                return JsonResponse({
                    'success': True,
                    'suggestions': [],
                    'message': 'Tu horario ya está optimizado. No se encontraron mejoras significativas.'
                })
            
            return JsonResponse({
                'success': True,
                'suggestions': suggestions,
                'message': f'Se encontraron {len(suggestions)} sugerencias de optimización.'
            })
            
        except Exception as e:
            print(f"Error en optimización: {str(e)}")  # Debug
            return JsonResponse({
                'success': False,
                'message': f'Error al optimizar el horario: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@login_required
@require_POST
def suggestions_template(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        suggestions = data.get('suggestions', [])
        
        # Debug: imprimir las sugerencias recibidas
        print(f"Sugerencias recibidas: {suggestions}")
        
        # Renderizar el template directamente
        return render(request, 'suggestions_modal.html', {
            'suggestions': suggestions
        })
        
    except json.JSONDecodeError as e:
        print(f"Error JSON: {e}")
        return render(request, 'suggestions_modal.html', {'suggestions': []})
    except Exception as e:
        print(f"Error en suggestions_template: {e}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error: {str(e)}", status=500)
    

@login_required
def focused_time_view(request):
    # Siempre usar valores fijos para la tabla
    bloques = generar_bloques_enfocados_semana(request.user, duracion_enfoque=25, duracion_descanso=5)

    # Paso 1: Agrupar eventos por día
    eventos_por_dia = defaultdict(list)
    eventos = Event.objects.filter(user=request.user).order_by("start_time")

    for evento in eventos:
        fecha = evento.start_time.date()
        eventos_por_dia[fecha].append({
            "title": evento.title,
            "start_time": evento.start_time,
            "end_time": evento.end_time,
            "event_type": evento.event_type.lower()
        })

    # Paso 3: Formato para HTML
    for bloque in bloques:
        # Usar timezone.localtime si los bloques tienen zona horaria, de lo contrario usar directamente
        bloque["start_time"] = bloque["start_time"].replace(tzinfo=None) if hasattr(bloque["start_time"], 'replace') else bloque["start_time"]
        bloque["end_time"] = bloque["end_time"].replace(tzinfo=None) if hasattr(bloque["end_time"], 'replace') else bloque["end_time"]
        bloque["hora_slot"] = bloque["start_time"].strftime("%H:%M")
        bloque["weekday"] = bloque["start_time"].weekday()

    # Rango de horas de la tabla
    horas = []
    actual = datetime.combine(timezone.now().date(), time(6, 0)).replace(tzinfo=None)
    final = datetime.combine(timezone.now().date(), time(22, 0)).replace(tzinfo=None)
    while actual <= final:
        horas.append(actual.strftime("%H:%M"))
        actual += timedelta(minutes=5)

    context = {
        "bloques": bloques,
        "horas": horas,
    }
    return render(request, "bloques_enfocados.html", context)

#---------------Vista de productividad---------------

from django.shortcuts import render
from planner.models import BloqueEstudio
from django.db.models import Sum
from datetime import date, timedelta
from collections import defaultdict

@login_required
def productividad_view(request):
    usuario = request.user
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())  # Lunes

    bloques = BloqueEstudio.objects.filter(
        usuario=usuario,
        fecha__range=(inicio_semana, hoy),
        completado=True
    )

    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    productividad_dias = [0] * 7

    for bloque in bloques:
        index = bloque.fecha.weekday()
        productividad_dias[index] += bloque.duracion_min

    hoy_index = hoy.weekday()
    minutos_hoy = productividad_dias[hoy_index]
    promedio = sum(productividad_dias[:hoy_index]) / hoy_index if hoy_index > 0 else 1
    dif_ayer = minutos_hoy - productividad_dias[hoy_index - 1] if hoy_index > 0 else 0
    dif_promedio = minutos_hoy - promedio

    productividad_hoy_percent = int((minutos_hoy / promedio) * 100) if promedio > 0 else 0

    context = {
        'productividad_dias': productividad_dias,
        'productividad_hoy': productividad_hoy_percent,
        'productividad_restante': 100 - productividad_hoy_percent,

        'dif_ayer_valor': abs(int(dif_ayer / productividad_dias[hoy_index - 1] * 100)) if hoy_index > 0 and productividad_dias[hoy_index - 1] > 0 else 0,
        'dif_ayer_positivo': dif_ayer >= 0,

        'dif_promedio_valor': abs(int(dif_promedio / promedio * 100)) if promedio > 0 else 0,
        'dif_promedio_positivo': dif_promedio >= 0,

        'dia_productivo': dias[productividad_dias.index(max(productividad_dias))] if max(productividad_dias) > 0 else "Ninguno",
        'mejor_rango': calcular_mejor_rango(bloques),
    }
    return render(request, 'productividad.html', context)

def calcular_mejor_rango(bloques):
    rangos_definidos = {
        "6:00 a.m. - 9:00 a.m.": (6, 9),
        "9:00 a.m. - 12:00 p.m.": (9, 12),
        "12:00 p.m. - 3:00 p.m.": (12, 15),
        "3:00 p.m. - 6:00 p.m.": (15, 18),
        "6:00 p.m. - 9:00 p.m.": (18, 21),
    }

    rendimiento = defaultdict(int)

    for bloque in bloques:
        print(f"▶️ Analizando bloque: {bloque.fecha} - {bloque.hora_inicio} - {bloque.duracion_min} min")
        if bloque.hora_inicio:
            hora = bloque.hora_inicio.hour
            for nombre_rango, (inicio, fin) in rangos_definidos.items():
                if inicio <= hora < fin:
                    rendimiento[nombre_rango] += bloque.duracion_min
                    print(f"✅ Bloque añadido a: {nombre_rango}")
                    break
            else:
                print(f"❌ Hora {hora} fuera de todos los rangos")

    print("📊 Resultado final:", rendimiento)
    return max(rendimiento, key=rendimiento.get) if rendimiento else "Ninguno"



#---------------vista de bloques guardados
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import BloqueEstudio
import json
from django.utils import timezone



@csrf_exempt
def registrar_bloque_temporizador(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        tipo = data.get('tipo', '').lower()
        if tipo not in ['estudio', 'descanso']:
            return JsonResponse({'error': 'Tipo inválido'}, status=400)
        try:
            duracion = int(data.get('duracion', 0))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Duración inválida'}, status=400)
        hora_inicio = timezone.localtime()
        hora_fin = hora_inicio + timedelta(minutes=duracion)
        print(" Hora guardada:", hora_inicio.time())

        BloqueEstudio.objects.create(
            usuario=request.user,
            tipo=tipo,
            fecha=hora_inicio.date(),
            hora_inicio=hora_inicio.time(),
            hora_fin=hora_fin.time(),
            duracion_min=duracion,
            completado=True
        )
        print("🔎 Usuario autenticado:", request.user)
        print("🔎 ¿Está autenticado?:", request.user.is_authenticated)

        return JsonResponse({'mensaje': 'Bloque guardado exitosamente'})
    return JsonResponse({'error': 'Método no permitido'}, status=405)
#----vista para obtener estadisticas 
from .models import BloqueEstudio

def obtener_estadisticas_productividad(request):
    usuario = request.user
    hoy = timezone.now().date()

    bloques_hoy = BloqueEstudio.objects.filter(usuario=usuario, fecha=hoy)

    bloques_estudio = bloques_hoy.filter(tipo='estudio')
    total_estudio = bloques_estudio.count()

    tiempo_total = bloques_hoy.aggregate(Sum('duracion_min'))['duracion_min__sum'] or 0

    print("Usuario:", usuario)
    print("Fecha:", hoy)
    print("Total bloques hoy:", bloques_hoy.count())
    print("Todos los bloques hoy:", list(bloques_hoy.values()))


    return JsonResponse({
        'bloques_estudio': total_estudio,
        'minutos_totales': tiempo_total,
    })

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import date
from .models import BloqueEstudio  # Asegúrate de importar bien tu modelo

@login_required
def productividad_api(request):
    hoy = date.today()

    bloques = BloqueEstudio.objects.filter(
        usuario=request.user,
        fecha=hoy,
        tipo='estudio',
        completado=True
    )

    bloques_completados = bloques.count()
    minutos_totales = sum([b.duracion_min for b in bloques])

    return JsonResponse({
        "bloques_estudio": bloques_completados,
        "minutos_totales": minutos_totales,
    })
