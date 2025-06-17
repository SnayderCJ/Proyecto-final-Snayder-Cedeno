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

#-- vista nuevaaaaaa
from .optimizer import generar_bloques_enfocados
from django.utils.timezone import make_aware
from datetime import datetime, time


"""#@login_required
#def generar_bloques_view(request):
    
    #Vista que genera bloques de estudio y descanso para el usuario actual.
    
    if request.method == 'POST':
        hoy = datetime.now().date()
        inicio = make_aware(datetime.combine(hoy, time(8, 0)))  # 08:00 AM
        fin = make_aware(datetime.combine(hoy, time(12, 0)))    # 12:00 PM

        bloques = generar_bloques_enfocados(inicio, fin)

        messages.success(request, f'Se generaron {len(bloques)} bloques exitosamente.')
        return redirect('planner:horarios')

    return render(request, 'generar_bloques_confirm.html')"""



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, time, timedelta
from django.utils.timezone import localtime
from .ia_generador import generar_bloques_enfocados_semana
from collections import defaultdict

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
        bloque["start_time"] = localtime(bloque["start_time"]).replace(tzinfo=None)
        bloque["end_time"] = localtime(bloque["end_time"]).replace(tzinfo=None)
        bloque["hora_slot"] = bloque["start_time"].strftime("%H:%M")
        bloque["weekday"] = bloque["start_time"].weekday()

    # Rango de horas de la tabla
    horas = []
    actual = datetime.combine(datetime.now().date(), time(6, 0))
    final = datetime.combine(datetime.now().date(), time(22, 0))
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
from django.contrib.auth.decorators import login_required
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
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Sum
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
