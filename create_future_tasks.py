import os
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PLANIFICADOR_IA.settings')
django.setup()

from django.contrib.auth.models import User
from planner.models import Event
from django.utils import timezone

# Obtener el usuario de prueba
user = User.objects.get(username='testuser')

# Crear tareas futuras (no completadas)
future_tasks = [
    {
        'title': 'Examen de Matemáticas',
        'event_type': 'exam',
        'priority': 'high',
        'start_time': timezone.now() + timedelta(days=1, hours=2),  # Mañana
        'end_time': timezone.now() + timedelta(days=1, hours=4),
        'is_completed': False
    },
    {
        'title': 'Entrega de Proyecto Final',
        'event_type': 'assignment',
        'priority': 'high',
        'start_time': timezone.now() + timedelta(days=3, hours=10),  # En 3 días
        'end_time': timezone.now() + timedelta(days=3, hours=12),
        'is_completed': False
    },
    {
        'title': 'Presentación Grupal',
        'event_type': 'presentation',
        'priority': 'medium',
        'start_time': timezone.now() + timedelta(days=5, hours=14),  # En 5 días
        'end_time': timezone.now() + timedelta(days=5, hours=16),
        'is_completed': False
    },
    {
        'title': 'Laboratorio de Química',
        'event_type': 'lab',
        'priority': 'medium',
        'start_time': timezone.now() + timedelta(days=7, hours=9),  # En una semana
        'end_time': timezone.now() + timedelta(days=7, hours=11),
        'is_completed': False
    },
    {
        'title': 'Tarea de Programación',
        'event_type': 'assignment',
        'priority': 'low',
        'start_time': timezone.now() + timedelta(days=10, hours=16),  # En 10 días
        'end_time': timezone.now() + timedelta(days=10, hours=18),
        'is_completed': False
    }
]

# Crear las tareas
for task_data in future_tasks:
    Event.objects.create(
        user=user,
        **task_data
    )

print("Tareas futuras creadas exitosamente")
