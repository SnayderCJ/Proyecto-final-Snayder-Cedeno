from time import localtime
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, time, timedelta, date
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

def get_productividad_hoy(usuario):
    hoy = date.today()
    bloques = BloqueEstudio.objects.filter(
        usuario=usuario,
        fecha=hoy,
        completado=True
    )
    eventos = Event.objects.filter(
        user=usuario,
        start_time__date=hoy,
        is_completed=True,
        event_type__in=['tarea', 'clase']
    )
    minutos_bloques = sum(bloque.duracion_min for bloque in bloques)
    minutos_eventos = sum(
        int((evento.end_time - evento.start_time).total_seconds() / 60)
        for evento in eventos
    )
    minutos_totales = minutos_bloques + minutos_eventos
    meta_diaria = 120
    porcentaje = int((minutos_totales / meta_diaria) * 100) if minutos_totales > 0 else 0
    return min(100, porcentaje)

@login_required
def calendar_view(request):
    try:
        user_settings = UserSettings.objects.get(user=request.user)
        user_tz = pytz.timezone(user_settings.timezone)
    except (UserSettings.DoesNotExist, pytz.exceptions.UnknownTimeZoneError):
        user_tz = pytz.timezone('America/Guayaquil')
    date_param = request.GET.get('date')
    direction = request.GET.get('direction', 'current')
    if date_param:
        try:
            base_date = datetime.strptime(date_param, '%Y-%m-%d')
            base_date = user_tz.localize(base_date)
        except ValueError:
            base_date = timezone.now().astimezone(user_tz)
    else:
        base_date = timezone.now().astimezone(user_tz)
    base_date = base_date.date()
    if direction == 'prev':
        base_date = base_date - timedelta(weeks=1)
    elif direction == 'next':
        base_date = base_date + timedelta(weeks=1)
    today = timezone.now().date()
    start_of_week = base_date - timedelta(days=base_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    start_of_week_dt = user_tz.localize(datetime.combine(start_of_week, datetime.min.time()))
    end_of_week_dt = user_tz.localize(datetime.combine(end_of_week, datetime.max.time()))
    day_names_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
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
    user_events = Event.objects.filter(
        user=request.user,
        start_time__gte=start_of_week_dt,
        start_time__lte=end_of_week_dt
    ).order_by('start_time')
    for event in user_events:
        event.start_time = event.start_time.astimezone(user_tz)
        event.end_time = event.end_time.astimezone(user_tz)
        if event.due_date:
            pass
    CALENDAR_START_HOUR = 0
    CALENDAR_END_HOUR = 23
    events_by_day = {i: {f"{h:02d}:00": [] for h in range(CALENDAR_START_HOUR, CALENDAR_END_HOUR + 1)} for i in range(7)}
    for event in user_events:
        start_time_local = event.start_time
        end_time_local = event.end_time
        weekday = start_time_local.weekday()
        css_class_type = f"event-{event.event_type}"
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
    if request.method == 'POST':
        try:
            event = get_object_or_404(Event, pk=pk, user=request.user)
            body = request.body.decode('utf-8')
            data = json.loads(body)
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

@login_required
def event_create(request):
    if request.method == 'POST':
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
        initial_data = {
            'start_time': datetime.now().strftime('%Y-%m-%dT%H:%M'),
            'end_time': (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'),
        }
        form = EventForm(initial=initial_data, user=request.user)
    return render(request, 'pages/horarios/event_form.html', {'form': form, 'form_type': 'Crear'})

@login_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk, user=request.user)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Evento "{event.title}" actualizado exitosamente.')
            return redirect('planner:event_detail', pk=event.pk)
        else:
            messages.error(request, '❌ Hubo errores en el formulario. Por favor revisa los datos.')
    else:
        form = EventForm(instance=event, user=request.user)
    return render(request, 'pages/horarios/event_form.html', {
        'form': form, 
        'form_type': 'Editar', 
        'event': event
    })

@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk, user=request.user)
    event_title = event.title
    if request.method == 'POST':
        event.delete()
        messages.success(request, f'🗑️ Evento "{event_title}" eliminado exitosamente.')
        return redirect('planner:horarios')
    return render(request, 'pages/horarios/event_confirm_delete.html', {'event': event})

