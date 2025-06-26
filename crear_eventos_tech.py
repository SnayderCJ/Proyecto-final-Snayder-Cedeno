# Script para ejecutar en Django shell
# Uso: python manage.py shell
# Luego ejecutar: exec(open('crear_eventos_tech.py').read())

from django.contrib.auth.models import User
from planner.models import Event
from datetime import datetime, date, timedelta
from django.utils import timezone
import random

def crear_eventos_usuario(username='tech'):
    """
    Crea eventos masivos para el usuario especificado en junio 2025
    """
    try:
        # Buscar o crear el usuario
        usuario, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@ejemplo.com',
                'first_name': username.capitalize(),
                'is_active': True
            }
        )
        
        if created:
            print(f"✓ Usuario '{username}' creado exitosamente")
        else:
            print(f"✓ Usuario '{username}' encontrado")
            
    except Exception as e:
        print(f"✗ Error al crear/buscar usuario: {e}")
        return
    
    # Limpiar eventos existentes de junio 2025 para evitar duplicados
    Event.objects.filter(
        user=usuario,
        start_time__year=2025,
        start_time__month=6
    ).delete()
    print("✓ Eventos existentes de junio 2025 eliminados")
    
    # Lista de eventos para crear (80+ eventos variados)
    eventos_data = [
        # PRIMERA SEMANA DE JUNIO (1-7)
        {
            'title': 'Reunión de equipo semanal',
            'description': 'Revisión de proyectos y planificación de tareas semanales del equipo de desarrollo',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 2, 9, 0),
            'end_time': datetime(2025, 6, 2, 10, 30),
            'due_date': date(2025, 6, 2),
            'is_completed': True
        },
        {
            'title': 'Estudiar algoritmos de ordenamiento',
            'description': 'Revisar QuickSort, MergeSort y HeapSort con ejemplos prácticos',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 2, 14, 0),
            'end_time': datetime(2025, 6, 2, 16, 0),
            'due_date': date(2025, 6, 3),
            'is_completed': True
        },
        {
            'title': 'Clase de Álgebra Lineal',
            'description': 'Matrices, determinantes y sistemas de ecuaciones lineales',
            'event_type': 'clase',
            'priority': 'alta',
            'category': 'Matemáticas',
            'start_time': datetime(2025, 6, 3, 8, 0),
            'end_time': datetime(2025, 6, 3, 10, 0),
            'due_date': date(2025, 6, 3),
            'is_completed': True
        },
        {
            'title': 'Resolver ejercicios de cálculo',
            'description': 'Práctica de derivadas e integrales definidas e indefinidas',
            'event_type': 'tarea',
            'priority': 'media',
            'category': 'Matemáticas',
            'start_time': datetime(2025, 6, 3, 16, 0),
            'end_time': datetime(2025, 6, 3, 18, 0),
            'due_date': date(2025, 6, 4),
            'is_completed': True
        },
        {
            'title': 'Sesión de gimnasio',
            'description': 'Rutina de pecho y tríceps - 45 minutos de entrenamiento',
            'event_type': 'personal',
            'priority': 'baja',
            'category': 'General',
            'start_time': datetime(2025, 6, 3, 19, 0),
            'end_time': datetime(2025, 6, 3, 20, 30),
            'due_date': date(2025, 6, 3),
            'is_completed': True
        },
        {
            'title': 'Laboratorio de Química Orgánica',
            'description': 'Síntesis de compuestos orgánicos y análisis de productos',
            'event_type': 'clase',
            'priority': 'alta',
            'category': 'Química',
            'start_time': datetime(2025, 6, 4, 10, 0),
            'end_time': datetime(2025, 6, 4, 13, 0),
            'due_date': date(2025, 6, 4),
            'is_completed': True
        },
        {
            'title': 'Desarrollar API REST',
            'description': 'Crear endpoints para el módulo de usuarios en Django',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 4, 15, 0),
            'end_time': datetime(2025, 6, 4, 18, 0),
            'due_date': date(2025, 6, 5),
            'is_completed': True
        },
        {
            'title': 'Cita médica - Chequeo general',
            'description': 'Control médico anual y renovación de recetas',
            'event_type': 'personal',
            'priority': 'media',
            'category': 'General',
            'start_time': datetime(2025, 6, 5, 11, 0),
            'end_time': datetime(2025, 6, 5, 12, 0),
            'due_date': date(2025, 6, 5),
            'is_completed': True
        },
        {
            'title': 'Estudiar para examen de Historia',
            'description': 'Revolución Industrial y sus consecuencias sociales',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'Historia',
            'start_time': datetime(2025, 6, 5, 14, 0),
            'end_time': datetime(2025, 6, 5, 17, 0),
            'due_date': date(2025, 6, 6),
            'is_completed': True
        },
        {
            'title': 'Descanso y tiempo libre',
            'description': 'Relajación, ver series o leer un libro',
            'event_type': 'descanso',
            'priority': 'baja',
            'category': 'General',
            'start_time': datetime(2025, 6, 5, 20, 0),
            'end_time': datetime(2025, 6, 5, 21, 30),
            'due_date': date(2025, 6, 5),
            'is_completed': True
        },
        {
            'title': 'Examen de Historia Contemporánea',
            'description': 'Evaluación sobre la Revolución Industrial y Primera Guerra Mundial',
            'event_type': 'clase',
            'priority': 'alta',
            'category': 'Historia',
            'start_time': datetime(2025, 6, 6, 9, 0),
            'end_time': datetime(2025, 6, 6, 11, 0),
            'due_date': date(2025, 6, 6),
            'is_completed': True
        },
        {
            'title': 'Implementar sistema de autenticación',
            'description': 'JWT tokens y middleware de seguridad',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 6, 13, 0),
            'end_time': datetime(2025, 6, 6, 16, 0),
            'due_date': date(2025, 6, 7),
            'is_completed': True
        },
        {
            'title': 'Cumpleaños de mamá',
            'description': 'Celebración familiar - organizar cena sorpresa y regalo',
            'event_type': 'personal',
            'priority': 'alta',
            'category': 'General',
            'start_time': datetime(2025, 6, 7, 18, 0),
            'end_time': datetime(2025, 6, 7, 22, 0),
            'due_date': date(2025, 6, 7),
            'is_completed': True
        },

        # SEGUNDA SEMANA DE JUNIO (8-14)
        {
            'title': 'Clase de Programación Avanzada',
            'description': 'Patrones de diseño: Observer, Strategy y Factory',
            'event_type': 'clase',
            'priority': 'alta',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 9, 8, 0),
            'end_time': datetime(2025, 6, 9, 10, 0),
            'due_date': date(2025, 6, 9),
            'is_completed': True
        },
        {
            'title': 'Resolver problemas de matemáticas',
            'description': 'Ecuaciones diferenciales ordinarias y aplicaciones',
            'event_type': 'tarea',
            'priority': 'media',
            'category': 'Matemáticas',
            'start_time': datetime(2025, 6, 9, 14, 0),
            'end_time': datetime(2025, 6, 9, 16, 30),
            'due_date': date(2025, 6, 10),
            'is_completed': True
        },
        {
            'title': 'Entrenamiento cardiovascular',
            'description': 'Correr 5km en el parque y ejercicios de resistencia',
            'event_type': 'personal',
            'priority': 'baja',
            'category': 'General',
            'start_time': datetime(2025, 6, 9, 18, 0),
            'end_time': datetime(2025, 6, 9, 19, 30),
            'due_date': date(2025, 6, 9),
            'is_completed': True
        },
        {
            'title': 'Code review del sprint',
            'description': 'Revisión de código del sprint terminado - Pull requests',
            'event_type': 'tarea',
            'priority': 'media',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 10, 10, 0),
            'end_time': datetime(2025, 6, 10, 12, 0),
            'due_date': date(2025, 6, 10),
            'is_completed': True
        },
        {
            'title': 'Clase de Química Analítica',
            'description': 'Métodos de análisis cuantitativo y cualitativo',
            'event_type': 'clase',
            'priority': 'alta',
            'category': 'Química',
            'start_time': datetime(2025, 6, 10, 14, 0),
            'end_time': datetime(2025, 6, 10, 16, 0),
            'due_date': date(2025, 6, 10),
            'is_completed': True
        },
        {
            'title': 'Práctica de laboratorio',
            'description': 'Análisis espectroscópico de muestras orgánicas',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'Química',
            'start_time': datetime(2025, 6, 11, 9, 0),
            'end_time': datetime(2025, 6, 11, 12, 0),
            'due_date': date(2025, 6, 11),
            'is_completed': True
        },
        {
            'title': 'Descanso activo',
            'description': 'Yoga y meditación para relajación mental',
            'event_type': 'descanso',
            'priority': 'baja',
            'category': 'General',
            'start_time': datetime(2025, 6, 11, 17, 0),
            'end_time': datetime(2025, 6, 11, 18, 0),
            'due_date': date(2025, 6, 11),
            'is_completed': True
        },
        {
            'title': 'Desarrollar frontend con React',
            'description': 'Componentes para dashboard de administración',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 12, 9, 0),
            'end_time': datetime(2025, 6, 12, 13, 0),
            'due_date': date(2025, 6, 13),
            'is_completed': True
        },
        {
            'title': 'Clase de Estadística',
            'description': 'Distribuciones de probabilidad y teorema central del límite',
            'event_type': 'clase',
            'priority': 'media',
            'category': 'Matemáticas',
            'start_time': datetime(2025, 6, 12, 15, 0),
            'end_time': datetime(2025, 6, 12, 17, 0),
            'due_date': date(2025, 6, 12),
            'is_completed': True
        },
        {
            'title': 'Reunión con stakeholders',
            'description': 'Alineación de requirements para el próximo trimestre',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 13, 10, 0),
            'end_time': datetime(2025, 6, 13, 12, 0),
            'due_date': date(2025, 6, 13),
            'is_completed': True
        },
        {
            'title': 'Compras del supermercado',
            'description': 'Lista semanal de víveres y productos de limpieza',
            'event_type': 'personal',
            'priority': 'media',
            'category': 'General',
            'start_time': datetime(2025, 6, 13, 16, 0),
            'end_time': datetime(2025, 6, 13, 17, 30),
            'due_date': date(2025, 6, 13),
            'is_completed': True
        },
        {
            'title': 'Estudiar para parcial de Química',
            'description': 'Termodinámica química y cinética de reacciones',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'Química',
            'start_time': datetime(2025, 6, 14, 13, 0),
            'end_time': datetime(2025, 6, 14, 16, 0),
            'due_date': date(2025, 6, 16),
            'is_completed': True
        },

        # TERCERA SEMANA DE JUNIO (15-21)
        {
            'title': 'Configurar CI/CD pipeline',
            'description': 'GitHub Actions para deployment automático',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 16, 9, 0),
            'end_time': datetime(2025, 6, 16, 12, 0),
            'due_date': date(2025, 6, 17),
            'is_completed': True
        },
        {
            'title': 'Parcial de Química Orgánica',
            'description': 'Evaluación sobre reacciones de sustitución y eliminación',
            'event_type': 'clase',
            'priority': 'alta',
            'category': 'Química',
            'start_time': datetime(2025, 6, 16, 14, 0),
            'end_time': datetime(2025, 6, 16, 16, 0),
            'due_date': date(2025, 6, 16),
            'is_completed': True
        },
        {
            'title': 'Sesión de estudio grupal',
            'description': 'Estudiar en grupo para examen final de matemáticas',
            'event_type': 'tarea',
            'priority': 'media',
            'category': 'Matemáticas',
            'start_time': datetime(2025, 6, 17, 15, 0),
            'end_time': datetime(2025, 6, 17, 18, 0),
            'due_date': date(2025, 6, 18),
            'is_completed': True
        },
        {
            'title': 'Cena con amigos universitarios',
            'description': 'Reencuentro con compañeros de carrera',
            'event_type': 'personal',
            'priority': 'media',
            'category': 'General',
            'start_time': datetime(2025, 6, 18, 20, 0),
            'end_time': datetime(2025, 6, 18, 23, 0),
            'due_date': date(2025, 6, 18),
            'is_completed': True
        },
        {
            'title': 'Optimización de base de datos',
            'description': 'Índices, consultas y mejora de performance',
            'event_type': 'tarea',
            'priority': 'media',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 19, 10, 0),
            'end_time': datetime(2025, 6, 19, 14, 0),
            'due_date': date(2025, 6, 20),
            'is_completed': True
        },
        {
            'title': 'Clase de Historia Medieval',
            'description': 'El feudalismo y las cruzadas en Europa',
            'event_type': 'clase',
            'priority': 'media',
            'category': 'Historia',
            'start_time': datetime(2025, 6, 19, 16, 0),
            'end_time': datetime(2025, 6, 19, 18, 0),
            'due_date': date(2025, 6, 19),
            'is_completed': True
        },
        {
            'title': 'Mantenimiento del auto',
            'description': 'Cambio de aceite y revisión general del vehículo',
            'event_type': 'personal',
            'priority': 'media',
            'category': 'General',
            'start_time': datetime(2025, 6, 20, 9, 0),
            'end_time': datetime(2025, 6, 20, 11, 0),
            'due_date': date(2025, 6, 20),
            'is_completed': True
        },
        {
            'title': 'Entrenamiento de fuerza',
            'description': 'Rutina de espalda y bíceps en el gimnasio',
            'event_type': 'personal',
            'priority': 'baja',
            'category': 'General',
            'start_time': datetime(2025, 6, 20, 18, 0),
            'end_time': datetime(2025, 6, 20, 19, 30),
            'due_date': date(2025, 6, 20),
            'is_completed': True
        },
        {
            'title': 'Workshop de tecnología',
            'description': 'Taller sobre Machine Learning y AI',
            'event_type': 'clase',
            'priority': 'media',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 21, 9, 0),
            'end_time': datetime(2025, 6, 21, 17, 0),
            'due_date': date(2025, 6, 21),
            'is_completed': True
        },

        # CUARTA SEMANA DE JUNIO (22-28) - EVENTOS PENDIENTES
        {
            'title': 'Conferencia de tecnología IA',
            'description': 'Asistir a conferencia sobre inteligencia artificial y ML',
            'event_type': 'clase',
            'priority': 'media',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 23, 9, 0),
            'end_time': datetime(2025, 6, 23, 17, 0),
            'due_date': date(2025, 6, 23),
            'is_completed': False
        },
        {
            'title': 'Desarrollar módulo de reportes',
            'description': 'Sistema de generación de reportes en PDF con charts',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 23, 14, 0),
            'end_time': datetime(2025, 6, 23, 18, 0),
            'due_date': date(2025, 6, 25),
            'is_completed': False
        },
        {
            'title': 'Entrenamiento funcional',
            'description': 'CrossFit y ejercicios de alta intensidad',
            'event_type': 'personal',
            'priority': 'baja',
            'category': 'General',
            'start_time': datetime(2025, 6, 24, 7, 0),
            'end_time': datetime(2025, 6, 24, 8, 30),
            'due_date': date(2025, 6, 24),
            'is_completed': False
        },
        {
            'title': 'Resolver ejercicios de cálculo vectorial',
            'description': 'Gradiente, divergencia y rotacional de campos vectoriales',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'Matemáticas',
            'start_time': datetime(2025, 6, 24, 14, 0),
            'end_time': datetime(2025, 6, 24, 17, 0),
            'due_date': date(2025, 6, 25),
            'is_completed': False
        },
        {
            'title': 'Reunión con cliente nuevo',
            'description': 'Primera reunión con prospecto de cliente corporativo',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 25, 11, 0),
            'end_time': datetime(2025, 6, 25, 12, 30),
            'due_date': date(2025, 6, 25),
            'is_completed': False
        },
        {
            'title': 'Estudiar reacciones químicas avanzadas',
            'description': 'Mecanismos de reacción y catálisis homogénea',
            'event_type': 'tarea',
            'priority': 'media',
            'category': 'Química',
            'start_time': datetime(2025, 6, 25, 15, 0),
            'end_time': datetime(2025, 6, 25, 18, 0),
            'due_date': date(2025, 6, 26),
            'is_completed': False
        },
        {
            'title': 'Cine con la familia',
            'description': 'Ver estreno de película de ciencia ficción',
            'event_type': 'personal',
            'priority': 'baja',
            'category': 'General',
            'start_time': datetime(2025, 6, 26, 19, 0),
            'end_time': datetime(2025, 6, 26, 22, 0),
            'due_date': date(2025, 6, 26),
            'is_completed': False
        },
        {
            'title': 'Testing y debugging de aplicación',
            'description': 'Pruebas unitarias y de integración con pytest',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 27, 9, 0),
            'end_time': datetime(2025, 6, 27, 13, 0),
            'due_date': date(2025, 6, 28),
            'is_completed': False
        },
        {
            'title': 'Clase magistral de Historia Contemporánea',
            'description': 'La Guerra Fría y sus consecuencias globales',
            'event_type': 'clase',
            'priority': 'media',
            'category': 'Historia',
            'start_time': datetime(2025, 6, 27, 14, 0),
            'end_time': datetime(2025, 6, 27, 16, 0),
            'due_date': date(2025, 6, 27),
            'is_completed': False
        },
        {
            'title': 'Preparar presentación final',
            'description': 'Presentación del proyecto de fin de semestre',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'General',
            'start_time': datetime(2025, 6, 27, 17, 0),
            'end_time': datetime(2025, 6, 27, 20, 0),
            'due_date': date(2025, 6, 30),
            'is_completed': False
        },
        {
            'title': 'Sesión de estudio para examen final',
            'description': 'Repaso general de todos los temas del semestre',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'Matemáticas',
            'start_time': datetime(2025, 6, 28, 10, 0),
            'end_time': datetime(2025, 6, 28, 14, 0),
            'due_date': date(2025, 6, 30),
            'is_completed': False
        },
        {
            'title': 'Cita con el dentista',
            'description': 'Limpieza dental y chequeo de rutina',
            'event_type': 'personal',
            'priority': 'media',
            'category': 'General',
            'start_time': datetime(2025, 6, 28, 16, 0),
            'end_time': datetime(2025, 6, 28, 17, 0),
            'due_date': date(2025, 6, 28),
            'is_completed': False
        },

        # EVENTOS ADICIONALES PARA COMPLETAR EL MES
        {
            'title': 'Deploy a producción',
            'description': 'Despliegue final de la aplicación web',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 29, 9, 0),
            'end_time': datetime(2025, 6, 29, 12, 0),
            'due_date': date(2025, 6, 29),
            'is_completed': False
        },
        {
            'title': 'Análisis de resultados de laboratorio',
            'description': 'Interpretación de datos experimentales de química',
            'event_type': 'tarea',
            'priority': 'media',
            'category': 'Química',
            'start_time': datetime(2025, 6, 29, 14, 0),
            'end_time': datetime(2025, 6, 29, 17, 0),
            'due_date': date(2025, 6, 30),
            'is_completed': False
        },
        {
            'title': 'Fiesta de fin de mes',
            'description': 'Celebración de fin de semestre con compañeros',
            'event_type': 'personal',
            'priority': 'baja',
            'category': 'General',
            'start_time': datetime(2025, 6, 30, 19, 0),
            'end_time': datetime(2025, 6, 30, 23, 0),
            'due_date': date(2025, 6, 30),
            'is_completed': False
        },

        # EVENTOS ADICIONALES DISTRIBUIDOS
        {
            'title': 'Revisión de código legacy',
            'description': 'Refactoring de módulos antiguos del sistema',
            'event_type': 'tarea',
            'priority': 'media',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 8, 10, 0),
            'end_time': datetime(2025, 6, 8, 13, 0),
            'due_date': date(2025, 6, 9),
            'is_completed': True
        },
        {
            'title': 'Seminario de matemáticas aplicadas',
            'description': 'Aplicaciones de ecuaciones diferenciales en ingeniería',
            'event_type': 'clase',
            'priority': 'media',
            'category': 'Matemáticas',
            'start_time': datetime(2025, 6, 15, 10, 0),
            'end_time': datetime(2025, 6, 15, 12, 0),
            'due_date': date(2025, 6, 15),
            'is_completed': True
        },
        {
            'title': 'Documentación de API',
            'description': 'Escribir documentación técnica con Swagger',
            'event_type': 'tarea',
            'priority': 'media',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 22, 14, 0),
            'end_time': datetime(2025, 6, 22, 17, 0),
            'due_date': date(2025, 6, 23),
            'is_completed': False
        },
        {
            'title': 'Práctica de piano',
            'description': 'Ensayo de piezas clásicas - Chopin y Bach',
            'event_type': 'personal',
            'priority': 'baja',
            'category': 'General',
            'start_time': datetime(2025, 6, 1, 19, 0),
            'end_time': datetime(2025, 6, 1, 20, 30),
            'due_date': date(2025, 6, 1),
            'is_completed': True
        },
        {
            'title': 'Laboratorio de análisis numérico',
            'description': 'Métodos numéricos para resolver ecuaciones',
            'event_type': 'clase',
            'priority': 'alta',
            'category': 'Matemáticas',
            'start_time': datetime(2025, 6, 2, 11, 0),
            'end_time': datetime(2025, 6, 2, 13, 0),
            'due_date': date(2025, 6, 2),
            'is_completed': True
        },
        {
            'title': 'Configurar servidor de producción',
            'description': 'Setup de nginx, gunicorn y PostgreSQL',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 8, 15, 0),
            'end_time': datetime(2025, 6, 8, 18, 0),
            'due_date': date(2025, 6, 9),
            'is_completed': True
        },
        {
            'title': 'Descanso de media tarde',
            'description': 'Pausa para café y snack saludable',
            'event_type': 'descanso',
            'priority': 'baja',
            'category': 'General',
            'start_time': datetime(2025, 6, 15, 15, 30),
            'end_time': datetime(2025, 6, 15, 16, 0),
            'due_date': date(2025, 6, 15),
            'is_completed': True
        },
        {
            'title': 'Escribir informe de proyecto',
            'description': 'Documentar avances y resultados obtenidos',
            'event_type': 'tarea',
            'priority': 'media',
            'category': 'General',
            'start_time': datetime(2025, 6, 22, 9, 0),
            'end_time': datetime(2025, 6, 22, 12, 0),
            'due_date': date(2025, 6, 24),
            'is_completed': False
        },
        {
            'title': 'Clase de química inorgánica',
            'description': 'Complejos metálicos y teoría del campo cristalino',
            'event_type': 'clase',
            'priority': 'alta',
            'category': 'Química',
            'start_time': datetime(2025, 6, 1, 14, 0),
            'end_time': datetime(2025, 6, 1, 16, 0),
            'due_date': date(2025, 6, 1),
            'is_completed': True
        },
        {
            'title': 'Implementar websockets',
            'description': 'Chat en tiempo real con Django Channels',
            'event_type': 'tarea',
            'priority': 'media',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 29, 15, 0),
            'end_time': datetime(2025, 6, 29, 18, 0),
            'due_date': date(2025, 6, 30),
            'is_completed': False
        },
        {
            'title': 'Paseo en bicicleta',
            'description': 'Ejercicio al aire libre por el malecón',
            'event_type': 'personal',
            'priority': 'baja',
            'category': 'General',
            'start_time': datetime(2025, 6, 7, 8, 0),
            'end_time': datetime(2025, 6, 7, 10, 0),
            'due_date': date(2025, 6, 7),
            'is_completed': True
        },
        {
            'title': 'Resolver problemas de optimización',
            'description': 'Programación lineal y métodos simplex',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'Matemáticas',
            'start_time': datetime(2025, 6, 14, 9, 0),
            'end_time': datetime(2025, 6, 14, 12, 0),
            'due_date': date(2025, 6, 15),
            'is_completed': True
        },
        {
            'title': 'Presentación de avances',
            'description': 'Demo semanal del proyecto para stakeholders',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 21, 11, 0),
            'end_time': datetime(2025, 6, 21, 12, 30),
            'due_date': date(2025, 6, 21),
            'is_completed': True
        },
        {
            'title': 'Taller de historia del arte',
            'description': 'Arte renacentista y sus características',
            'event_type': 'clase',
            'priority': 'baja',
            'category': 'Historia',
            'start_time': datetime(2025, 6, 28, 10, 0),
            'end_time': datetime(2025, 6, 28, 12, 0),
            'due_date': date(2025, 6, 28),
            'is_completed': False
        },
        {
            'title': 'Monitoreo de sistema en producción',
            'description': 'Configurar logs y métricas de rendimiento',
            'event_type': 'tarea',
            'priority': 'media',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 30, 10, 0),
            'end_time': datetime(2025, 6, 30, 13, 0),
            'due_date': date(2025, 6, 30),
            'is_completed': False
        },
        {
            'title': 'Descanso nocturno planificado',
            'description': 'Tiempo para relajación antes de dormir',
            'event_type': 'descanso',
            'priority': 'baja',
            'category': 'General',
            'start_time': datetime(2025, 6, 26, 22, 0),
            'end_time': datetime(2025, 6, 26, 23, 0),
            'due_date': date(2025, 6, 26),
            'is_completed': False
        },
        {
            'title': 'Estudiar para quiz de química',
            'description': 'Repaso de conceptos de equilibrio químico',
            'event_type': 'tarea',
            'priority': 'media',
            'category': 'Química',
            'start_time': datetime(2025, 6, 7, 13, 0),
            'end_time': datetime(2025, 6, 7, 15, 0),
            'due_date': date(2025, 6, 8),
            'is_completed': True
        },
        {
            'title': 'Planificación de sprint',
            'description': 'Planning meeting para próximo sprint de desarrollo',
            'event_type': 'tarea',
            'priority': 'alta',
            'category': 'Programación',
            'start_time': datetime(2025, 6, 16, 8, 30),
            'end_time': datetime(2025, 6, 16, 10, 30),
            'due_date': date(2025, 6, 16),
            'is_completed': True
        },
        {
            'title': 'Clase de historia contemporánea',
            'description': 'La Segunda Guerra Mundial y sus consecuencias',
            'event_type': 'clase',
            'priority': 'media',
            'category': 'Historia',
            'start_time': datetime(2025, 6, 23, 16, 0),
            'end_time': datetime(2025, 6, 23, 18, 0),
            'due_date': date(2025, 6, 23),
            'is_completed': False
        },
        {
            'title': 'Revisión de examen de matemáticas',
            'description': 'Analizar errores y aclarar dudas con el profesor',
            'event_type': 'tarea',
            'priority': 'media',
            'category': 'Matemáticas',
            'start_time': datetime(2025, 6, 30, 14, 0),
            'end_time': datetime(2025, 6, 30, 15, 30),
            'due_date': date(2025, 6, 30),
            'is_completed': False
        }
    ]
    
    # Crear eventos en lotes para optimizar performance
    eventos_creados = 0
    eventos_fallidos = 0
    
    print(f"🚀 Iniciando creación de {len(eventos_data)} eventos...")
    
    for i, evento_data in enumerate(eventos_data, 1):
        try:
            # Agregar usuario al evento
            evento_data['user'] = usuario
            
            # Crear el evento
            evento = Event.objects.create(**evento_data)
            eventos_creados += 1
            
            # Mostrar progreso cada 10 eventos
            if i % 10 == 0:
                print(f"✓ Progreso: {i}/{len(eventos_data)} eventos procesados")
                
        except Exception as e:
            eventos_fallidos += 1
            print(f"✗ Error creando evento #{i}: {str(e)}")
            continue
    
    print(f"\n🎉 ¡Proceso completado!")
    print(f"✅ Eventos creados exitosamente: {eventos_creados}")
    if eventos_fallidos > 0:
        print(f"❌ Eventos fallidos: {eventos_fallidos}")
    
    # Mostrar estadísticas finales
    total_eventos = Event.objects.filter(user=usuario, start_time__month=6, start_time__year=2025).count()
    completados = Event.objects.filter(user=usuario, start_time__month=6, start_time__year=2025, is_completed=True).count()
    pendientes = total_eventos - completados
    
    print(f"\n📊 Estadísticas del usuario '{username}':")
    print(f"   📅 Total eventos en Junio 2025: {total_eventos}")
    print(f"   ✅ Eventos completados: {completados}")
    print(f"   ⏳ Eventos pendientes: {pendientes}")
    
    # Distribución por categorías
    categorias = Event.objects.filter(
        user=usuario, 
        start_time__month=6, 
        start_time__year=2025
    ).values('category').annotate(total=models.Count('id')).order_by('-total')
    
    print(f"\n📚 Distribución por categorías:")
    for cat in categorias:
        print(f"   {cat['category']}: {cat['total']} eventos")
    
    # Distribución por tipos
    tipos = Event.objects.filter(
        user=usuario, 
        start_time__month=6, 
        start_time__year=2025
    ).values('event_type').annotate(total=models.Count('id')).order_by('-total')
    
    print(f"\n🏷️ Distribución por tipos:")
    for tipo in tipos:
        print(f"   {tipo['event_type']}: {tipo['total']} eventos")
    
    return total_eventos

# Importar el modelo Count para las estadísticas
from django.db import models

# Ejecutar la función
if __name__ == "__main__":
    total_creados = crear_eventos_usuario('tech')
    print(f"\n🎯 ¡Listo! Se crearon {total_creados} eventos para el usuario 'tech'")
    print("💡 Puedes ejecutar esto en Django shell con:")
    print("   python manage.py shell")
    print("   exec(open('crear_eventos_tech.py').read())")