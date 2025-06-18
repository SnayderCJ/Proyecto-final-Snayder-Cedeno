import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
import joblib
import os
import json
from django.conf import settings

class SmartScheduleOptimizer:
    """
    Optimizador inteligente de horarios para estudiantes usando Machine Learning.
    Compatible con el modelo entrenado en Google Colab.
    """
    
    def __init__(self, model_path=None):
        """
        Inicializa el optimizador con el modelo pre-entrenado.
        
        Args:
            model_path (str): Ruta al directorio que contiene los archivos del modelo
        """
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), 'trained_models')
        
        self.model_path = model_path
        self.model = None
        self.encoders = None
        self.scaler = None
        self.metadata = None
        self.is_loaded = False
        
        # Intentar cargar el modelo automáticamente
        self.load_model()
    
    def load_model(self):
        """Carga el modelo y preprocesadores desde archivos .joblib"""
        try:
            model_file = os.path.join(self.model_path, 'smart_scheduler_model.joblib')
            encoders_file = os.path.join(self.model_path, 'smart_scheduler_encoders.joblib')
            scaler_file = os.path.join(self.model_path, 'smart_scheduler_scaler.joblib')
            metadata_file = os.path.join(self.model_path, 'smart_scheduler_metadata.json')
            
            if all(os.path.exists(f) for f in [model_file, encoders_file, scaler_file]):
                self.model = joblib.load(model_file)
                self.encoders = joblib.load(encoders_file)
                self.scaler = joblib.load(scaler_file)
                
                # Cargar metadatos si existe
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r') as f:
                        self.metadata = json.load(f)
                
                self.is_loaded = True
                print(f"✅ Modelo cargado exitosamente desde {self.model_path}")
                
                if self.metadata:
                    print(f"📊 Versión del modelo: {self.metadata.get('version', 'N/A')}")
                    print(f"📅 Entrenado el: {self.metadata.get('trained_date', 'N/A')}")
                
            else:
                print(f"❌ No se encontraron todos los archivos del modelo en {self.model_path}")
                self.is_loaded = False
                
        except Exception as e:
            print(f"❌ Error al cargar el modelo: {str(e)}")
            self.is_loaded = False
    
    def validate_event_data(self, event_data):
        """Valida que los datos del evento sean correctos"""
        required_fields = ['event_type', 'priority', 'duration', 'weekday']
        for field in required_fields:
            if field not in event_data:
                raise ValueError(f"Campo requerido faltante: {field}")
        
        # Validar tipos de eventos compatibles con Django
        valid_event_types = ["tarea", "clase", "examen", "proyecto", "estudio", "descanso", "personal", "otro"]
        if event_data['event_type'] not in valid_event_types:
            raise ValueError(f"Tipo de evento no válido: {event_data['event_type']}")
        
        # Validar prioridades compatibles con Django
        valid_priorities = ["alta", "media", "baja"]
        if event_data['priority'] not in valid_priorities:
            raise ValueError(f"Prioridad no válida: {event_data['priority']}")
        
        return True

    def process_due_date(self, due_date, start_date=None):
        """Procesa fechas de vencimiento de manera flexible"""
        if not due_date:
            return None, 999
        
        if start_date is None:
            start_date = datetime.now().date()
        elif isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        elif isinstance(start_date, datetime):
            start_date = start_date.date()
        
        if isinstance(due_date, str):
            try:
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            except ValueError:
                try:
                    due_date = datetime.strptime(due_date, '%Y-%m-%dT%H:%M:%S').date()
                except ValueError:
                    return None, 999
        elif isinstance(due_date, datetime):
            due_date = due_date.date()
        
        days_to_deadline = (due_date - start_date).days
        return due_date, max(0, days_to_deadline)

    def transform_data(self, df):
        """Preprocesa los datos para el modelo"""
        if not self.is_loaded:
            raise ValueError("El modelo no está cargado. Verifica los archivos del modelo.")
        
        df = df.copy()
        
        # Transformar usando los encoders cargados
        df['event_type_encoded'] = self.encoders['event_type'].transform(df['event_type'])
        df['priority_encoded'] = self.encoders['priority'].transform(df['priority'])

        numeric_features = ['start_hour', 'duration', 'weekday', 'days_to_deadline']
        df[numeric_features] = self.scaler.transform(df[numeric_features])

        return df[['start_hour', 'duration', 'event_type_encoded',
                 'priority_encoded', 'weekday', 'days_to_deadline']]

    def predict_best_schedule(self, event_data, user_events=None):
        """Predice el mejor horario para un evento verificando disponibilidad"""
        if not self.is_loaded:
            raise ValueError("El modelo no está cargado. Verifica los archivos del modelo.")

        # Validar datos de entrada
        self.validate_event_data(event_data)

        # Procesar fecha de vencimiento
        due_date, days_to_deadline = self.process_due_date(
            event_data.get('due_date'), 
            event_data.get('start_date')
        )

        resultados = []
        for hora in range(6, 23):  # Horario extendido para estudiantes
            event_test = event_data.copy()
            event_test['start_hour'] = hora
            event_test['days_to_deadline'] = days_to_deadline

            # ✅ NUEVA FUNCIONALIDAD: Verificar disponibilidad de horario
            is_available = self._check_time_availability(
                hora, event_data.get('duration', 1), 
                event_data.get('start_date'), user_events
            )

            df_test = pd.DataFrame([event_test])
            X = self.transform_data(df_test)

            prob = self.model.predict_proba(X)[0][1]
            score = self._calculate_score(prob, hora, event_test)
            
            # ✅ PENALIZAR HORARIOS NO DISPONIBLES
            if not is_available:
                score *= 0.1  # Reducir drasticamente el score si hay conflicto

            resultados.append({
                'hora': hora,
                'probabilidad': prob,
                'score': score,
                'hora_formateada': f"{hora:02d}:00",
                'disponible': is_available  # ✅ NUEVO: Indicar disponibilidad
            })

        df_result = pd.DataFrame(resultados)
        mejor = df_result.loc[df_result['score'].idxmax()]

        return {
            'mejor_hora': int(mejor['hora']),
            'mejor_hora_formateada': mejor['hora_formateada'],
            'probabilidad': float(mejor['probabilidad']),
            'score': float(mejor['score']),
            'confianza': self._calculate_confidence(df_result),
            'disponible': bool(mejor['disponible']),  # ✅ NUEVO
            'todas_opciones': df_result.to_dict('records')
        }

    def _calculate_score(self, prob, hora, event):
        """Calcula el score mejorado con más factores"""
        score = prob

        # Factores de prioridad
        if event['priority'] == 'alta':
            score *= 1.3
        elif event['priority'] == 'baja':
            score *= 0.8

        # Factores de horario óptimo por tipo
        if event['event_type'] in ['estudio', 'tarea', 'proyecto']:
            if 9 <= hora <= 11 or 15 <= hora <= 17:  # Horas de mayor concentración
                score *= 1.3
            elif hora >= 20:
                score *= 0.7
        elif event['event_type'] == 'clase':
            if 8 <= hora <= 18:  # Horario académico normal
                score *= 1.1
        elif event['event_type'] in ['descanso', 'personal']:
            if hora >= 18 or hora <= 8:  # Horarios más relajados
                score *= 1.2

        # Factor de urgencia
        if event.get('days_to_deadline', 999) <= 1:
            score *= 1.4
        elif event.get('days_to_deadline', 999) <= 3:
            score *= 1.2

        return score

    def _calculate_confidence(self, df_result):
        """Calcula la confianza de la recomendación"""
        scores = df_result['score'].values
        max_score = scores.max()
        mean_score = scores.mean()
        
        # Confianza basada en qué tan destacada es la mejor opción
        confidence = min(1.0, (max_score - mean_score) / mean_score + 0.5)
        return float(confidence)

    def optimize_schedule(self, events_queryset, start_date, end_date):
        """
        Optimiza un conjunto de eventos del usuario.
        Compatible con QuerySet de Django.
        """
        if not self.is_loaded:
            raise ValueError("El modelo no está cargado. Verifica los archivos del modelo.")
        
        suggestions = []
        
        for event in events_queryset:
            try:
                # Convertir evento Django a formato del modelo
                event_data = {
                    'event_type': self._map_django_event_type(event.event_type),
                    'priority': self._map_django_priority(event.priority),
                    'duration': self._calculate_duration(event.start_time, event.end_time),
                    'weekday': event.start_time.weekday(),
                    'due_date': event.due_date,
                    'start_date': start_date
                }
                
                # Obtener predicción
                prediction = self.predict_best_schedule(event_data)
                
                # Crear horario sugerido
                current_date = event.start_time.date()
                suggested_datetime = datetime.combine(
                    current_date, 
                    datetime.min.time().replace(hour=prediction['mejor_hora'])
                )
                suggested_end_datetime = suggested_datetime + timedelta(hours=event_data['duration'])
                
                # Solo sugerir si es diferente al horario actual
                if suggested_datetime.hour != event.start_time.hour:
                    suggestions.append({
                        'event_id': event.id,
                        'title': event.title,
                        'current_time': event.start_time.isoformat(),
                        'suggested_time': suggested_datetime.isoformat(),
                        'suggested_end_time': suggested_end_datetime.isoformat(),
                        'improvement_score': round((prediction['score'] - 0.5) * 100, 1),
                        'confianza': prediction['confianza'],
                        'mejor_hora': prediction['mejor_hora'],
                        'todas_opciones': prediction['todas_opciones'],
                        'reason': self._generate_reason(event_data, prediction)
                    })
                    
            except Exception as e:
                print(f"Error procesando evento {event.id}: {str(e)}")
                continue
        
        return suggestions

    def _map_django_event_type(self, django_type):
        """Mapea tipos de eventos de Django a tipos del modelo"""
        mapping = {
            'task': 'tarea',
            'class': 'clase', 
            'exam': 'examen',
            'project': 'proyecto',
            'study': 'estudio',
            'break': 'descanso',
            'personal': 'personal',
            'other': 'otro'
        }
        return mapping.get(django_type, 'otro')

    def _map_django_priority(self, django_priority):
        """Mapea prioridades de Django a prioridades del modelo"""
        mapping = {
            'high': 'alta',
            'medium': 'media',
            'low': 'baja'
        }
        return mapping.get(django_priority, 'media')

    def _calculate_duration(self, start_time, end_time):
        """Calcula la duración en horas"""
        duration = (end_time - start_time).total_seconds() / 3600
        return round(duration, 1)

    def _generate_reason(self, event_data, prediction):
        """Genera una razón explicativa para la sugerencia"""
        reasons = []
        
        if prediction['confianza'] > 0.8:
            reasons.append("Alta confianza en la predicción")
        
        if event_data['event_type'] in ['estudio', 'tarea']:
            if 9 <= prediction['mejor_hora'] <= 11:
                reasons.append("Horario óptimo para concentración matutina")
            elif 15 <= prediction['mejor_hora'] <= 17:
                reasons.append("Horario ideal para productividad vespertina")
        
        if event_data['priority'] == 'alta':
            reasons.append("Prioridad alta requiere horario premium")
        
        if event_data.get('days_to_deadline', 999) <= 3:
            reasons.append("Proximidad del deadline sugiere este horario")
        
        # ✅ NUEVO: Agregar razón de disponibilidad
        if prediction.get('disponible', True):
            reasons.append("Horario disponible sin conflictos")
        
        return ". ".join(reasons) if reasons else "Optimización basada en patrones de productividad"

    def _check_time_availability(self, hora, duration, start_date, user_events):
        """
        Verifica si un horario está disponible revisando conflictos con eventos existentes.
        
        Args:
            hora (int): Hora del día a verificar (0-23)
            duration (float): Duración del evento en horas
            start_date (datetime.date): Fecha del evento
            user_events (QuerySet): Eventos existentes del usuario
        
        Returns:
            bool: True si el horario está disponible, False si hay conflicto
        """
        if not user_events:
            return True
            
        # Importar timezone aquí para evitar problemas de importación circular
        from django.utils import timezone
            
        # Crear datetime para el horario a verificar
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        elif isinstance(start_date, datetime):
            start_date = start_date.date()
            
        proposed_start = datetime.combine(start_date, datetime.min.time().replace(hour=hora))
        proposed_end = proposed_start + timedelta(hours=duration)
        
        # Hacer timezone-aware si es necesario
        if timezone.is_aware(user_events[0].start_time if user_events else None):
            proposed_start = timezone.make_aware(proposed_start)
            proposed_end = timezone.make_aware(proposed_end)
        
        # Verificar conflictos
        for event in user_events:
            # Si el evento propuesto empieza durante otro evento
            if (event.start_time <= proposed_start < event.end_time):
                return False
                
            # Si el evento propuesto termina durante otro evento
            if (event.start_time < proposed_end <= event.end_time):
                return False
                
            # Si el evento propuesto contiene completamente a otro evento
            if (proposed_start <= event.start_time and proposed_end >= event.end_time):
                return False
        
        return True