@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, user=request.user)
    return render(request, 'pages/horarios/event_detail.html', {'event': event})

@login_required
def toggle_event_completion(request, pk):
    if request.method == 'POST':
        try:
            event = get_object_or_404(Event, pk=pk, user=request.user)
            event.is_completed = not event.is_completed
            event.save()
            print(f"Evento {event.pk} actualizado. Completado: {event.is_completed}")
            return JsonResponse({
                'success': True,
                'is_completed': event.is_completed,
                'message': 'Completado' if event.is_completed else 'Pendiente'
            })
        except Exception as e:
            print(f"Error al actualizar evento: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def tareas_view(request):
    today = timezone.localdate()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    user_events = Event.objects.filter(
        user=request.user,
        start_time__date__gte=start_of_week,
        start_time__date__lte=end_of_week
    ).order_by('start_time')
    day_names_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    events_by_day = {i: [] for i in range(7)}
    def extract_subject_from_title(title):
        title_lower = title.lower().strip()
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
        for subject, keywords in subject_keywords.items():
            if title_lower in [kw.lower() for kw in keywords] or title_lower == subject.lower():
                return subject
        for subject, keywords in subject_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                return subject
        return title.strip().title()
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
            'subject': subject,
        })
    week_days_data = []
    for i in range(7):
        current_day_date = start_of_week + timedelta(days=i)
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
            'events': day_events,
            'subjects': subjects_dict,
            'event_count': len(day_events),
        })
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
        'total_events': total_events,
        'completed_events': completed_events,
        'pending_events': pending_events,
    }
    return render(request, 'tareas.html', context)

