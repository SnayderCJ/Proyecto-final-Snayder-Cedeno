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

# Limpiar tareas existentes
Event.objects.filter(user=user).delete()

# Crear tareas para diferentes semanas
def create_test_tasks():
    # Semana actual (15 de junio)
    Event.objects.create(
        user=user,
        title="Tarea Semana Actual 1",
        event_type="task",
        priority="high",
        start_time=timezone.now(),
        end_time=timezone.now() + timedelta(hours=2),
        is_completed=False
    )
    
    # Próxima semana (23-29 junio)
    Event.objects.create(
        user=user,
        title="Tarea Próxima Semana",
        event_type="task",
        priority="medium",
        start_time=timezone.now() + timedelta(days=8),
        end_time=timezone.now() + timedelta(days=8, hours=2),
        is_completed=False
    )
    
    # Semana pasada
    Event.objects.create(
        user=user,
        title="Tarea Semana Pasada",
        event_type="task",
        priority="low",
        start_time=timezone.now() - timedelta(days=7),
        end_time=timezone.now() - timedelta(days=7, hours=2),
        is_completed=False
    )
    
    print("Tareas de prueba creadas exitosamente")

create_test_tasks()
