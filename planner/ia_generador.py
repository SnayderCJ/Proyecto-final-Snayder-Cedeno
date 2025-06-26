from datetime import datetime, timedelta, time 
from django.utils import timezone
from django.utils.timezone import make_aware
from .models import Event
import pytz
from core.models import UserSettings


def redondear_a_multiplo(tiempo, minutos=5):
    """Redondea hacia abajo al múltiplo de minutos más cercano."""
    return tiempo - timedelta(
        minutes=tiempo.minute % minutos,
        seconds=tiempo.second,
        microseconds=tiempo.microsecond
    )


def generar_bloques_enfocados_semana(user, duracion_enfoque=25, duracion_descanso=5, hora_inicio=time(6, 0), hora_fin=time(22, 0)):
    bloques = []
    hoy = timezone.now().date()

    # Obtener la zona horaria del usuario
    try:
        user_settings = UserSettings.objects.get(user=user)
        user_tz = pytz.timezone(user_settings.timezone)
    except (UserSettings.DoesNotExist, pytz.exceptions.UnknownTimeZoneError):
        user_tz = pytz.timezone('America/Guayaquil')

    for offset in range(7):
        dia = hoy + timedelta(days=offset)
        eventos = Event.objects.filter(user=user, start_time__date=dia).order_by("start_time")

        for evento in eventos:
            tipo = evento.event_type.lower()
            # Convertir los tiempos del evento a la zona horaria del usuario
            inicio = evento.start_time.astimezone(user_tz)
            fin = evento.end_time.astimezone(user_tz)

            if tipo in ["descanso", "descanso/ocio", "recreación"]:
                bloques.append({
                    "title": evento.title,
                    "start_time": inicio,
                    "end_time": fin,
                    "event_type": "descanso_real"
                })
            elif tipo in ["tarea", "tarea/estudio", "estudio", "clase", "clase/academico"]:
                # Mantener el tiempo original del evento
                tiempo_actual = inicio
                while tiempo_actual + timedelta(minutes=duracion_enfoque) <= fin:
                    bloques.append({
                        "title": f"{evento.title} - Bloque de Estudio",
                        "start_time": tiempo_actual,
                        "end_time": tiempo_actual + timedelta(minutes=duracion_enfoque),
                        "event_type": "bloque_estudio"
                    })
                    tiempo_actual += timedelta(minutes=duracion_enfoque)

                    # Solo agregar descanso si hay suficiente tiempo
                    tiempo_restante = (fin - tiempo_actual).total_seconds() / 60
                    if tiempo_actual < fin and tiempo_restante >= duracion_descanso:
                        descanso_fin = min(fin, tiempo_actual + timedelta(minutes=duracion_descanso))
                        bloques.append({
                            "title": f"Descanso - {evento.title}",
                            "start_time": tiempo_actual,
                            "end_time": descanso_fin,
                            "event_type": "descanso_recomendado"
                        })
                        tiempo_actual = descanso_fin
            else:
                bloques.append({
                    "title": evento.title,
                    "start_time": inicio,
                    "end_time": fin,
                    "event_type": "otro"
                })

    return bloques