@csrf_exempt
@login_required
def optimize_schedule(request):
    if request.method == 'POST':
        try:
            optimizer = SmartScheduleOptimizer()
            if not optimizer.is_loaded:
                return JsonResponse({
                    'success': False,
                    'message': 'El modelo de IA no está disponible. Verifica que los archivos del modelo estén en la carpeta trained_models.'
                })
            today = timezone.localdate()
            start_date = today
            end_date = today + timedelta(days=7)
            user_events = Event.objects.filter(
                user=request.user,
                start_time__date__gte=start_date,
                start_time__date__lte=end_date,
                is_completed=False
            )
            if not user_events.exists():
                return JsonResponse({
                    'success': True,
                    'suggestions': [],
                    'message': 'No hay eventos pendientes para optimizar en los próximos 7 días.'
                })
            if user_events.count() < 4:
                return JsonResponse({
                    'success': True,
                    'suggestions': [],
                    'message': 'Se necesitan al menos 4 tareas programadas para generar sugerencias de optimización precisas.',
                    'insufficient_tasks': True,
                    'current_tasks': user_events.count()
                })
            suggestions = []
            for event in user_events:
                other_events = user_events.exclude(pk=event.pk)
                event_data = {
                    'event_type': optimizer._map_django_event_type(event.event_type),
                    'priority': optimizer._map_django_priority(event.priority),
                    'duration': optimizer._calculate_duration(event.start_time, event.end_time),
                    'weekday': event.start_time.weekday(),
                    'due_date': event.due_date,
                    'start_date': start_date
                }
                prediction = optimizer.predict_best_schedule(event_data, other_events)
                current_date = event.start_time.date()
                suggested_datetime = datetime.combine(
                    current_date, 
                    datetime.min.time().replace(hour=prediction['mejor_hora'])
                )
                suggested_end_datetime = suggested_datetime + timedelta(hours=event_data['duration'])
                has_conflict = False
                for existing_suggestion in suggestions:
                    existing_start = datetime.fromisoformat(existing_suggestion['suggested_time_iso'])
                    existing_end = datetime.fromisoformat(existing_suggestion['suggested_end_time_iso'])
                    if (suggested_datetime <= existing_end and 
                        suggested_end_datetime >= existing_start and
                        existing_start.date() == suggested_datetime.date()):
                        has_conflict = True
                        break
                if (suggested_datetime.hour != event.start_time.hour and 
                    prediction.get('disponible', True) and 
                    not has_conflict):
                    suggestions.append({
                        'event_id': event.id,
                        'title': event.title,
                        'current_time': event.start_time.strftime('%H:%M'),
                        'suggested_time': suggested_datetime.strftime('%H:%M'),
                        'suggested_end_time': suggested_end_datetime.strftime('%H:%M'),
                        'current_time_iso': event.start_time.isoformat(),
                        'suggested_time_iso': suggested_datetime.isoformat(),
                        'suggested_end_time_iso': suggested_end_datetime.isoformat(),
                        'improvement_score': round((prediction['score'] - 0.5) * 100, 1),
                        'confianza': round(prediction['confianza'] * 100),
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
            print(f"Error en optimización: {str(e)}")
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
        print(f"Sugerencias recibidas: {suggestions}")
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
    bloques = generar_bloques_enfocados_semana(request.user, duracion_enfoque=25, duracion_descanso=5)
    from collections import defaultdict
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
    for bloque in bloques:
        bloque["start_time"] = bloque["start_time"].replace(tzinfo=None) if hasattr(bloque["start_time"], 'replace') else bloque["start_time"]
        bloque["end_time"] = bloque["end_time"].replace(tzinfo=None) if hasattr(bloque["end_time"], 'replace') else bloque["end_time"]
        bloque["hora_slot"] = bloque["start_time"].strftime("%H:%M")
        bloque["weekday"] = bloque["start_time"].weekday()
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

from django.shortcuts import render
from planner.models import BloqueEstudio
from django.db.models import Sum
from datetime import date, timedelta
from collections import defaultdict

@login_required
def productividad_view(request):
    usuario = request.user
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    bloques = BloqueEstudio.objects.filter(
        usuario=usuario,
        fecha__range=(inicio_semana, fin_semana),
        completado=True
    )
    eventos_completados = Event.objects.filter(
        user=usuario,
        start_time__date__range=(inicio_semana, fin_semana),
        is_completed=True,
        event_type__in=['tarea', 'clase']
    ).order_by('start_time')
    print(f"🔍 Debug - Usuario: {usuario}")
    print(f"🔍 Debug - Fecha hoy: {hoy}")
    print(f"🔍 Debug - Inicio semana: {inicio_semana}")
    print(f"🔍 Debug - Total bloques encontrados: {bloques.count()}")
    print(f"🔍 Debug - Total eventos completados: {eventos_completados.count()}")
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    productividad_dias = [0] * 7
    for dia in range(7):
        fecha_actual = inicio_semana + timedelta(days=dia)
        bloques_dia = [b for b in bloques if b.fecha == fecha_actual]
        minutos_bloques = sum(b.duracion_min for b in bloques_dia)
        eventos_dia = [e for e in eventos_completados if e.start_time.date() == fecha_actual]
        minutos_eventos = sum(
            int((e.end_time - e.start_time).total_seconds() / 60)
            for e in eventos_dia
        )
        productividad_dias[dia] = minutos_bloques + minutos_eventos
    minutos_originales = productividad_dias.copy()
    if all(m == 0 for m in productividad_dias):
        print("⚠️ No hay actividad registrada. Usando datos de ejemplo.")
        productividad_dias = [0, 0, 0, 0, 0, 0, 0]
    meta_diaria = 120
    productividad_dias_porcentajes = [min(100, int((minutos / meta_diaria) * 100)) for minutos in productividad_dias]
    print(f"🔍 Debug - Productividad por días (minutos): {productividad_dias}")
    print(f"🔍 Debug - Productividad por días (porcentajes): {productividad_dias_porcentajes}")
    hoy_index = hoy.weekday()
    minutos_hoy = minutos_originales[hoy_index]
    dias_anteriores = minutos_originales[:hoy_index] if hoy_index > 0 else [60]
    promedio = sum(dias_anteriores) / len(dias_anteriores) if len(dias_anteriores) > 0 else 60
    dif_ayer = minutos_hoy - minutos_originales[hoy_index - 1] if hoy_index > 0 else 0
    dif_promedio = minutos_hoy - promedio
    productividad_hoy_percent = min(100, int((minutos_hoy / meta_diaria) * 100)) if minutos_hoy > 0 else 0
    minutos_ayer = minutos_originales[hoy_index - 1] if hoy_index > 0 else 0
    porcentaje_ayer = min(100, int((minutos_ayer / meta_diaria) * 100)) if minutos_ayer > 0 else 0
    porcentaje_promedio = min(100, int((promedio / meta_diaria) * 100)) if promedio > 0 else 0
    dif_ayer_puntos = productividad_hoy_percent - porcentaje_ayer
    dif_promedio_puntos = productividad_hoy_percent - porcentaje_promedio
    print(f"🎯 Meta diaria: {meta_diaria} minutos")
    print(f"⏱️ Minutos completados hoy: {minutos_hoy}")
    print(f"⏱️ Minutos completados ayer: {minutos_ayer}")
    print(f"📊 Porcentaje de productividad hoy: {productividad_hoy_percent}%")
    print(f"📊 Porcentaje de productividad ayer: {porcentaje_ayer}%")
    print(f"📊 Diferencia en puntos porcentuales: {dif_ayer_puntos}%")
    import json
    dias_nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    datos_productividad = []
    for i, porcentaje in enumerate(productividad_dias_porcentajes):
        datos_productividad.append({
            'name': dias_nombres[i],
            'percentage': porcentaje
        })
    context = {
        'productividad_dias': json.dumps(datos_productividad),
        'productividad_hoy': productividad_hoy_percent,
        'productividad_restante': 100 - productividad_hoy_percent,
        'dif_ayer_valor': abs(dif_ayer_puntos),
        'dif_ayer_positivo': dif_ayer_puntos >= 0,
        'dif_promedio_valor': abs(dif_promedio_puntos),
        'dif_promedio_positivo': dif_promedio_puntos >= 0,
        'dia_productivo': dias[minutos_originales.index(max(minutos_originales))] if max(minutos_originales) > 0 else "Ninguno",
        'mejor_rango': calcular_mejor_rango_combinado(bloques, eventos_completados),
        'total_bloques': bloques.count(),
        'total_eventos': eventos_completados.count(),
        'minutos_hoy': minutos_hoy,
        'meta_diaria': meta_diaria,
    }
    return render(request, 'productividad.html', context)

def calcular_mejor_rango_combinado(bloques, eventos):
    rangos_definidos = {
        "6:00 a.m. - 9:00 a.m.": (6, 9),
        "9:00 a.m. - 12:00 p.m.": (9, 12),
        "12:00 p.m. - 3:00 p.m.": (12, 15),
        "3:00 p.m. - 6:00 p.m.": (15, 18),
        "6:00 p.m. - 9:00 p.m.": (18, 21),
        "9:00 p.m. - 12:00 a.m.": (21, 24),
    }
    rendimiento = defaultdict(int)
    total_actividad = 0
    for bloque in bloques:
        print(f"▶️ Analizando bloque: {bloque.fecha} - {bloque.hora_inicio} - {bloque.duracion_min} min")
        if bloque.hora_inicio:
            hora = bloque.hora_inicio.hour
            total_actividad += bloque.duracion_min
            for nombre_rango, (inicio, fin) in rangos_definidos.items():
                if inicio <= hora < fin:
                    rendimiento[nombre_rango] += bloque.duracion_min
                    print(f"✅ Bloque añadido a: {nombre_rango}")
                    break
            else:
                print(f"❌ Hora {hora} fuera de todos los rangos")
    for evento in eventos:
        try:
            hora_inicio = evento.start_time.hour
            duracion = int((evento.end_time - evento.start_time).total_seconds() / 60)
            total_actividad += duracion
            print(f"▶️ Analizando evento: {evento.title} - {hora_inicio}h - {duracion} min")
            for nombre_rango, (inicio, fin) in rangos_definidos.items():
                if inicio <= hora_inicio < fin:
                    rendimiento[nombre_rango] += duracion
                    print(f"✅ Evento añadido a: {nombre_rango}")
                    break
            else:
                print(f"❌ Hora {hora_inicio} fuera de todos los rangos")
        except Exception as e:
            print(f"❌ Error procesando evento {evento.title}: {e}")
    print(f"📊 Total actividad encontrada: {total_actividad} minutos")
    print("📊 Rendimiento por rangos:", dict(rendimiento))
    if total_actividad == 0:
        print("⚠️ No hay actividad real, usando datos de ejemplo")
        rendimiento["9:00 a.m. - 12:00 p.m."] = 45
        rendimiento["3:00 p.m. - 6:00 p.m."] = 30
        rendimiento["6:00 p.m. - 9:00 p.m."] = 60
    if rendimiento:
        mejor_rango = max(rendimiento, key=rendimiento.get)
        print(f"🏆 Mejor rango: {mejor_rango} con {rendimiento[mejor_rango]} minutos")
        return mejor_rango
    else:
        return "6:00 a.m. - 9:00 a.m."

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

from .models import BloqueEstudio

@login_required
def obtener_estadisticas_productividad(request):
    usuario = request.user
    hoy = timezone.now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    bloques_semana = BloqueEstudio.objects.filter(
        usuario=usuario, 
        fecha__range=(inicio_semana, fin_semana),
        completado=True
    )
    bloques_estudio = bloques_semana.filter(tipo='estudio')
    total_estudio = bloques_estudio.count()
    tiempo_total = bloques_semana.aggregate(Sum('duracion_min'))['duracion_min__sum'] or 0
    print("Usuario:", usuario)
    print("Fecha:", hoy)
    print("Inicio semana:", inicio_semana)
    print("Fin semana:", fin_semana)
    print("Total bloques semana:", bloques_semana.count())
    print("Todos los bloques semana:", list(bloques_semana.values()))
    return JsonResponse({
        'bloques_estudio': total_estudio,
        'minutos_totales': tiempo_total,
    })

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import date
from .models import BloqueEstudio

@login_required
def productividad_api(request):
    usuario = request.user
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    bloques = BloqueEstudio.objects.filter(
        usuario=usuario,
        fecha__range=(inicio_semana, fin_semana),
        completado=True
    )
    eventos = Event.objects.filter(
        user=usuario,
        start_time__date__range=(inicio_semana, fin_semana),
        is_completed=True,
        event_type__in=['tarea', 'clase']
    )
    productividad_dias = [0] * 7
    meta_diaria = 120
    for dia in range(7):
        fecha_actual = inicio_semana + timedelta(days=dia)
        bloques_dia = [b for b in bloques if b.fecha == fecha_actual]
        minutos_bloques = sum(b.duracion_min for b in bloques_dia)
        eventos_dia = [e for e in eventos if e.start_time.date() == fecha_actual]
        minutos_eventos = sum(
            int((e.end_time - e.start_time).total_seconds() / 60)
            for e in eventos_dia
        )
        minutos_totales = minutos_bloques + minutos_eventos
        productividad_dias[dia] = min(100, int((minutos_totales / meta_diaria) * 100))
    return JsonResponse({
        "productividad_dias": productividad_dias,
        "dia_actual": hoy.weekday()
    })
