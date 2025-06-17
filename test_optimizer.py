#!/usr/bin/env python3
"""
Script de prueba para el sistema de optimización de horarios con IA.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PLANIFICADOR_IA.settings')
sys.path.append('.')
django.setup()

from django.contrib.auth.models import User
from planner.models import Event
from planner.ai_optimizer import SmartScheduleOptimizer
from django.utils import timezone

def create_test_data():
    """Crear datos de prueba para el sistema."""
    print("🔧 Creando datos de prueba...")
    
    # Crear usuario de prueba si no existe
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Usuario',
            'last_name': 'Prueba'
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✅ Usuario de prueba creado: {user.username}")
    else:
        print(f"✅ Usuario de prueba encontrado: {user.username}")
    
    # Limpiar eventos existentes del usuario de prueba
    Event.objects.filter(user=user).delete()
    
    # Crear eventos de prueba
    today = timezone.localdate()
    events_data = [
        {
            'title': 'Matemáticas - Álgebra',
            'description': 'Estudiar ecuaciones lineales',
            'start_time': timezone.make_aware(datetime.combine(today, datetime.min.time().replace(hour=8))),
            'end_time': timezone.make_aware(datetime.combine(today, datetime.min.time().replace(hour=9))),
            'event_type': 'task',
            'priority': 'high',
        },
        {
            'title': 'Física - Mecánica',
            'description': 'Resolver problemas de cinemática',
            'start_time': timezone.make_aware(datetime.combine(today, datetime.min.time().replace(hour=14))),
            'end_time': timezone.make_aware(datetime.combine(today, datetime.min.time().replace(hour=15))),
            'event_type': 'task',
            'priority': 'medium',
        },
        {
            'title': 'Programación Python',
            'description': 'Práctica de algoritmos',
            'start_time': timezone.make_aware(datetime.combine(today + timedelta(days=1), datetime.min.time().replace(hour=16))),
            'end_time': timezone.make_aware(datetime.combine(today + timedelta(days=1), datetime.min.time().replace(hour=17))),
            'event_type': 'task',
            'priority': 'high',
        },
        {
            'title': 'Historia Universal',
            'description': 'Leer capítulo sobre la Revolución Francesa',
            'start_time': timezone.make_aware(datetime.combine(today + timedelta(days=2), datetime.min.time().replace(hour=20))),
            'end_time': timezone.make_aware(datetime.combine(today + timedelta(days=2), datetime.min.time().replace(hour=21))),
            'event_type': 'task',
            'priority': 'low',
        }
    ]
    
    created_events = []
    for event_data in events_data:
        event = Event.objects.create(user=user, **event_data)
        created_events.append(event)
        print(f"✅ Evento creado: {event.title} - {event.start_time}")
    
    return user, created_events

def test_optimizer():
    """Probar el sistema de optimización."""
    print("\n🤖 Probando el sistema de optimización...")
    
    # Crear datos de prueba
    user, events = create_test_data()
    
    # Inicializar el optimizador
    optimizer = SmartScheduleOptimizer()
    
    if not optimizer.is_loaded:
        print("⚠️  El modelo de IA no está cargado. Esto es normal en la primera ejecución.")
        print("   El sistema funcionará con reglas heurísticas básicas.")
    else:
        print("✅ Modelo de IA cargado correctamente.")
    
    # Obtener eventos para optimizar
    today = timezone.localdate()
    start_date = today
    end_date = today + timedelta(days=7)
    
    user_events = Event.objects.filter(
        user=user,
        start_time__date__gte=start_date,
        start_time__date__lte=end_date,
        is_completed=False
    )
    
    print(f"\n📊 Eventos a optimizar: {user_events.count()}")
    for event in user_events:
        print(f"   - {event.title}: {event.start_time.strftime('%Y-%m-%d %H:%M')}")
    
    # Ejecutar optimización
    print("\n🔄 Ejecutando optimización...")
    suggestions = optimizer.optimize_schedule(user_events, start_date, end_date)
    
    # Mostrar resultados
    print(f"\n📈 Resultados de optimización:")
    print(f"   Sugerencias generadas: {len(suggestions)}")
    
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n   Sugerencia {i}:")
            print(f"     📚 Evento: {suggestion['title']}")
            print(f"     ⏰ Horario actual: {suggestion['current_time']}")
            print(f"     ⏰ Horario sugerido: {suggestion['suggested_time']}")
            print(f"     📊 Mejora esperada: {suggestion['improvement_score']}%")
            print(f"     🎯 Confianza: {suggestion['confianza']:.2f}")
            print(f"     💡 Razón: {suggestion['reason']}")
    else:
        print("   ✅ No se encontraron optimizaciones necesarias.")
    
    return suggestions

def test_api_endpoint():
    """Probar el endpoint de la API."""
    print("\n🌐 Probando endpoint de API...")
    
    try:
        from django.test import Client
        from django.contrib.auth.models import User
        
        client = Client()
        user = User.objects.get(username='test_user')
        client.force_login(user)
        
        response = client.post('/planner/optimize/')
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Respuesta exitosa: {data.get('success', False)}")
            print(f"   Mensaje: {data.get('message', 'Sin mensaje')}")
            if 'suggestions' in data:
                print(f"   Sugerencias: {len(data['suggestions'])}")
        else:
            print(f"   Error en la respuesta: {response.content}")
            
    except Exception as e:
        print(f"   ❌ Error al probar API: {str(e)}")

def main():
    """Función principal."""
    print("🚀 Iniciando pruebas del sistema de optimización de horarios")
    print("=" * 60)
    
    try:
        # Probar el optimizador
        suggestions = test_optimizer()
        
        # Probar el endpoint de API
        test_api_endpoint()
        
        print("\n" + "=" * 60)
        print("✅ Pruebas completadas exitosamente!")
        
        if suggestions:
            print(f"🎉 El sistema generó {len(suggestions)} sugerencias de optimización.")
        else:
            print("ℹ️  No se generaron sugerencias (esto puede ser normal si los horarios ya están optimizados).")
            
        print("\n📝 Próximos pasos:")
        print("   1. Ejecuta el servidor Django: python manage.py runserver")
        print("   2. Ve a la página de horarios o tareas")
        print("   3. Haz clic en el botón '🤖 Optimizar Horario'")
        print("   4. Revisa las sugerencias generadas por la IA")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
