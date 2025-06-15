import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PLANIFICADOR_IA.settings')
django.setup()

from django.contrib.auth.models import User
from planner.models import Event

try:
    user = User.objects.get(username='testuser')
    
    # Crear algunas tareas de prueba
    tasks = [
        {
            'title': 'Estudiar Matemáticas',
            'event_type': 'study',
            'priority': 'high',
            'is_completed': False
        },
        {
            'title': 'Proyecto de Programación',
            'event_type': 'project',
            'priority': 'medium',
            'is_completed': False
        },
        {
            'title': 'Leer capítulo de Física',
            'event_type': 'study',
            'priority': 'low',
            'is_completed': True
        }
    ]
    
    for task_data in tasks:
        Event.objects.create(
            user=user,
            title=task_data['title'],
            event_type=task_data['event_type'],
            priority=task_data['priority'],
            start_time=datetime.now() + timedelta(hours=1),
            end_time=datetime.now() + timedelta(hours=2),
            is_completed=task_data['is_completed']
        )
    
    print('Tareas de prueba creadas exitosamente')
    
except Exception as e:
    print(f'Error: {e}')
