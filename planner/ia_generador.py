from datetime import datetime, timedelta, time 
from django.utils.timezone import make_aware
from .models import Event


def redondear_a_multiplo(tiempo, minutos=5):
    """Redondea hacia abajo al múltiplo de minutos más cercano."""
    return tiempo - timedelta(
        minutes=tiempo.minute % minutos,
        seconds=tiempo.second,
        microseconds=tiempo.microsecond
    )


def generar_bloques_enfocados_semana(user, duracion_enfoque=25, duracion_descanso=5, hora_inicio=time(6, 0), hora_fin=time(22, 0)):
    bloques = []
    hoy = datetime.now().date()

    for offset in range(7):
        dia = hoy + timedelta(days=offset)
        inicio_dia = make_aware(datetime.combine(dia, hora_inicio))
        fin_dia = make_aware(datetime.combine(dia, hora_fin))
        
        eventos = Event.objects.filter(user=user, start_time__date=dia).order_by("start_time")
        actual = inicio_dia

        for evento in eventos:
            tipo = evento.event_type.lower()
            inicio = evento.start_time
            fin = evento.end_time

            # Rellenar con descanso libre si hay hueco
            while actual < inicio:
                bloques.append({
                    "title": "Descanso libre",
                    "start_time": actual,
                    "end_time": min(inicio, actual + timedelta(minutes=30)),
                    "event_type": "descanso_libre"
                })
                actual += timedelta(minutes=30)

            if tipo in ["descanso", "descanso/ocio", "recreación"]:
                bloques.append({
                    "title": evento.title,
                    "start_time": inicio,
                    "end_time": fin,
                    "event_type": "descanso_real"
                })
                actual = fin
            elif tipo in ["tarea", "tarea/estudio", "estudio", "clase", "clase/academico"]:
                tiempo_actual = redondear_a_multiplo(inicio, minutos=5)
                while tiempo_actual + timedelta(minutes=duracion_enfoque) <= fin:
                    bloques.append({
                        "title": "Bloque de Estudio",
                        "start_time": tiempo_actual,
                        "end_time": tiempo_actual + timedelta(minutes=duracion_enfoque),
                        "event_type": "bloque_estudio"
                    })
                    tiempo_actual += timedelta(minutes=duracion_enfoque)

                    if tiempo_actual < fin:
                        descanso_fin = min(fin, tiempo_actual + timedelta(minutes=duracion_descanso))
                        bloques.append({
                            "title": "Descanso recomendado",
                            "start_time": tiempo_actual,
                            "end_time": descanso_fin,
                            "event_type": "descanso_recomendado"
                        })
                        tiempo_actual = descanso_fin

                actual = max(actual, fin)
            else:
                bloques.append({
                    "title": evento.title,
                    "start_time": inicio,
                    "end_time": fin,
                    "event_type": "otro"
                })
                actual = fin

        while actual < fin_dia:
            bloques.append({
                "title": "Descanso libre",
                "start_time": actual,
                "end_time": min(fin_dia, actual + timedelta(minutes=30)),
                "event_type": "descanso_libre"
            })
            actual += timedelta(minutes=30)

    return bloques