from datetime import datetime, timedelta

def generar_bloques_enfocados(inicio: datetime, fin: datetime, duracion_enfoque=25, duracion_descanso=5):
    bloques = []
    actual = inicio

    while actual + timedelta(minutes=duracion_enfoque) <= fin:
        inicio_estudio = actual
        fin_estudio = actual + timedelta(minutes=duracion_enfoque)
        bloques.append({
            'tipo': 'tarea',
            'titulo': 'Bloque de Estudio',
            'inicio': inicio_estudio,
            'fin': fin_estudio
        })
        actual = fin_estudio

        if actual + timedelta(minutes=duracion_descanso) <= fin:
            inicio_descanso = actual
            fin_descanso = actual + timedelta(minutes=duracion_descanso)
            bloques.append({
                'tipo': 'descanso',
                'titulo': 'Bloque de Descanso',
                'inicio': inicio_descanso,
                'fin': fin_descanso
            })
            actual = fin_descanso
        else:
            break

    return bloques
